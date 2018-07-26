FROM python:latest

COPY start.py ./
COPY requirements.txt ./
COPY google.js /tmp/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "start.py"]
