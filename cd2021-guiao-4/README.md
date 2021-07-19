# Load Balancer

Very simples HTTP/TCP Load Balancer.
Implemented in Python3, single thread, using OS selector.
The code contains 4 classes that implement different strategies to select the next back-end server:

1. **N to 1:** all the requests are routed to a single server
2. **Round Robin:** the requests are routed to all servers in sequence
3. **Least Connections:** the request is routed to the server with fewer processed connections
4. **Least Response Time:** the request is routed to the server with less average execution time

At the moment only the fist strategy is fully implemented.

## Back-end server

The back-end server was implemented with [flask](http://flask.pocoo.org/).
It provides a simple service that computes the number Pi with a certain precision.

## Prerequisites

```console
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```

## How to run

```console
$ source venv/bin/activate
$ ./setup.sh
```

In another terminal
```console
$ curl -s http://localhost:8080/10
```

Or use a browser to open
```console
http://localhost:8080/10
```


## How to access the load balancer

Go to a browser and open this [link](http://localhost:8080/100).
The number after the URL specifies the precision of the computation.

## How to Stress Test

```console
$ ./stress_test.sh
```

Alternative
```console
$ httperf --server=localhost --port=8080 --uri=/100 --num-conns=100 --rate=5
```

## Git Upstream

```console
$ git remote add upstream git@github.com:detiuaveiro/load-balancer.git
$ git fetch upstream
$ git checkout master
$ git merge upstream/master
```

## Authors

* **Mário Antunes** - [mariolpantunes](https://github.com/mariolpantunes)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
