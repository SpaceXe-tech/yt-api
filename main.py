# /usr/bin/python3
"""
Converts fastapi app to wsgi app

uwsgi --http=69.62.84.40:8080 -w main:application
"""

from app import app
from a2wsgi import ASGIMiddleware

application = ASGIMiddleware(app)
