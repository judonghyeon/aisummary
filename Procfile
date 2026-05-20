web: uvicorn main:app --host 0.0.0.0 --port $PORT
worker: celery -A celery_app:celery worker --loglevel=info
