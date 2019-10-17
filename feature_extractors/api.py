import json
import logging
import os
import re

import docker

from tqdm import tqdm

logger = logging.getLogger(__name__)


def extract(
    extractor: str = None,
    action: str = None,
    input_: str = None,
    output: str = None,
    rest_args: str = None,
    gpus: str = None,
    cpus: str = None,
    disable_progress_bar: bool = False,
):
    assert extractor
    if not input_:
        input_ = ""
    if not output:
        output = ""

    tag = f"feature_extractors_{extractor}"
    client = docker.from_env()
    try:
        client.images.get(tag)
    except docker.errors.ImageNotFound:
        _build_image(extractor, tag, disable_progress_bar)

    try:
        out = client.containers.run(
            tag,
            command=_build_command(action, input_, output, rest_args),
            volumes=_prepare_volumes(input_, output),
            **_prepare_cpu_and_gpu_options(cpus, gpus),
            remove=True,
            stream=True,
        )
        for line in out:
            print(line.decode("utf-8").strip())

    except docker.errors.ContainerError as e:
        logger.debug("image used: %s", e.image)
        logger.debug("command used: %s", e.command)
        print(e.stderr.decode("utf-8"))


def _prepare_volumes(input_, output):
    volumes = {}
    input_path = None
    output_path = os.path.dirname(os.path.abspath(output))

    if input_ and os.path.exists(input_):
        input_path = os.path.dirname(os.path.abspath(input_))
        if input_path == output_path:
            mode = "rw"
        else:
            mode = "ro"
        volumes[input_path] = {
            "bind": "/input",
            "mode": mode,
        }

    if output and input_path != output_path:
        volumes[output_path] = {
            "bind": "/output",
            "mode": "rw",
        }
    return volumes


def _build_command(action, input_, output, rest_args):
    input_arg = ""
    output_arg = ""
    input_path = None
    output_path = os.path.dirname(os.path.abspath(output))

    if not action:
        action = ""

    if input_:
        if os.path.exists(input_):
            input_path = os.path.dirname(os.path.abspath(input_))
            input_arg = os.path.join("/input", os.path.basename(input_))
        else:
            input_arg = input_

    if output:
        if input_path == output_path:
            path = "/input"
        else:
            path = "/output"
        output_arg = os.path.join(path, os.path.basename(output))

    if not rest_args:
        rest_args = ""

    command = f"python extract.py {action} {input_arg} {output_arg} {rest_args}"
    logger.debug("command: %s", command)
    return command


def _prepare_cpu_and_gpu_options(cpus, gpus):
    options = {}
    if gpus:
        options["runtime"] = "nvidia"
        options["environment"] = {"CUDA_VISIBLE_DEVICES": gpus}

    if cpus:
        options["cpuset_cpus"] = cpus

    return options


def _build_image(extractor, tag, disable_progress_bar):
    logger.info("building image..")
    extractor_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, "extractors", extractor)
    )

    logger.debug(extractor_dir)
    pbar = None
    prev_number = 0
    client = docker.from_env()
    try:
        for lines in client.api.build(path=extractor_dir, tag=tag):
            split_lines = lines.decode("utf-8").split("\r\n")
            for line in split_lines:
                if not line:
                    continue
                json_line = json.loads(line)
                if "stream" in json_line:
                    real_line = json_line["stream"].strip()
                    numbers = re.search(r"Step (\d+)/(\d+)", real_line)
                    if numbers:
                        if not pbar and not disable_progress_bar:
                            pbar = tqdm(total=int(numbers.group(2)))
                        if pbar and int(numbers.group(1)) != prev_number:
                            pbar.update(1)
                    logger.debug(real_line)
                elif "error" in json_line:
                    logger.error(json_line)
                    exit()
    except docker.errors.BuildError as e:
        build_log = e.build_log
        print("".join([x["stream"] for x in build_log if "stream" in x]))
        exit()
    finally:
        if pbar:
            pbar.close()
    logger.debug("done building image")
