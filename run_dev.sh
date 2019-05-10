#!/bin/sh
cd $(dirname "$0")
. env/bin/activate
export FLASK_DEBUG=true
flask run
