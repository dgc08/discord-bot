FROM python:slim

VOLUME /bot
WORKDIR /bot

ADD . /bot

CMD ["bash"]

RUN apt update
RUN yes | apt install ffmpeg

RUN python3 -m pip install -r requirements.txt

CMD ["python3", "main.py"]
