FROM python:3
RUN apt-get update
RUN apt-get install -y cmake
WORKDIR /workspace
COPY . . 
ADD http://arunponnusamy.com/files/mmod_human_face_detector.dat models/mmod_human_face_detector.dat
RUN curl http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2 --output shape_predictor_68_face_landmarks.dat.bz2
RUN bunzip2 shape_predictor_68_face_landmarks.dat.bz2 && mv shape_predictor_68_face_landmarks.dat models/shape_predictor_68_face_landmarks.dat
RUN pip install -r requirements.txt