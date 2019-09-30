#!/usr/bin/env bash

echo "Running migrate..."
flask db init
flask db migrate
flask db upgrade

echo "Running any commands passed to this script from CMD or command..."
exec "$@"