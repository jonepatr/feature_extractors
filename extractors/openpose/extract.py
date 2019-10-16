import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import click


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_dir")
@click.option("--openpose_args", default="-face")
@click.option(
    "--openpose_bin", default="/openpose/build/examples/openpose/openpose.bin"
)
def extract_openpose(input_file, output_dir, openpose_args, openpose_bin):
    with tempfile.TemporaryDirectory() as td:

        input_file_name = os.path.basename(input_file)
        input_file_avi = os.path.splitext(input_file_name)[0] + ".avi"

        subprocess.check_call(
            [
                openpose_bin,
                "-video",
                input_file,
                "-write_json",
                os.path.join(td, "frames"),
                "--write_video",
                os.path.join(td, input_file_avi),
                "-display",
                "0",
                "-render_pose",
                "1",
                openpose_args,
            ]
        )

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        for f in os.listdir(td):
            shutil.move(os.path.join(td, f), output_dir)


if __name__ == "__main__":
    extract_openpose()
