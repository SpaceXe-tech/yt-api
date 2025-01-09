# /usr/bin/python3
"""
Converts fastapi app to wsgi app

uwsgi --http=0.0.0.0:8080 -w main:application
"""

from app import app
from a2wsgi import ASGIMiddleware

application = ASGIMiddleware(app)
