FROM ubuntu:latest

# Necessary general packages
RUN apt update && apt install -y \
    apache2 libapache2-mod-wsgi-py3 \
    python3 python3-pip nodejs

# Install python dependencies and setup virtual env
RUN pip3 install flask fuzzywuzzy virtualenv bokeh holoviews scipy nodejs
RUN virtualenv /var/www/expmath/website/venv
RUN . /var/www/expmath/website/venv/bin/activate
RUN pip3 install flask fuzzywuzzy bokeh
RUN exit


# Copy files
RUN mkdir -p /var/www/expmath/website
RUN mkdir -p /var/www/expmath/log
COPY deployment/expmath.conf /etc/apache2/sites-available/
COPY deployment/expmath.wsgi /var/www/expmath/
COPY website/__init__.py /var/www/expmath/website/
COPY website/templates /var/www/expmath/website/templates/
COPY website/static /var/www/expmath/website/static/

RUN mkdir -p /var/www/expmath/plots
COPY plots /var/www/expmath/plots/

COPY deployment/running_script.sh /

# Activate the website
RUN a2enmod wsgi
RUN a2ensite expmath
RUN a2dissite 000-default
RUN service apache2 restart

# Start the bokeh server (This will be the foreground process keeping the Docker
# container running)
CMD ./running_script.sh

# Expose ports
EXPOSE 9001
EXPOSE 80
