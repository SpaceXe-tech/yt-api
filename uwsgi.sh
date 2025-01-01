#!/usr/bin/bash
target_server=$1

if [ "$target_server" == "proxy" ]; then
   echo "[PROXY] Running on 0.0.0.0:8080"
   uwsgi --http=0.0.0.0:8080 -w servers.proxy:app --enable-threads
elif [ "$target_server" == "static" ]; then
   echo "[STATIC] Running on 0.0.0.0:8888"
   echo "[STATIC] Serving files from static/downloads at /file"
   uwsgi --http=0.0.0.0:8888 --static-map /file=static/downloads -w servers.static:app --enable-threads
else
   echo "proxy|static must be explicitly declared"
   echo "e.g ./uwsgi.sh proxy"
fi
