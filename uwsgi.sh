#!/usr/bin/bash
uwsgi --http=0.0.0.0:8080 --static-map /file=static/downloads -w static_server:application --enable-threads