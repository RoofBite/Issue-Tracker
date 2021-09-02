# Python and Linux Version 
FROM python:3.8-slim-buster

RUN apt-get update && apt-get install -y git
RUN apt-get update \
&& apt-get install gcc -y \
&& apt-get clean

COPY requirements.txt /app/requirements.txt

# Configure server
RUN set -ex \
    && pip install --upgrade pip \  
    && pip install --no-cache-dir -r /app/requirements.txt 

# Working directory
WORKDIR /app

ADD . .

#Uncomment for local usage

# EXPOSE 8000
# CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "issue_tracker_project.wsgi:application"]


#Uncomment for Heroku

CMD gunicorn issue_tracker_project.wsgi:application --bind 0.0.0.0:$PORT

