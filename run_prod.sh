#!/bin/sh
cd $(dirname "$0")
. bin/activate
export FLASK_DEBUG=false
export CONFIG=config.ProdConfig
gunicorn -b unix:./.sock wsgi
