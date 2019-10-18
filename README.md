# Feature Extractors

## Installation
`pip install -e .`

### Dependencies
* A running instance of docker
* For some of the extrators nvidia-docker is needed

## Usage
One can either use the feature extractor from the command line or import it as a python library.

### As a library

Here is an example usage:
```
from feature_extractors.api import extract

def extract(
    extractor="audio",
    command_args=["extract-mfcc", "-i", "/mnt/path/to/my/file.wav", "-o", "/mnt/here/I/want/it/to/go.npy", "--n_mfcc", "80"],
    volumes={"/path/to/my/file.wav:/mnt/path/to/my/file.wav", "/here/I/want/it/to/":"/mnt/here/I/want/it/to/"}
)
```

### Command line
`feature_extractor [extractor]`

Each extractor then in turn takes an `[action]` (e.g. extract-mfcc), some sort of input, an output file or directory and some extra arguments specific to that extractor. The system builds a docker image for each extractor type and assigns it a tag on the format `feature_extractors_[extractor]`, this might sometimes take a long while. This is only done the first time an etractor is used. 
Using -v flags one can mount directories from the host into the docker container. This is done by passing one or several -v /path/on/host:/path/in/container flags. There is also a quick way of mounting a file which is preceeding the path with a `@`. This will mount for example `/path/to/myfile.csv` under the path `/mnt/path/to/myfile.csv` in the container. It also works with output files/directories that does not exist yet by mounting the parent path instead, i.e. if `/path/to/a/directory` exists and we want to mount an output directory `@/path/to/a/directory/new_directory` it will mount `/path/to/a/directory/` to `/mnt/path/to/a/directory/` in the container.


An example (using both ways of mounting):
`feature_extractor audio extract-mfcc -i /path/to/my/file.wav -o @/here/I/want/it/to/go.npy --n_mfcc 80 -v /hostpah/myfile.wav:/path/to/my/file.wav`

It is also possible to just build the extractors normally using docker and run them with `docker run`. The `feature_extractor` is simply doing that automatically.

### List of current Extractors
* audio
* dlib
* openface
* openpose (requires nvidia-docker and GPUS)
* opensmile
* ringnet (requires nvidia-docker and GPUS)
* video
* youtube
