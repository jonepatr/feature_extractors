FROM python:3.7
RUN apt-get update
RUN apt-get install -y libsndfile1
WORKDIR /workspace
COPY . .
RUN pip install -r requirements.txt