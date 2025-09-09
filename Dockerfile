# start from an official image
FROM python:3.13
LABEL name="backend-gunicorn"
# args Django
ARG WORKDIR=/opt/services/djangoapp/src
# ARG DJANGO_SUPERUSER_EMAIL
# ARG DJANGO_SUPERUSER_USERNAME
# ARG DJANGO_SUPERUSER_PASSWORD
# ENV DJANGO_SUPERUSER_EMAIL=$DJANGO_SUPERUSER_EMAIL
# ENV DJANGO_SUPERUSER_USERNAME=$DJANGO_SUPERUSER_USERNAME
# ENV DJANGO_SUPERUSER_PASSWORD=$DJANGO_SUPERUSER_PASSWORD
ARG DB_USER
ARG DB_PASSWORD
ARG DB_NAME
ARG DB_ADDR
ARG DB_PORT
ARG DB_ENGINE
ENV DB_USER=$DB_USER
ENV DB_PASSWORD=$DB_PASSWORD
ENV DB_NAME=$DB_NAME
ENV DB_ADDR=$DB_ADDR
ENV DB_PORT=$DB_PORT
ENV DB_ENGINE=$DB_ENGINE

RUN apt update && apt install -y python3-dev libldap2-dev libsasl2-dev libssl-dev gunicorn default-libmysqlclient-dev build-essential gettext

RUN mkdir -p $WORKDIR
WORKDIR $WORKDIR
COPY . .
RUN pip install -r requirements.txt && pip install gunicorn

EXPOSE 80

# RUN python manage.py makemigrations --no-input
# RUN python manage.py migrate --no-input
RUN python manage.py collectstatic --no-input -v 2
# ignore already existing user
# RUN python manage.py createsuperuser --noinput ; exit 0
RUN python manage.py compilemessages
# ENTRYPOINT python manage.py runserver 
ENTRYPOINT gunicorn -c gunicorn.config.py
# ENTRYPOINT gunicorn --bind 0.0.0.0:8080 kantineApp.wsgi:application

# ENTRYPOINT ["sh", "entrypoint.sh"]