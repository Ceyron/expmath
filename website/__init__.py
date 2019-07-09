# -*- coding: utf-8 -*

from flask import Flask, render_template
from bokeh.embed import server_document

"""
Add a new plot:
    1) Create a template
    2) Add to the topic dictionary
"""

# ip address and port of the bokeh server
IP = "134.169.53.27"
PORT = "9001"

app = Flask(__name__)

# The following dictionaries contain the plot_name (as used as a link)
# for the key and the item is the proper name that is going to be
# displayed on the website (i.e., rendered into the template).
# Changing the ordering in here will change the order of appearance
# in the dropdown.
analysis_1 = {
    "epsilon_delta_kriterium": "Epsilon-Delta Kriterium",
    "epsilon_kriterium": "Epsilon Kriterium",
    "integrale_und_ableitungen": "Integrale und Ableitungen",
    "taylorpolynome": "Taylorpolynome",
    "trigonometrische_funktionen": "Trigonometrische Funktionen",
    }

lineare_algebra = {
    "komplexes_wurzelziehen": "Komplexes Wurzelziehen",
    "komplexe_zahlen": "Komplexe Zahlen",
    "matrizen_2d": "Matrizen und Lineare Transformationen",
    }

analysis_2 = {
    "multivariable_funktionen": "Multivariable Funktionen",
    }

ode = {
    "richtungsfeld": "Richtungsfeld",
    "phasen_plot": "Phasen-Plot",
    }

analysis_3 = {
    "test": "Test",
    }

pde = {
    "schwingungen": "Schwingungen",
    "variationsformulierung": "Variationsformulierung",
    }

all_plot_keys = \
        list(analysis_1.keys()) + list(lineare_algebra.keys()) + \
        list(analysis_2.keys()) + list(ode.keys()) + \
        list(analysis_3.keys()) + list(pde.keys())

#Homesite
@app.route('/', methods=['GET'])
def bkapp_page():
    return render_template("home.html", template="Flask",
        analysis_1=analysis_1,
        lineare_algebra=lineare_algebra,
        analysis_2=analysis_2,
        ode=ode,
        analysis_3=analysis_3,
        pde=pde,
    )

# General Routing
@app.route("/<string:plot_name>", methods=["GET"])
def plot_app(plot_name):
    if plot_name.lower() in all_plot_keys:
        script = server_document("http://" + IP + ":" + PORT + "/" + plot_name.lower())
        return render_template(plot_name.lower() + ".html", script=script,
            analysis_1=analysis_1,
            lineare_algebra=lineare_algebra,
            analysis_2=analysis_2,
            ode=ode,
            analysis_3=analysis_3,
            pde=pde,
        )
    else:
        return "Plot {0} not found".format(plot_name)



# If using the flask-intern webserver instead of a WSGI gateway (i.e., if this file is called from the terminal)
if __name__ == '__main__':
  #  app.run(host="0.0.0.0", port=8080)
    app.run(port=8080)
