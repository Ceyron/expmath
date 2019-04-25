#fuer deutsche Umlaute 
# -*- coding: utf-8 -*

#Benoetigte Zusatzbibliotheken, Flask und Bokeh
from flask import Flask, render_template,request
from bokeh.embed import server_document

#Beispiel der Einbindung einer neuen Website am Ende des Skriptes

app = Flask(__name__)

#Homesite
@app.route('/', methods=['GET'])
def bkapp_page():

        return render_template("Home.html", template="Flask")

#Testsite A
@app.route('/ContentA', methods=['GET'])
def ContentA():

        return render_template("ContentA.html", template="Flask")

#Testsite B
@app.route('/ContentB', methods=['GET'])
def ContentB():

        return render_template("ContentB.html", template="Flask")

#Testsite C
@app.route('/ContentC', methods=['GET'])
def ContentC():

        return render_template("ContentC.html", template="Flask")

#Testsite D
@app.route('/ContentD', methods=['GET'])
def ContentD():

        return render_template("ContentD.html", template="Flask")


#Site Folgen
@app.route('/Folgen', methods=['GET'])
def Folgen():

        script = server_document("http://134.169.6.175:9001/Epsilon_Kriterium")
        return render_template("Folgen.html", template="Flask", script=script)

#Site Schwingungen
@app.route('/Schwingungen', methods=['GET'])
def Schwingungen():

        script = server_document("http://134.169.6.175:9001/Schwingungen")
        return render_template("Schwingungen.html", template="Flask", script=script)
      

#Site Richtungsfeld
@app.route('/Richtungsfeld', methods=['GET'])
def Richtungsfeld():

        script = server_document("http://134.169.6.175:9001/Richtungsfeld")
        return render_template("Richtungsfeld.html", template="Flask", script=script)
      

#Leere Site
@app.route('/Leer', methods=['GET'])
def Leer():

        return render_template("Leer.html", template="Flask")
        
###Beispieleinbindung neuer Site (Ohne #)
###Es existiert eine NAME.html im /templates Verzeichnis.
###Es existiert ein Bokehplot für diese Anwendung, URL benoetigt (Eigenes Skript)
###Website Navigation wird in wrapper.html angepasst. (/templates Verzeichnis)
#@app.route('/NAME', methods=['GET'])
#def NAME():
#
#        script = server_document("URL_ZU_BOKEH_SITE")
#        return render_template("NAME.html", template="Flask", script=script)
#
#
###

#Notwendig, wenn Skript nicht ueber WSGI gestartet wird, flaskeigener Webserver wird gestartet
if __name__ == '__main__':
  #  app.run(host="0.0.0.0", port=8080)
        app.run(port=8080)
