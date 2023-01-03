FROM python:3.11.1-bullseye
WORKDIR /app
COPY requirements.txt requirements.txt
RUN apt update -y
RUN pip install -r requirements.txt
COPY . .
CMD ["python3", "-u", "main.py"]
