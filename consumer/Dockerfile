FROM python:3.9-slim-buster

WORKDIR /app

COPY consumer.py /app

RUN pip3 install confluent-kafka

CMD ["python3", "consumer.py"]