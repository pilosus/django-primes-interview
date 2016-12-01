#!/bin/bash

echo "Activating virtualenv..."
. /home/vitaly/django-primes-interview/.venv/bin/activate

echo "Running celery flower"
/home/vitaly/django-primes-interview/.venv/bin/celery flower -A primes --port=5555
