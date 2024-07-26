FROM python:3.11.4

COPY requirements.txt /

COPY . /app

RUN pip install --no-cache-dir -r /requirements.txt

WORKDIR /app

ENV PYTHONUNBUFFERED=1

CMD [ "flask", "--app", "listener", "run", "--host", "0.0.0.0", "--port", "80" ]
