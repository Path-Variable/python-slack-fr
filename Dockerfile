FROM ghcr.io/isaric/docker-dlib:python-opencv-4.8.0-dlib-19.24

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5000

CMD [ "python3", "-m" , "flask", "--app", "main", "run", "--host=0.0.0.0"]
