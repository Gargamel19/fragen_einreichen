python3 -m venv venv
source venv/bin/activate & pip install wheel & pip install -r requirements.txt & gunicorn --bind 0.0.0.0:5000 wsgi:app


