#!/bin/sh
cd $(dirname "$0")
. bin/activate
export FLASK_DEBUG=false
gunicorn -b unix:./.sock wsgi
