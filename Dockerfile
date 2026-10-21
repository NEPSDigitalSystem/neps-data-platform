FROM python:3.15-slim

WORKDIR /app
RUN groupadd -r neps && useradd -r -g neps neps

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY etl/ ./etl/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY ops/ ./ops/

RUN chown -R neps:neps /app
USER neps

CMD ["python", "-m", "etl.main"]
