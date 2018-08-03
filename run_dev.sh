#!/bin/sh
cd $(dirname "$0")
. bin/activate
export FLASK_DEBUG=true
export CONFIG=config.DevConfig
flask run
