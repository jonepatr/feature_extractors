import os
import shutil
import subprocess
import tempfile
from pathlib import Path
import click


@click.group()
def cli():
    pass


@cli.command()
@click.option("-i", "input_file", required=True, help="Input file")
@click.option("-o", "output_dir", required=True, help="Output directory")
@click.option(
    "--openface_args", default="-tracked -2Dfp -3Dfp -pdmparams -pose -aus -gaze"
)
@click.option("--openface_bin", default="FeatureExtraction")
def extract_openface(input_file, output_dir, openface_args, openface_bin):
    with tempfile.TemporaryDirectory() as td:
        subprocess.check_call(
            [openface_bin, "-f", input_file, "-out_dir", td, openface_args, "-q"]
        )
        input_path = Path(input_file)
        csv_file_name = os.path.join(td, input_path.with_suffix(".csv").name)
        video_file_name = os.path.join(td, input_path.with_suffix(".avi").name)

        os.makedirs(output_dir, exist_ok=True)

        output_csv = os.path.join(output_dir, input_path.with_suffix(".csv").name)
        output_avi = os.path.join(output_dir, input_path.with_suffix(".avi").name)

        if os.path.exists(video_file_name):
            shutil.copy(video_file_name, output_avi)

        if os.path.exists(csv_file_name):
            with open(output_csv, "w") as outfile:
                subprocess.check_call(
                    ["sed", "s/, /,/g", csv_file_name], stdout=outfile
                )


if __name__ == "__main__":
    cli()
