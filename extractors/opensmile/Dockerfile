FROM ubuntu:16.04

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt-get update
RUN apt-get install -y software-properties-common git automake build-essential libtool curl
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get install -y python3.6
RUN curl https://bootstrap.pypa.io/get-pip.py | python3.6
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 1
RUN git clone https://github.com/naxingyu/opensmile
RUN cd opensmile && ./buildStandalone.sh

WORKDIR /workspace
COPY . .
RUN pip install -r requirements.txt

ENV PATH="/opensmile/inst/bin:${PATH}"
