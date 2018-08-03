#!/bin/sh
cd $(dirname "$0")
export FLASK_DEBUG=false
export CONFIG=config.ProdConfig
flask run
