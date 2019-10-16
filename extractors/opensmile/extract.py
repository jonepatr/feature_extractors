import os
import shutil
import subprocess
import tempfile

import click


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file")
@click.argument("config")
@click.option("--opensmile_bin", default="SMILExtract")
def extract_opensmile(input_file, output_file, config, opensmile_bin):
    extension = os.path.splitext(output_file)[1]
    with tempfile.NamedTemporaryFile(suffix=extension) as tmpf:

        subprocess.check_call(
            [opensmile_bin, "-C", config, "-I", input_file, "-O", tmpf.name]
        )

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        shutil.copy(tmpf.name, output_file)


if __name__ == "__main__":
    extract_opensmile()
