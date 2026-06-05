FROM python:3.14-slim

WORKDIR /app
RUN groupadd -r neps && useradd -r -g neps neps

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chown -R neps:neps /app
USER neps

CMD ["python", "-m", "etl.main"]
