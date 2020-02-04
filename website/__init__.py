# -*- coding: utf-8 -*

from flask import Flask, render_template
from bokeh.embed import server_document

from fuzzywuzzy import fuzz

"""
Add a new plot:
    1) Create a template
    2) Add to the topic dictionary
"""

# ip address and port of the bokeh server
IP = "134.169.53.27"
#IP = "127.0.0.1"
PORT = "9001"

# The fuzzy ratio needed at least to set the recommendation
RATIO = 50

app = Flask(__name__)

# The following dictionaries contain the plot_name (as used as a link)
# for the key and the item is the proper name that is going to be
# displayed on the website (i.e., rendered into the template).
# Changing the ordering in here will change the order of appearance
# in the dropdown.
analysis_1 = {
    #"sinus": "Sinus Funktion mit variable ŕ Phasenverschiebung",
    "epsilon_kriterium": "Folgen und Grenzwerte",
    #"ordnungssymbol": "Größenordnungen und Landausches Ordnungssymbol (TODO)",
    "reihen": "Partialsummen und Reihen",
    "einfache_funktionen": "Standardfunktionen",    
    "trigonometrische_funktionen": "Trigonometrische Funktionen",
    "schrittweises_skizzieren": "Schrittweises Skizzieren von Funktionen",
    "epsilon_delta_kriterium": "Stetigkeit von Funktionen",
    "diffbarkeit": "Differenzierbarkeit von Funktionen",
    #"integrale_und_ableitungen": "Integrale und Ableitungen",
    #"riemann_integrale": "Ober- und Untersummen (Riemann-Integrale)",
    #"taylorpolynome": "Taylor-Polynome",
    #"umkehrfunktionen": "Umkehrfunktionen",
    }

lineare_algebra = {
    "komplexe_zahlen": "Komplexe Zahlen",
    "komplexes_wurzelziehen": "Komplexe Wurzeln",
    #"basisvektoren": "Zerlegung beliebiger Vektoren in Basisvektoren (TODO)",
    #"matrizen_2d": "Matrizen und lineare Transformationen (2D)",
   # "matrizen_3d": "Matrizen und lineare Transformationen (3D)",
    #"eigenvektoren": "Eigenvektoren von Matrizen (TODO)",
    #"skalar_produkt": "Skalarprodukt von Vektoren (2D) (TODO)",
    #"vektor_produkt": "Vektorprodukt/Kreuzprodukt von Vektoren (3D) (TODO)",
    }

analysis_2 = {
    #"multivariable_funktionen": "Multivariate Funktionen - Skalarfelder",
    #"partielle_ableitungen": "Partielle Ableitungen (TODO)",
    #"gradient": "Gradient (TODO)",
    #"divergenz": "Divergenz (TODO)",
    #"rotation": "Rotation (TODO)",
    "parametrisierungen_2d": "Parametrisierung von Kurven (2D)",
    #"parametrisierungen_3d": "Parametrisierung von Linien im Raum (3D) (TODO)",
    #"kurven_integrale_1": "Kurven-Integrale 1. Art (TODO)",
    #"fourier_reihen": "Fourier-Reihen",
    #"fourier_zerlegung": "Fourier-Zerlegung - Frequenzraum (TODO)",
    }

ode = {
    #"einfache_ode": "Einfache gewöhnliche Differentialgleichungen (TODO)",
    #"federschwinger": "Federschwinger (TODO)",
  #  "richtungsfeld": "Richtungsfeld",
   # "phasen_plot": "Phasenplot",
    #"lipschitz_stetigkeit": "Lipschitzstetigkeit - Existenz und Eindeutigkeit\
    #(TODO)",
    #"laplace_transformation": "Laplace-Transformation (TODO)",
    }

analysis_3 = {
    #"satz_von_gauss": "Satz von Gauß (TODO)",
    #"transformations_satz": "Integraltransformationen und Transformationssatz\
    #    (TODO)",
    }

pde = {
    "waermeleitung": "Wärmeleitung",
    "schwingungen": "Schwingungen",
    "wellen": "Wellenausbreitung",
    "transport_gleichung": "Transportgleichung und Charakteristiken",
    #"membran_verformung": "Verformung von Membranen (Maximumsprinzip,\
    #    Mittelwerteigenschaft (TODO)",
    #"fundamental_loesungen": "Fundamentallösungen und Faltungen (TODO)",
    #"green_funktion": "Green-Funktion (TODO)",
    "variationsformulierung": "Variationsformulierung",
    #"finite_elemente": "Finite Elemente",
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
        if plot_name.lower() in analysis_1:
            folder = "analysis_1/"
        elif plot_name.lower() in lineare_algebra:
            folder = "lineare_algebra/"
        elif plot_name.lower() in analysis_2:
            folder = "analysis_2/"
        elif plot_name.lower() in ode:
            folder = "ode/"
        elif plot_name.lower() in analysis_3:
            folder = "analysis_3/"
        elif plot_name.lower() in pde:
            folder = "pde/"
        else:
            folder = ""
        script = server_document("http://" + IP + ":" + PORT + "/" +
                plot_name.lower())
        return render_template(folder + plot_name.lower() + ".html",
                script=script,
                analysis_1=analysis_1,
                lineare_algebra=lineare_algebra,
                analysis_2=analysis_2,
                ode=ode,
                analysis_3=analysis_3,
                pde=pde,
        )
    else:
        closest_match = None
        for key in all_plot_keys:
            if fuzz.ratio(plot_name.lower(), key) > RATIO:
                ratio = fuzz.ratio(plot_name.lower(), key)
                closest_match = key
        if closest_match != None:
            return render_template("recommend.html", recommend=closest_match,
                    analysis_1=analysis_1,
                    lineare_algebra=lineare_algebra,
                    analysis_2=analysis_2,
                    ode=ode,
                    analysis_3=analysis_3,
                    pde=pde,
            )
        else:
            return render_template("404.html",
                    analysis_1=analysis_1,
                    lineare_algebra=lineare_algebra,
                    analysis_2=analysis_2,
                    ode=ode,
                    analysis_3=analysis_3,
                    pde=pde,
            )



# If using the flask-intern webserver instead of a WSGI gateway (i.e., if this file is called from the terminal)
if __name__ == '__main__':
  #  app.run(host="0.0.0.0", port=8080)
    app.run(port=8080)
