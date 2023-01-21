Website Scraping Service
========================

This is a web service that is able to scrape websites and store the links and urls that are found in them.

## Setup

1. If not already present, install Python 3.11 and [virtualeenvwrapper](https://pypi.org/project/virtualenvwrapper/)
2. Create a local virtualenv
```
$ mkvirtualenv {your-env-name}
```
3. Install project dependencies using
```bash
$ pip install -r requirements.txt
```

## Running Tests

We use [nox](https://nox.thea.codes/en/stable/tutorial.html#running-nox-for-the-first-time) as our testing framework. To run the tests do the following:
1. Install `nox`
```bash
$ pip install nox
```
2. Run `nox` tests
```bash
$ nox --session unit_test -f noxfile.py
```

## Running Localy
1. Configure your environment's interpreter into your IDE
2. Make sure your `PATH` and `PYTHONPATH` env variables are configured properly
3. Open `web/app.py` and run the file via the IDE

## Running in Docker
1. Make sure you have `Docker` installed
2. `cd` to project root folder and build the image
```bash
$ docker build . -t website-scraping
```
3. Run the image with exposed ports (make sure you're binded to the correct localhost - could also be `0.0.0.0`)
```bash
$ docker run -d -p 127.0.0.1:5000:5000 website-scraping
```

## Running in K8s
1. Make sure Docker is installed
2. Make sure you have K8s installed either via Docker-Desktop or other service such as minikube
3. Install kubectl
4. Create the K8s deployment
```bash
$ kubectl create -f k8s\deployment.yaml
```
5. Run the K8s deployment
```bash
$ kubectl run website-scraping-deployment --image website-scraping --namespace website-scraping-namespace
```
6. To kill the container and clean up resources run
```bash
kubectl delete namespace website-scraping-namespace
```