FROM ghcr.io/isaric/python-opencv-docker:python-3.10-opencv-4.8.0-arm64

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5000

CMD [ "python3", "-m" , "flask", "--app", "main", "run", "--host=0.0.0.0"]
