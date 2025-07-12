FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean
COPY . /app
RUN pip install --upgrade pip && pip install .
RUN chmod +x /app/entrypoint.sh /app/waiting_for_rabbitmq.sh
ENTRYPOINT ["sh", "/app/entrypoint.sh"]