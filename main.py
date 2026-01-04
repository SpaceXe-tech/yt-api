# /usr/bin/python3
"""
Converts fastapi app to wsgi app

uwsgi  -w main:application
"""

from app import app
from a2wsgi import ASGIMiddleware

application = ASGIMiddleware(app)
