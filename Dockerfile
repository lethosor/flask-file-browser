FROM python:3.8-slim

WORKDIR /app

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt .

RUN pip install -r requirements.txt gunicorn==20.0.4

COPY templates ./templates
COPY app.py .
COPY config.py .
COPY wsgi.py .

ENTRYPOINT ["gunicorn", "wsgi", "-b", "0.0.0.0:8000"]
