# ExpMath (Exploratory Mathematics)

![Example Screenshot](https://user-images.githubusercontent.com/27728103/112809743-9d09b100-907a-11eb-955e-ebbac9a7fe6e.png)

ExpMath is a project of the Institute of Computational Mathematics at the
Technical University of Braunschweig. It aims at providing a web application
visualizing mathematical ideas to students of the engineering disciplines of the
first semesters. The concept is to not provide a more sophisticated alternative
to Matlab, Mathematica, Octave, GNUplot etc. but to empower students with
the capabilities of visualization even if they not yet have the skills to create
the tools themselves.

The ExpMath site consists of two parts:

1. The actual interactive plots are rendered with the help of bokeh, a Python
   visualization library in combination with some custom extensions.
2. Each interactive plot is framed within static components summarizing the
   theoretical background and enhancing the user experience with questions.

# Usage

### Deployment with docker

1. Clone the repository to the production server, and adjust the IP address in
   website/__init__.py to the one of the server
2. Make sure docker is installed and the docker daemon is running
3. Use the script to build the docker container

    ./build_on_server.sh

4. Use the script to deploy the server (if necessary stop an old docker
   container beforehand)

    ./start_on_server.sh

5. Use the script to stop a running server

    ./stop_on_server.sh

### Manual deployment on a Ubuntu machine

1. Install the necessary dependencies

    sudo apt update

    sudo apt install apache2 libapache2-mod-wsgi-py3 python3 python3-pip

    sudo pip3 install flask fuzzywuzzy virtualenv bokeh holoviews scipy

2. Create the folder structure

    mkdir -p /var/www/expmath/website
    
    mkdir -p /var/www/expmath/log

    mkdir -p /var/www/expmath/plots

3. Create a virtual environment for the flask application

    virtualenv /var/www/expmath/website/venv

    source /var/www/expmath/website/venv/bin/activate

    pip3 install flask fuzzywuzzy bokeh

    exit

4. Clone the github repository and !! adjust the IP address in
   website/__init__.py to the one of the server

    git clone https://github.com/Ceyron/expmath.git ~/expmath

5. Copy the files

    cp -r ~/expmath/plots/* /var/www/expmath/plots/

    cp -r ~/expmath/website/* /var/www/expmath/website/

    cp ~/expmath/deployment/expmath.conf /etc/apache2/sites-available/

    cp ~/expmath/deployment/expmath.wsgi /var/www/expmath/

6. Configure Apache

    sudo a2enmod wsgi

    sudo a2ensite expmath

    sudo a2dissite 000-default

    sudo apache2ctl restart

7. Make sure the firewall does not block port 80 and 9001


# Embedding in an all static web-app
If you are not using flask, then it is still possible interactive bokeh-plots,
i.e. ones that will callback to the bokeh server, by including a script tag as
follows
    
    <script
        src="http://[IP]:[PORT]/[PLOT\_NAME]/autoload.js?bokeh-autoload-element&
        bokeh-app-path=/[PLOT\_NAME]&bokeh-absolute-url=http://[IP]:[PORT]/
        [PLOT\_NAME]" id="1000"></script>



