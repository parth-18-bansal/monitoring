from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time

app = Flask(__name__)

REQUEST_COUNT = Counter('flask_app_requests_total', 'Total number of HTTP requests', ['method', 'endpoint', 'http_status'])
REQUEST_LATENCY = Histogram('flask_app_request_latency_seconds', 'Latency of HTTP requests in seconds', ['endpoint'])
IN_PROGRESS = Gauge('flask_app_inprogress_requests', 'In-progress requests')

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    resp_time = time.time() - request.start_time
    REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()
    REQUEST_LATENCY.labels(request.path).observe(resp_time)
    return response

@app.route('/')
@IN_PROGRESS.track_inprogress()
def home():
    time.sleep(0.2)  # Simulate delay
    return "Welcome to the Flask App!"

@app.route('/api/greet/<name>')
@IN_PROGRESS.track_inprogress()
def greet(name):
    return jsonify({"message": f"Hello, {name}!"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
