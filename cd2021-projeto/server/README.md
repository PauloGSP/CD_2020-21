# Launching the Server as a container:

```
$ docker pull diogogomes/cd2021:0.1
$ docker run -d --name server diogogomes/cd2021:0.1
```

# Finding the address of the server:

```
$ docker logs server
