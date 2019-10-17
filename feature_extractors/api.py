import docker
import os
import json
import logging

logger = logging.getLogger(__name__)

def extract(
    extractor: str=None,
    action: str=None,
    input_: str=None,
    output: str=None,
    rest_args: str=None,
    gpus: str=None,
    cpus: str=None
):
    assert extractor
    if not action:
        action = ""

    if not input_:
        input_ = ""

    if not output:
        output = ""
    
    if not rest_args:
        rest_args = ""



    client = docker.from_env()
    tag = f"feature_extractors_{extractor}"
    try:
        client.images.get(tag)
    except docker.errors.ImageNotFound:
        logger.info("building image..")
        extractor_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.pardir, "extractors", extractor)
        )

        logger.debug(extractor_dir)
        try:
            for lines in client.api.build(path=extractor_dir, tag=tag):
                split_lines = lines.decode("utf-8").split("\r\n")
                for line in split_lines:
                    if line:
                        json_line = json.loads(line)
                        if "stream" in json_line:
                            logger.info(json_line["stream"].strip())
                        elif "error" in json_line:
                            logger.error(json_line)
                            exit()
        except docker.errors.BuildError as e:
            build_log = e.build_log
            print("".join([x["stream"] for x in build_log if "stream" in x]))
            exit()
        logger.info("done building image")

    volumes = {}
    input_arg = ""
    output_arg = ""

    if output:
        volumes[os.path.dirname(os.path.abspath(output))] = {
            "bind": "/output",
            "mode": "rw",
        }
        output_arg = os.path.join("/output", os.path.basename(output))

    if input_:
        if os.path.exists(input_):
            volumes[os.path.dirname(os.path.abspath(input_))] = {
                "bind": "/input",
                "mode": "ro",
            }
            input_arg = os.path.join("/input", os.path.basename(input_))
        else:
            input_arg = input_

    command = f"python extract.py {action} {input_arg} {output_arg} {rest_args}"

    gpu_options, cpu_options = {}, {}
    if gpus:
        gpu_options = {
            "runtime": "nvidia",
            "environment": {"CUDA_VISIBLE_DEVICES": gpus},
        }
    if cpus:
        cpu_options = {"cpuset_cpus": cpus}
    try:
        out = client.containers.run(
            tag,
            command=command,
            remove=True,
            **gpu_options,
            **cpu_options,
            volumes=volumes,
            stream=True,
        )
        for line in out:
            print(line.decode("utf-8").strip())

    except docker.errors.ContainerError as e:
        logger.debug("image used: %s", e.image)
        logger.debug("command used: %s", e.command)
        print(e.stderr.decode("utf-8"))
