#!/bin/sh
cd $(dirname "$0")
. bin/activate
export FLASK_DEBUG=true
flask run
