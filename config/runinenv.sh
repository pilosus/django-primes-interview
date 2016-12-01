#!/bin/bash

echo "Activating virtualenv..."
. /home/vitaly/django-primes-interview/.venv/bin/activate

echo "Exporting env variables"
set -a
source /home/vitaly/django-primes-interview/primes/.env
set +a

echo "Running command"
exec "$@"
