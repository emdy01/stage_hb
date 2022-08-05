# Modules nécessaires
import json
from tkinter import Grid
from turtle import width
import guizero as gz
import getopt
import sys
import requests

class GUI():
    def __init__(self):
        self.app = gz.App("Application commandes du dossier",height=200)
        
        self.title_box = gz.Box(self.app, width="fill", align="top", border=True)
        gz.Text(self.title_box,text="Panneau de contrôle")
        
        #début description des contrôles de la GUI
        self.control_box= gz.Box(self.app, width="fill", align="top", border=True)
        self.form_box=  gz.Box(self.control_box,layout="grid",width="fill",align="left",border=True)
        
        self.boutonUp = gz.PushButton(self.form_box,grid=[0,0],text = "Lever le dossier",width="30",command=self.up)
        self.boutonDown = gz.PushButton(self.form_box,grid=[0,1],text = "Baisser le dossier",width="30",command=self.down)
        
        gz.Text(self.form_box,size=10,text="Pas",grid=[1,0],align="left",width=10)
        self.pas_ig = self.steps = gz.TextBox(self.form_box,grid=[2,0],text="512",)
        
        gz.Text(self.form_box,size=10,text="Position",grid=[1,1],align="left",width=10)
        self.position_ig = self.position = gz.TextBox(self.form_box,grid=[2,1],text="0")
        
        #début de la description des statuts
        self.status_box = gz.Box(self.app,layout="grid",width="fill",align="bottom",border=True)
        
        gz.Text(self.status_box,size=8,text="URL Serveur:",grid=[0,0],align="left")
        self.url_ig = gz.Text(self.status_box,size=8,text=url,grid=[1,0],align="right")
        
        gz.Text(self.status_box,size=8,text="Statut:",grid=[0,1],align="left")
        self.status_ig = gz.Text(self.status_box,size=8,text="??",grid=[1,1],align="right")
        
        # Complétion des statuts avec les infos renvoyées par le serveur
        urlstatus=url+"/status"
        response = requests.get(urlstatus)
        r=json.loads(response.text)
        self.status_ig.value=r['serveur']
        self.position_ig.value=r['position']        
 
    def launch(self): # pour le main
        self.app.display()
    
    def up(self):
        #Envoi de la requête
        n = self.pas_ig.value
        url_up=url+"/up/"+str(n)
        
        #Réception de la réponse
        response = requests.get(url_up)
        r=json.loads(response.text)
        
        #Retranscription sur l'interface
        self.url_ig.value=url_up
        self.position_ig.value=r['position']
        self.status_ig.value=r['msg']+" rc:"+ str(response.status_code)
        
    def down(self): # Même structure que up
        n = self.pas_ig.value
        url_up=url+"/down/"+str(n)
        
        response = requests.get(url_up)
        r=json.loads(response.text)
        
        self.url_ig.value=urlup
        self.position_ig.value=r['position']
        self.status_ig.value=r['msg']+" rc:"+ str(response.status_code)
    
   
    def stopSystem(self):
        self.app.hide()

def usage():
    print("--url indique l'url nom de host du serveur  ('http://127.0.0.1:8080' par defaut)")
    print("-h ou --help imprime ce message")

if __name__ == "__main__":
    url ="http://127.0.0.1:8080"     #url par default
    try:                                
        opts, args = getopt.getopt(sys.argv[1:], "h:p:", ["help","url="])  #le programme supporte 3 paramètres : -h ou --help  -p ou --port et l'url du serveur
    except getopt.GetoptError:          
        usage()                         
        sys.exit(2)                     
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()                     
            sys.exit()                     
        elif opt in ("--url"):
            url = arg               
    interface = GUI()
    interface.launch()
