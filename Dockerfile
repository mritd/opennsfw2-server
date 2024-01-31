FROM python:3.9-slim

ENV TZ Asia/Shanghai
ENV OPENNSFW2_HOME /data

WORKDIR /app

COPY server.py requirements.txt /app

RUN set -ex \
    && apt update \
    && apt install cmake libglib2.0-0 libhdf5-dev libgl1-mesa-glx tzdata -y \
    && ln -sf /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo ${TZ} > /etc/timezone \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*

VOLUME /data

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "server:app"]
