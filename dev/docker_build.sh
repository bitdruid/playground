#!/bin/bash

if [ ! -f .env ]; then
    touch .env
fi

#docker build -t osintbot .
docker buildx build --platform linux/amd64,linux/arm64 -t osintbot .
docker run -p 5050:5000 --hostname osintbot --env-file .env --rm osintbot
