from flask import Flask, jsonify
import redis

db_conn = redis.Redis(host='localhost', port=6379, db=0)

app = Flask(__name__)

@app.route('/')
def index():
    return "test"

@app.route('/api/v1/interfaces')
def get_interfaces():
    try:
        interface_keys = db_conn.keys('PORT_TABLE:*')
        interfaces = [key.decode('utf-8').split(':')[-1] for key in interface_keys]
        return jsonify({"interfaces": interfaces})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
