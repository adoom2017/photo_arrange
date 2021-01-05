FROM python:3.8.7-slim

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY main.py metadata.py requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

VOLUME ["/usr/input", "/usr/output"]

ENTRYPOINT ["python", "main.py", "-i /usr/input", "-o /usr/output"]
