import json
import logging
import os
import re

import docker
from tqdm import tqdm

logger = logging.getLogger(__name__)


def extract(
    extractor: str = None,
    command_args: list = None,
    volumes: dict = None,
    gpus: str = None,
    cpus: str = None,
    disable_progress_bar: bool = False,
):
    assert extractor

    logger.debug(
        f"""
        extractor: {extractor}
        command_args: {command_args}
        volumes: {volumes}
        gpus: {gpus}
        cpus: {cpus}
        disable_progress_bar: {disable_progress_bar}
        """
    )
    tag = f"feature_extractors_{extractor}"
    client = docker.from_env()
    try:
        client.images.get(tag)
    except docker.errors.ImageNotFound:
        _build_image(extractor, tag, disable_progress_bar)

    args = " ".join(command_args)

    command = f"python extract.py {args}"
    logger.debug("command: %s", command)

    final_volumes = {}
    if volumes:
        for host_path, machine_path in volumes.items():
            final_volumes[host_path] = {"bind": machine_path, "mode": "rw"}

    try:
        out = client.containers.run(
            tag,
            command=command,
            volumes=final_volumes,
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
