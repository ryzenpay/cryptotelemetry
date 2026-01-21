FROM python:3.10-slim

RUN useradd cryptotelementry

COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

USER cryptotelementry
WORKDIR /app

COPY main.py main.py

CMD ["opentelemetry-instrument", "python", "main.py"]