FROM python:3.9-slim

ENV TOKEN=abc
ENV VPN_CONFIGPATH=abc

WORKDIR /app

# Instala las dependencias necesarias
RUN apt-get update && apt-get install -y openvpn && apt-get install -y procps 

COPY main.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]