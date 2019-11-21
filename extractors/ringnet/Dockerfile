FROM nvidia/cuda:9.0-cudnn7-runtime-ubuntu16.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -y python python-pip build-essential autoconf libtool pkg-config python-dev git libboost-all-dev libsm6 libxext6 libxrender-dev python-tk python-opengl python-virtualenv vim ffmpeg

RUN pip install --upgrade pip
RUN pip install numpy
RUN pip install scipy
RUN pip install opendr==0.77
RUN pip install matplotlib==2.2.3
RUN pip install scikit-image==0.10.1
RUN pip install chumpy
RUN pip install opencv-python
RUN pip install absl-py
RUN pip install tensorflow-gpu==1.12.0
RUN pip install ipdb
RUN pip install PyOpenGL==3.1.0
RUN pip install pillow
RUN pip install pyrender
RUN pip install trimesh
RUN pip install tqdm

RUN git clone https://github.com/MPI-IS/mesh.git
RUN cd mesh && make && make install

WORKDIR /workspace
RUN git clone https://github.com/soubhiksanyal/RingNet.git

COPY . .
RUN pip install -r requirements.txt

