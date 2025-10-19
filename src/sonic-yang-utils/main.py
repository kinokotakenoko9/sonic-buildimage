#!/usr/bin/env python3

from flask import Flask, render_template, jsonify
import os
import requests

app = Flask(__name__)

RESTCONF_USER = os.environ.get('RESTCONF_USER', 'chdpc2')
RESTCONF_PASS = os.environ.get('RESTCONF_PASS', 'YourPaSsWoRd')

RESTCONF_URL = "https://localhost/restconf/data/ietf-yang-library:modules-state"

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/get-yang-modules")
def get_yang_modules():
    headers = {
        'Accept': 'application/yang-data+json'
    }

    try:
        response = requests.get(
            RESTCONF_URL,
            auth=(RESTCONF_USER, RESTCONF_PASS),
            headers=headers,
            verify=False, 
            timeout=10
        )

        response.raise_for_status()

        return jsonify(response.json())

    except requests.exceptions.RequestException as err:
        print(f"An unexpected error occurred: {err}")
        return jsonify({"error": "An unexpected error occurred", "message": str(err)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
