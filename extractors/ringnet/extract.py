import os
import shutil

import click
import cv2
import numpy as np
import skimage.io as io
import tensorflow as tf

from backports import tempfile
from pathlib2 import Path
from RingNet.config_test import get_config
from RingNet.run_RingNet import RingNet_inference
from RingNet.util import image as img_util
from RingNet.util import renderer as vis_util


@click.group()
def cli():
    pass


def preprocess_image(img, img_size):
    if np.max(img.shape[:2]) != img_size:
        scale = float(img_size) / np.max(img.shape[:2])
    else:
        scale = 1.0
    center = np.round(np.array(img.shape[:2]) / 2).astype(int)
    center = center[::-1]
    crop, proc_param = img_util.scale_and_crop(img, scale, center, img_size)
    crop = 2 * ((crop / 255.0) - 0.5)
    return crop


def ringnet_from_image(img, config, model):
    input_img = preprocess_image(img, config.img_size)
    vertices, flame_parameters = model.predict(
        np.expand_dims(input_img, axis=0), get_parameters=True
    )
    return {
        "vertices": vertices,
        "cam": flame_parameters[0][:3],
        "pose": flame_parameters[0][3 : 3 + config.pose_params],
        "shape": flame_parameters[0][
            3 + config.pose_params : 3 + config.pose_params + config.shape_params
        ],
        "expression": flame_parameters[0][
            3 + config.pose_params + config.shape_params :
        ],
    }


def create_config(img_size, flame_model_path, model_path):
    config = get_config()
    config.img_size = img_size
    config.flame_model_path = str(flame_model_path)
    config.load_path = str(model_path)
    return config


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file")
@click.option("--model_path", default="/model/ring_6_68641")
@click.option("--flame_model_path", default="/flame_model/ch_models/generic_model.pkl")
@click.option("--img_size", default=224)
def extract_from_image(input_file, output_file, model_path, flame_model_path, img_size):
    config = create_config(img_size, flame_model_path, model_path)

    img = io.imread(input_file)
    sess = tf.Session()
    model = RingNet_inference(config, sess=sess)

    flame_parameters = ringnet_from_image(img, config, model)
    Path(output_file).parent.mkdir(exist_ok=True)
    np.save(output_file, flame_parameters)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_dir")
@click.option("--model_path", default="/model/ring_6_68641")
@click.option("--flame_model_path", default="/flame_model/ch_models/generic_model.pkl")
@click.option("--img_size", default=224)
def extract_from_video(input_file, output_dir, model_path, flame_model_path, img_size):
    config = create_config(img_size, flame_model_path, model_path)

    sess = tf.Session()
    model = RingNet_inference(config, sess=sess)
    i = 0
    cap = cv2.VideoCapture(input_file)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    with tempfile.TemporaryDirectory() as td:
        while cap.isOpened():
            ret, img = cap.read()
            if ret != True:
                break
            flame_parameters = ringnet_from_image(img, config, model)
            img_path = str(i).zfill(len(str(length)))

            np.save(os.path.join(td, img_path + ".npy"), flame_parameters)

            i += 1
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        for f in os.listdir(td):
            shutil.move(os.path.join(td, f), output_dir)
        cap.release()


if __name__ == "__main__":
    cli()
