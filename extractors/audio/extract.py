import os

import click
import numpy as np

import librosa


@click.group()
def cli():
    pass


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file")
@click.option("--n_frames")
@click.option("--n_ac_coefficients", default=32)
@click.option("--sampling_rate", default=16000)
@click.option("--frame_length", required=True, type=int)
@click.option("--hop_length", required=True, type=int)
@click.option("--normalize_audio", type=bool)
def extract_autocorrelation(
    input_file,
    output_file,
    n_frames,
    n_ac_coefficients,
    sampling_rate,
    frame_length,
    hop_length,
    normalize_audio,
):
    y, sr = librosa.core.load(input_file, sr=sampling_rate, mono=True)

    if normalize_audio:
        y /= np.abs(np.max(y))

    chunked_y = librosa.util.frame(y, frame_length=frame_length, hop_length=hop_length)

    chunked_y = np.hanning(frame_length)[:, None] * chunked_y

    autocorrelation_coef = librosa.core.autocorrelate(chunked_y, axis=0)[
        :n_ac_coefficients
    ]

    first_element = autocorrelation_coef[:1]
    autocorr = np.divide(
        autocorrelation_coef,
        first_element,
        out=np.zeros_like(autocorrelation_coef),
        where=first_element != 0,
    )
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    np.save(output_file, autocorr.T)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file")
@click.option("--sampling_rate")
@click.option("--n_fft", required=True, type=int)
@click.option("--n_mels", default=64)
@click.option("--hop_length", required=True, type=int)
@click.option("--normalize_audio")
def extract_spectrogram(
    input_file, output_file, sampling_rate, n_fft, n_mels, hop_length, normalize_audio
):
    y, _ = librosa.core.load(input_file, sr=sampling_rate, mono=True)

    if normalize_audio:
        y /= np.abs(np.max(y))

    spectrogram = np.abs(
        librosa.stft(
            y=y, n_fft=n_fft, hop_length=hop_length, center=False, window="hann"
        )
        ** 2
    )

    melspectrogram = librosa.feature.melspectrogram(S=spectrogram, n_mels=n_mels)
    melspectrogram = librosa.core.power_to_db(melspectrogram).T

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    np.save(output_file, melspectrogram)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file")
@click.option("--n_mfcc")
def extract_mfcc(input_file, output_file, n_mfcc):
    melspectrogram = np.load(input_file)
    mfcc = librosa.feature.mfcc(S=melspectrogram.T, n_mfcc=n_mfcc).T

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    np.save(output_file, mfcc)


if __name__ == "__main__":
    cli()
