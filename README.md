# expmath
Online visualization tool for basic engineering math concepts using flask and bokeh

https://www.tutorialspoint.com/flask/flask_quick_guide.htm

https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world

# Usage
Inside data there is the Flask and Bokeh directory. Use the build-in bokeh server (*bokeh serve*) to serve the entire Bokeh directory with the appropriate commands to make it visibile to the outside or use the available shell-script. For additonal security use a proxy server in front of the bokeh tornado. The Flask App serves the dynamically created content around the interactive diagrams. It is connected to an Apache Webserver by the wsgi interface. Make sure Apache is set up correctly.

# Road-Map
Create two more examples, consisting of a dynamic animation of an oscillating string showing of the combination of eigen frequencies and eigen modes and a three-dimensional example of a transformation taking place.


# TODO

* Dockerize the entire application: This might consist of two independent docker containers, one for the static webpage und one for the interactive bokeh content
* Get the DNS working
