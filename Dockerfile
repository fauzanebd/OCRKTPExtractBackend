FROM python:3.12-slim-bullseye

RUN apt-get update

WORKDIR /app

COPY requirements.txt /app/requirements.txt  
RUN pip install -r requirements.txt

COPY . .

RUN rm -f .env
COPY start-script-flask /usr/local/bin
RUN chmod +x /usr/local/bin/start-script-flask
RUN sed -i -e 's/\r$//' /usr/local/bin/start-script-flask

CMD ["start-script-flask"]