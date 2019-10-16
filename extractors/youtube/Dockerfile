FROM python:3
RUN apt-get update
RUN apt-get install -y ffmpeg
WORKDIR /workspace
COPY . .
RUN pip install -r requirements.txt