FROM python:3.9

WORKDIR /app

RUN pip3 install gunicorn==20.1.0
RUN pip3 freeze > requirements.txt

COPY . .

RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--access-logfile" , "-", "foodgram.wsgi"]