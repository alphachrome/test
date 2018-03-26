#!/usr/local/conda2/bin/python
from flask import Flask, request

app = Flask(__name__)

@app.route('/sys/class')
def sysvar_read():
    with open('/sys/class/'+request.args.get('var'),'r') as fd:
        return fd.readline().rstrip()

app.run(debug=True, port=9000)