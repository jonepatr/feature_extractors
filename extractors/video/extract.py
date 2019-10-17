import os
import shutil
import tempfile
from pathlib import Path

import click
import cv2


@click.group()
def cli():
    pass


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_dir")
@click.option("--file_extension", default="jpg")
def extract_images(input_file, output_dir, file_extension):
    cap = cv2.VideoCapture(input_file)

    count = 0
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    with tempfile.TemporaryDirectory() as td:
        while cap.isOpened():
            ret, img = cap.read()
            if ret != True:
                break
            img_path = str(count).zfill(len(str(length)))
            cv2.imwrite(os.path.join(td, f"{img_path}.{file_extension}"), img)

            count += 1

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        for f in os.listdir(td):
            shutil.move(os.path.join(td, f), output_dir)


if __name__ == "__main__":
    cli()
