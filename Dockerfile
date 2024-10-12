FROM python:3.12-slim

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install uv

COPY uv.lock .
COPY pyproject.toml .

RUN uv sync

COPY . /app
