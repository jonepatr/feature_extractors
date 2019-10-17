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

extract(
    extractor="audio",
    action="extract-mfcc",
    input_="/path/to/my/file.wav",
    output="/here/I/want/it/to/go.npy",
    rest_args="--n_mfcc 80"
)
```

### Command line
`feature_extractor [extractor]`

Each extractor then in turn takes an `[action]` (e.g. extract-mfcc) `[input]` (typically a file), an `[output]` (a file or directory depending on the extractor) and furhter options. The system builds a docker image for each extractor type and assigns it a tag on the format `feature_extractors_[extractor]`, this might sometimes take a long while. This is only done the first time an etractor is used. 

An example:
`feature_extractor audio extract-mfcc /path/to/my/file.wav /here/I/want/it/to/go.npy --n_mfcc 80`

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
