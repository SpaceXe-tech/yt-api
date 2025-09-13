#!/usr/bin/env bash
set -euo pipefail

target_server=${1:-""}
host=${2:-"0.0.0.0"}
port=""

# default ports by server type (can still override with 3rd arg)
if [ "$target_server" == "proxy" ]; then
  port=${3:-"8080"}
elif [ "$target_server" == "static" ]; then
  port=${3:-"8888"}
else
  echo "[ERROR] Usage: $0 proxy|static [host] [port]"
  echo "  examples:"
  echo "    $0 proxy                    # bind 0.0.0.0:8080"
  echo "    $0 proxy 69.62.84.40 8080   # bind 69.62.84.40:8080"
  echo "    $0 static 127.0.0.1 8888    # bind localhost:8888"
  exit 1
fi

# quick check: is the host present on this machine?
if [[ "$host" != "0.0.0.0" && "$host" != "127.0.0.1" && "$host" != "localhost" ]]; then
  if ! ip addr show | grep -q -F "$host"; then
    echo "[WARNING] IP $host not found on this machine's interfaces."
    echo "          If this IP is remote, uWSGI must run on the host that owns that address."
    echo "          Proceeding anyway — uWSGI will fail to bind if the IP is missing."
  fi
fi

if [ "$target_server" == "proxy" ]; then
   echo "[INFO] To daemonize process use : make uwsgi-proxy"
   echo "[PROXY] Running on ${host}:${port}"
   uwsgi --http="${host}:${port}" -w servers.proxy:app --enable-threads
elif [ "$target_server" == "static" ]; then
   echo "[INFO] To daemonize process use : make uwsgi-static"
   echo "[STATIC] Running on ${host}:${port}"
   echo "[STATIC] Serving files from static/downloads at /file"
   uwsgi --http="${host}:${port}" -w servers.static:app --enable-threads
fi
