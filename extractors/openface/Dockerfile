FROM algebr/openface

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get install -y python3.6 curl
RUN curl https://bootstrap.pypa.io/get-pip.py | python3.6
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 1

WORKDIR /workspace
COPY . .
RUN pip install -r requirements.txt
ENV PATH="/home/openface-build/build/bin:${PATH}"
RUN cp -r /home/openface-build/build/bin/model model
RUN cp -r /home/openface-build/build/bin/AU_predictors AU_predictors
ENTRYPOINT []