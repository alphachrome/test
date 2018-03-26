#!/usr/local/conda2/bin/python
#
# Example using browser: localhost:9000/sys/class/power_supply/BAT0/capacity

from flask import Flask, request

app = Flask(__name__)

@app.route('/sys/<path:filename>')
def sysvar_read(filename):
    with open('/sys/'+filename,'r') as fd:
        return fd.readline().rstrip()

app.run(debug=True, port=9000)
