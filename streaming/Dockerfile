FROM bde2020/spark-submit:3.3.0-hadoop3.3

WORKDIR /app

COPY template.sh /
COPY submit.sh /

RUN apk update && apk add --no-cache curl
RUN curl -o postgresql-driver.jar https://jdbc.postgresql.org/download/postgresql-42.7.1.jar

# Copy the requirements.txt first, for separate dependency resolving and downloading
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy the source code
COPY streaming.py .

ENV SPARK_APPLICATION_PYTHON_LOCATION=/app/streaming.py
ENV SPARK_SUBMIT_ARGS="--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0 --driver-class-path postgresql-driver.jar --jars postgresql-driver.jar"
EXPOSE 4040

CMD ["/bin/bash", "/template.sh"]