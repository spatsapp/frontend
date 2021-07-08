FROM python:3

WORKDIR /app

COPY ./spats_frontend ./spats_frontend
COPY ./requirements.txt .
COPY ./setup.py .
COPY ./.flaskenv .

RUN pip install -r requirements.txt

CMD [ "python3", "-m", "flask", "run" ]