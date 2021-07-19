#!/bin/bash

docker build --tag projecto_final .
worker="worker""$1"
docker run --name $worker projecto_final
sleep 1
docker logs $worker