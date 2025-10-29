#!/usr/bin/env python3

from flask import Flask, render_template, jsonify, request
import os
import requests
import json
import subprocess
import os.path
from pathlib import Path
from urllib.parse import urlparse, urlunparse

app = Flask(__name__)

RESTCONF_USER = os.environ.get('RESTCONF_USER', 'chdpc2')
RESTCONF_PASS = os.environ.get('RESTCONF_PASS', 'YourPaSsWoRd')

YANG_MODELS_CACHE_DIR = '/tmp/sonic-yang-models'

GET_MODULES_URL = "https://localhost/restconf/data/ietf-yang-library:modules-state"

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
            GET_MODULES_URL,
            auth=(RESTCONF_USER, RESTCONF_PASS),
            headers=headers,
            verify=False,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()

        try:
            Path(YANG_MODELS_CACHE_DIR).mkdir(parents=True, exist_ok=True)
            
            modules = data["ietf-yang-library:modules-state"]["module"]
            
            fetch_headers = {'Accept': 'application/yang'}
            
            for module in modules:
                module_name = module.get('name')
                schema_url = module.get('schema')
                
                if not module_name or not schema_url:
                    continue
                
                model_filename = f"{module_name}.yang"
                model_path = os.path.join(YANG_MODELS_CACHE_DIR, model_filename)
                
                if not os.path.exists(model_path):
                    
                    parsed_url = urlparse(schema_url)
                    fixed_url = urlunparse(parsed_url._replace(netloc='localhost'))

                    mod_resp = requests.get(
                        fixed_url,
                        auth=(RESTCONF_USER, RESTCONF_PASS),
                        headers=fetch_headers,
                        verify=False,
                        timeout=10
                    )
                    mod_resp.raise_for_status()
                    
                    with open(model_path, 'w') as f:
                        f.write(mod_resp.text)

        except Exception as e:
            print(f"Error during sync: {e}")

        return jsonify(data)

    except requests.exceptions.RequestException as err:
        print(f"Unexpected error: {err}")
        return jsonify({"error": "Unexpected error", "message": str(err)}), 500

@app.route("/custom-request", methods=['POST'])
def custom_request():
    try:
        data = request.get_json()
        method = data.get('method', 'GET').upper()
        url = data.get('url')
        payload_str = data.get('payload') 

        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        if url.startswith('/restconf'):
            url = f"https://localhost{url}"

        headers = {
            'Content-Type': 'application/yang-data+json',
            'Accept': 'application/yang-data+json'
        }

        kwargs = {
            "auth": (RESTCONF_USER, RESTCONF_PASS),
            "headers": headers,
            "verify": False,
            "timeout": 10
        }

        if method in ['POST', 'PATCH', 'PUT'] and payload_str:
            try:
                kwargs['json'] = json.loads(payload_str)
            except json.JSONDecodeError as json_err:
                return jsonify({"error": "Invalid JSON in payload", "message": str(json_err)}), 400
        
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()

        if response.status_code == 204:
            return jsonify({"success": True, "message": f"Success 204"})
        
        try:
            return jsonify(response.json())
        except requests.exceptions.JSONDecodeError:
            return jsonify({"success": True, "status_code": response.status_code, "data": response.text})

    except requests.exceptions.RequestException as err:
        if err.response is not None:
            try:
                error_details = err.response.json()
            except requests.exceptions.JSONDecodeError:
                error_details = err.response.text
            return jsonify({
                "error": f"Error from {method} to {url}", 
                "message": str(err),
                "details": error_details
            }), err.response.status_code
        return jsonify({"error": "Unexpected server error", "message": str(err)}), 500
    except Exception as e:
        return jsonify({"error": "General server error", "message": str(e)}), 500

@app.route("/get-model-tree", methods=['POST'])
def get_model_tree():
    try:
        data = request.get_json()
        module_name = data.get('module_name')
        if not module_name:
            return jsonify({"error": "module_name not provided"}), 400

        model_filename = f"{module_name}.yang"
        model_path = os.path.join(YANG_MODELS_CACHE_DIR, model_filename)

        if not os.path.exists(model_path):
            return jsonify({
                "error": "Module not found in cache",
                "details": f"{model_path} does not exist."
            }), 404

        command = [
            'pyang', 
            '-f', 'tree',             
            '-p', YANG_MODELS_CACHE_DIR, 
            model_path                  
        ]
        
        result = subprocess.run(command, capture_output=True, text=True, check=False)

        if result.returncode != 0:
            return jsonify({
                "error": "pyang command failed", 
                "details": result.stderr 
            }), 500
        
        return jsonify({"success": True, "tree": result.stdout})

    except Exception as e:
        print(f"General server error: {e}")
        return jsonify({"error": "General server error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
