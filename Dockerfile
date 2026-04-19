FROM python:3.12
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . /app/

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && gunicorn DiplomProject.wsgi:application --bind 0.0.0.0:8000"]