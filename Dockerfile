# start from an official image
FROM python:3.12
LABEL name="backend-gunicorn"
# args
ARG WORKDIR=/opt/services/djangoapp/src
ARG DJANGO_SUPERUSER_EMAIL
ARG DJANGO_SUPERUSER_USERNAME
ARG DJANGO_SUPERUSER_PASSWORD
ENV DJANGO_SUPERUSER_EMAIL=$DJANGO_SUPERUSER_EMAIL
ENV DJANGO_SUPERUSER_USERNAME=$DJANGO_SUPERUSER_USERNAME
ENV DJANGO_SUPERUSER_PASSWORD=$DJANGO_SUPERUSER_PASSWORD


RUN mkdir -p $WORKDIR
WORKDIR $WORKDIR

COPY . .

RUN apt update && apt install -y python3-dev libldap2-dev libsasl2-dev libssl-dev gunicorn default-libmysqlclient-dev build-essential
RUN pip install -r requirements.txt

EXPOSE 8080

RUN python manage.py makemigrations
RUN python manage.py migrate
RUN ["python", "manage.py", "collectstatic", "--no-input", "-v 2"]
RUN python manage.py createsuperuser --noinput
# ENTRYPOINT gunicorn -c ./config/gunicorn.config.py

ENTRYPOINT ["sh", "entrypoint.sh"]