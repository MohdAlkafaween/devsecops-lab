FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ ./app/

EXPOSE 8080
CMD ["python", "app/main.py"]
