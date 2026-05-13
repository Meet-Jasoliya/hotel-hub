import sys
import os

# Add the root directory to the python path so modules can be found
root_dir = os.path.abspath(os.path.join(os.path.dirname(__name__), '..', '..'))
sys.path.append(root_dir)

import serverless_wsgi
from app import app

def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)
