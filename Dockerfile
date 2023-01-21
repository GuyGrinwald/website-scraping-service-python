# pull official base image
FROM python:3.11.1-slim-buster

# set work directory
WORKDIR /usr/website-scraping-service

# set Python environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/website-scraping-service/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . /usr/website-scraping-service/

# annouce needed ports
EXPOSE 5000

# executes our gunicorn
ENTRYPOINT ["./gunicorn.sh"]