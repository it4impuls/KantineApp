"""Gunicorn *development* config file"""

# Django WSGI application path in pattern MODULE_NAME:VARIABLE_NAME
wsgi_app = "kantineApp.wsgi:application"
# The granularity of Error log outputs
loglevel = "debug"
# The number of worker processes for handling requests
workers = 2
# The socket to bind
bind = ":80"
# Restart workers when code changes (development only!)
# reload = True
preload_app = True
# Write access and error info to /var/log
# log_file = "/var/log/gunicorn/dev.log"
accesslog = errorlog = "/var/log/gunicorn/dev.log"

# errorlog = "/var/log/gunicorn/dev.log"
# Redirect stdout/stderr to log file
# capture_output = True
# PID file so you can easily fetch process ID
# pidfile = "/var/run/gunicorn/dev.pid"
# Daemonize the Gunicorn process (detach & enter background)
daemon = False