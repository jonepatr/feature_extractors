import json
import os
from glob import glob

import click
import dlib


@click.group()
def cli():
    pass


@cli.command()
@click.argument("input_dir", type=click.Path(exists=True))
@click.argument("output_file")
@click.option("--cnn_weights_path", default="models/mmod_human_face_detector.dat")
@click.option(
    "--shape_predictor_path", default="models/shape_predictor_68_face_landmarks.dat"
)
@click.option("--resize_factor", default=0.25)
def extract_dlib(
    input_dir, output_file, cnn_weights_path, shape_predictor_path, resize_factor
):
    detector = dlib.cnn_face_detection_model_v1(cnn_weights_path)
    predictor = dlib.shape_predictor(shape_predictor_path)

    height = None
    width = None
    result = []

    image_files = sorted(glob(os.path.join(input_dir, "*")))
    total_count = len(image_files)

    for file_path in image_files:
        img = dlib.load_rgb_image(file_path)

        if not height or not width:
            height, width = img.shape[:2]
        resized_img = dlib.resize_image(img, resize_factor)

        faces = detector(img, 0)
        sub_result = []
        for f in faces:
            shape = predictor(resized_img, f.rect)
            sub_sub_result = []
            for part in shape.parts():
                sub_sub_result += [part.x, part.y]
            sub_result.append(sub_sub_result)
        result.append(sub_result)

    data = {
        "video_width": width,
        "video_height": height,
        "frame_count": total_count,
        "frames": result,
    }

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(data, f)


if __name__ == "__main__":
    cli()
