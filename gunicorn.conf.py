# This is the gunicron config file. For more information on the configs here see - https://docs.gunicorn.org/en/stable/settings.html

chdir = "web"

loglevel = "debug"

worker_class = "gthread"

workers = 1 # set this to 1 for easy debug purposes

threads = 2

bind = "0.0.0.0:5000"

