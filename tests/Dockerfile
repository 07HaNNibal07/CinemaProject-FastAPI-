FROM python:3.11-slim-bookworm

WORKDIR /app

COPY booking-service/requirements.txt /tmp/booking-requirements.txt
COPY cinema-service/requirements.txt /tmp/cinema-requirements.txt
COPY tests/requirements.txt /tmp/tests-requirements.txt

RUN pip install --no-cache-dir \
    -r /tmp/booking-requirements.txt \
    -r /tmp/cinema-requirements.txt \
    -r /tmp/tests-requirements.txt

CMD ["pytest", "-q", "tests"]
