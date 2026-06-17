FROM python:3

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

# RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
# USER appuser

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000","--reload"]