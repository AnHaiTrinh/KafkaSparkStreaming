FROM bde2020/spark-submit:3.3.0-hadoop3.3

COPY template.sh /
COPY submit.sh /

# Copy the requirements.txt first, for separate dependency resolving and downloading
COPY requirements.txt /app/
RUN cd /app && pip3 install -r requirements.txt

# Copy the source code
COPY streaming.py /app

ENV SPARK_APPLICATION_PYTHON_LOCATION=/app/streaming.py
ENV SPARK_SUBMIT_ARGS="--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0"
EXPOSE 4040

CMD ["/bin/bash", "/template.sh"]