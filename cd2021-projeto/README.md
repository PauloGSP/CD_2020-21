# How to execute

Run the server in your host (not inside any container)

$ python3 main.py

Launch containers with 1 worker each (this is your code)

When you successfully guess the password, the worker will receive an image file.

# Using Docker

## Build your docker container 

$ docker build --tag projecto_final .

## Launching containers

$ docker run -d --name worker1 projecto_final

## Monitor your containers

$ docker ps -a

## Stop your container

$ docker stop <container id>

## Remove old containers

$ docker rm <container id>

# Tips for install in Ubuntu:

$ sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev python3-openssl
