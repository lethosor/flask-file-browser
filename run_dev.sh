#!/bin/sh
cd $(dirname "$0")
export FLASK_DEBUG=true
export CONFIG=config.DevConfig
flask run
