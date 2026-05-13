import os
import sys

# Ensure the root of the lambda task is in the Python path
if '/var/task' not in sys.path:
    sys.path.insert(0, '/var/task')

import serverless_wsgi
from app import app

def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)
