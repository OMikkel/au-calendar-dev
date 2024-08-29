FROM python:3.12-slim

ENV PIP_NO_CACHE_DIR=1

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 8080

ENTRYPOINT ["python", "__main__.py"]