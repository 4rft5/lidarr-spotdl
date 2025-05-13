FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y cron && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN spotdl --download-ffmpeg

COPY . /app

COPY run_spotdl.sh /app/run_spotdl.sh
RUN chmod +x /app/run_spotdl.sh

COPY init.sh /app/init.sh
RUN chmod +x /app/init.sh

CMD ["/app/init.sh"]