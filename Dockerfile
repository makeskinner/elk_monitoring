FROM logstash:8.11.3

USER root

# Install Python and Pip
RUN apt-get update && apt-get install -y python3 python3-pip

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY logstash.conf ./
COPY poller.py ./

EXPOSE 50000

CMD ["python3", "./poller.py"]
