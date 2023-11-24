FROM bde2020/spark-submit:3.3.0-hadoop3.3

WORKDIR /app

COPY template.sh /
COPY submit.sh /

# Copy the requirements.txt first, for separate dependency resolving and downloading
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy the source code
COPY streaming.py .

ENV SPARK_APPLICATION_PYTHON_LOCATION=/app/streaming.py
ENV SPARK_SUBMIT_ARGS="--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0"
EXPOSE 4040

CMD ["/bin/bash", "/template.sh"]