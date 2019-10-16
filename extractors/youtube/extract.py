import csv
import html
import json
import os
import shutil
import subprocess
import tempfile

import click
import requests

from bs4 import BeautifulSoup
from pytube import YouTube


@click.group()
def cli():
    pass


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file")
@click.option("--fps", default=30)
@click.option("--ffmpeg_bin", default="ffmpeg")
@click.option("--ffprobe_bin", default="ffprobe")
def process_youtube_video(input_file, output_file, fps, ffmpeg_bin, ffprobe_bin):
    with tempfile.NamedTemporaryFile(suffix=".mp4") as tmpf:
        current_fps = eval(
            subprocess.check_output(
                [
                    ffprobe_bin,
                    "-v",
                    "0",
                    "-of",
                    "csv=p=0",
                    "-select_streams",
                    "v:0",
                    "-show_entries",
                    "stream=r_frame_rate",
                    input_file,
                ]
            )
        )

        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        if current_fps != fps:
            subprocess.check_call(
                [
                    *ffmpeg_bin.split(" "),
                    "-hide_banner",
                    "-loglevel",
                    "panic",
                    "-y",
                    "-i",
                    input_file,
                    "-r",
                    str(fps),
                    tmpf.name,
                ]
            )
            shutil.copy(tmpf.name, output_file)
        else:
            shutil.copy(input_file, output_file)


@cli.command()
@click.argument("yt_video_id")
@click.argument("output_file")
@click.option("--caption_type", default="asr")
def download_youtube_captions(yt_video_id, output_file, caption_type):
    yt = YouTube("https://youtu.be/" + yt_video_id)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    for caption_url in [x.url for x in yt.captions.all() if x.code == "en"]:
        if ("kind=asr" in caption_url) is (caption_type == "asr"):
            page = requests.get(caption_url + "&fmt=srv2")
            sentences = []
            for w in BeautifulSoup(page.content, "lxml").findAll("text"):
                word = w.text
                if word.startswith("\n"):
                    continue
                elif word.startswith("<font"):
                    word = word.split(">")[1]
                    word = word.replace("</font", "")
                sentences.append([html.unescape(word), w.get("t"), w.get("d")])

            with open(output_file, "w") as f:
                csv.writer(f).writerows(sentences)


@cli.command()
@click.argument("yt_video_id")
@click.argument("output_file")
@click.option("--file_type", type=click.Choice(["audio", "video"]), required=True)
def youtube_downloader(yt_video_id, output_file, file_type):

    yt = YouTube("https://youtu.be/" + yt_video_id)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    media_stream = (
        yt.streams.filter(mime_type=f"{file_type}/mp4")
        .order_by("resolution")
        .desc()
        .first()
    )

    with tempfile.TemporaryDirectory() as tmpd:
        tmp_path = media_stream.download(output_path=tmpd)
        shutil.copy(tmp_path, output_file)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file")
@click.option("--fs", default=44100)
@click.option("--ffmpeg_bin", default="ffmpeg")
def process_youtube_audio(input_file, output_file, fs, ffmpeg_bin):

    with tempfile.NamedTemporaryFile(suffix=".wav") as tmpf:
        subprocess.check_call(
            [
                ffmpeg_bin,
                "-y",
                "-hide_banner",
                "-loglevel",
                "panic",
                "-i",
                input_file,
                "-vn",
                "-ar",
                str(fs),
                tmpf.name,
            ]
        )

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        shutil.copy(tmpf.name, output_file)


if __name__ == "__main__":
    cli()
