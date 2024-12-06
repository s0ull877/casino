FROM python:3.10
WORKDIR .
COPY ./requirements.txt .
RUN apt-get install gcc
RUN python -m pip install --upgrade pip && \
    pip install -r requirements.txt --no-cache-dir
COPY . .
RUN chmod +x wsgi.sh
RUN chmod +x asgi.sh
CMD ["sh", "-c", "./wsgi.sh"]
CMD ["sh", "-c", "./start.sh"]