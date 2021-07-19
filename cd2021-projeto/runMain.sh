#!/bin/bash

docker stop server
docker rm server
echo ".... Server running ...."
docker run --name server diogogomes/cd2021
sleep 1
docker logs server