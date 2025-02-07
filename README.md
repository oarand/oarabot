# oarabot

Librería: python-telegram-bot https://docs.python-telegram-bot.org/en/v21.10/




# Build
```
docker build -t oarabot .
```

# Run 
```
docker run --net host --name oarabot -e TOKEN=XXX -e VPN_CONFIGPATH=/etc/openvpn/surf-shark -v /etc/openvpn:/etc/openvpn --restart always -t --privileged oarabot:latest
```

# Run (Docker compose)

See [docker-compose](./docker-compose.yml)