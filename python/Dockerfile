FROM python:3.11-slim

LABEL maintainer="jaimeercilla11"
LABEL description="Distributed Matrix Multiplication with MapReduce"

WORKDIR /app

RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p results/plots

ENV PYTHONUNBUFFERED=1

CMD ["python", "benchmark.py"]