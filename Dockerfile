FROM python:3.12

WORKDIR /app

COPY ./frontend ./frontend
COPY ./static ./static
COPY ./templates ./templates
COPY ./frontend.cfg .

COPY ./requirements.txt .

RUN pip install -r requirements.txt

CMD [ "python3", "-m", "frontend" ]