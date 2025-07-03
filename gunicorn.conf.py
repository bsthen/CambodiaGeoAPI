bind = "0.0.0.0:8080"
workers = 3
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
max_requests = 1000
max_requests_jitter = 50
keepalive = 5