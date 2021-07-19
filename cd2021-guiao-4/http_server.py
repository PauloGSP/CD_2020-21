# coding: utf-8

import argparse
from threading import Lock
from utils import leibniz_pi_precision
from flask import Flask
from flask import render_template


app = Flask(__name__)
lock = Lock() 


@app.route("/<int:precision>")
def index(precision):
    with lock:
        calc = {'precision': precision, 'pi': leibniz_pi_precision(precision)}
        return render_template('index.html', calc=calc)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Pi HTTP server')
    parser.add_argument('-p', dest='port', type=int, help='HTTP port', default=5000)
    args = parser.parse_args()
    app.run(port=args.port, threaded=False)