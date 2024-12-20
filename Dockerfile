FROM python:3.13-slim-bullseye

USER root

# Runtime dependency
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    exiftool \
    # dumb-init \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Default USERID and GROUPID
ARG USERID=10000
ARG GROUPID=10000

USER $USERID:$GROUPID

WORKDIR /app
COPY server.py .

# CMD ["dumb-init", "python", "server.py"]
CMD ["python", "server.py"]