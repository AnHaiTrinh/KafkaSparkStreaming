FROM python:3.9-slim-buster

WORKDIR /app

COPY consumer.py /app

RUN pip3 install confluent-kafka

ENTRYPOINT ["python3", "consumer.py"]