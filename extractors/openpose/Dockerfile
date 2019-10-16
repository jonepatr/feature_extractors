FROM nvidia/cuda:10.0-cudnn7-devel-ubuntu16.04

#python3-setuptools \
#python3-dev \
#python3-pip \

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ARG DEBIAN_FRONTEND=noninteractive

RUN echo "Installing dependencies..." && \
	apt-get -y --no-install-recommends update && \
	apt-get -y --no-install-recommends upgrade && \
	apt-get install -y --no-install-recommends software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get -y --no-install-recommends update && \
    apt-get install -y --no-install-recommends \
	build-essential \
	cmake \
	git \
	libatlas-base-dev \
	libprotobuf-dev \
	libleveldb-dev \
	libsnappy-dev \
	libhdf5-serial-dev \
	protobuf-compiler \
	libboost-all-dev \
	libgflags-dev \
	libgoogle-glog-dev \
	liblmdb-dev \
	pciutils \
    python3.6 \
    curl \
	opencl-headers \
	ocl-icd-opencl-dev \
	libviennacl-dev \
	libcanberra-gtk-module \
	libopencv-dev && \
	curl https://bootstrap.pypa.io/get-pip.py | python3.6 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.6 1 && \
    pip install \
	numpy \
	protobuf \
	opencv-python
ARG CUDA_ARCH_PTX='75'
ARG CUDA_ARCH_BIN='75'
RUN echo "Downloading and building OpenPose..." && \
	git clone https://github.com/CMU-Perceptual-Computing-Lab/openpose.git
RUN mkdir -p /openpose/build && \
	cd /openpose/build && \
	cmake .. -DCUDA_ARCH=Manual -DCUDA_ARCH_PTX='75' -DCUDA_ARCH_BIN='75' && \
	CUDA_ARCH_PTX=75 CUDA_ARCHBIN=75 make -j`nproc`


WORKDIR /workspace
COPY . .
RUN pip install -r requirements.txt

ENTRYPOINT []