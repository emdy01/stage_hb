# Modules nécessaires
import guizero as gz
#import RPi.GPIO as io
from http.server import BaseHTTPRequestHandler, HTTPServer
import multiprocessing as mp
import time
import sys


class stepmotor():
    

    def setup(self):
        """
        coil_A_1_pin = 4 # green
        coil_A_2_pin = 27 # red
        coil_B_1_pin = 23 # black
        coil_B_2_pin = 24 # yellow
        
        
        # configuration des GPIO
        io.setmode(io.BCM)  
        io.setwarnings(False)
        
        io.setup(4, io.OUT)
        io.setup(27, io.OUT)
        io.setup(23, io.OUT)
        io.setup(24, io.OUT) """

    def seq_alim(self):
        # Stockage mémoire de la séquence d'alimentation des phases du steppermotor

        Seq = []
        Seq.append([1,0,0,0])
        Seq.append([1,1,0,0])
        Seq.append([0,1,0,0])
        Seq.append([0,1,1,0])
        Seq.append([0,0,1,0])
        Seq.append([0,0,1,1])
        Seq.append([0,0,0,1])
        Seq.append([1,0,0,1])
        return Seq

    def setStep(self, w1, w2, w3, w4):
        # Alimenter les phases. w1, w2, w3, w4 représentent les niveaux logiques (et donc de tension)
        """
        io.output(4, w1)
        io.output(27, w2)
        io.output(23, w3)
        io.output(24, w4)
    """
    def forward(self,x):
        # Faire avancer le moteur de x pas en parcourant la séquence d'alimentation
        delay = 0.001
        StepCount = 8
        Seq = self.seq_alim()
        self.setup()
        if x <= 13824:
            for i in range(x):                                                                                                                                                               
                for j in (range(StepCount)):
                    self.setStep(Seq[j][0], Seq[j][1], Seq[j][2], Seq[j][3])
                    time.sleep(delay)
        self.setStep(0,0,0,0)
    
    def backwards(self,x):
        # Faire reculer le moteur de x pas en parcourant la séquence d'alimentation en sens inverse
        StepCount = 8
        delay = 0.001
        Seq = self.seq_alim()
        self.setup()
        if x <= 13824:
            for i in range(x):
                for j in (range(StepCount-1, -1, -1)):
                    self.setStep(Seq[j][0], Seq[j][1], Seq[j][2], Seq[j][3])
                    time.sleep(delay)
        self.setStep(0,0,0,0)
        

class MyServer(BaseHTTPRequestHandler):     
        
    def do_GET(self):
        
        self.client_adress = ("0.0.0.0",80)
        self.moteur = stepmotor()
        self.send_response(200, "compris !")
        self.send_header("Content-type", "text")
        self.end_headers()
        #if self.requestline == "GET /up/wxyz HTTP/1.1":
        if (self.requestline[5:8] == "up/"):
            self.wfile.write(bytes("compris ! ", encoding = "ASCII"))
            f = self.LimiteNb(self.requestline, 7)
            n = int(self.requestline[8:f])
            self.moteur.forward(n)
        #elif self.requestline == "GET /down/wxyz HTTP/1.1":
        elif(self.requestline[5:10] == "down/"):
            self.wfile.write(bytes("compris ! ", encoding = "ASCII"))
            f = self.LimiteNb(self.requestline, 9)
            n = int(self.requestline[10:f])
            self.moteur.backwards(n)
        else:
            self.wfile.write(bytes("REQUETE INVALIDE", encoding = "ASCII"))
    
    def LimiteNb(self, txt, n):
        # déterminer la longueur du nombre en recherchant le premier et le dernier indice qu'il occupe
        index = n
        while txt[index] != " ":
            index = index + 1
        return index       

class GUI():
    def __init__(self):
        self.moteur = stepmotor()
        """
        self.ServerProcess = mp.Process(target = self.ServerUnlocked, args = ()) 
        
        self.hostName ="192.168.0.104" # Créagora
        #self.hostName ="192.168.1.34" # Domicile
        self.serverPort = 8080
        self.webServer = HTTPServer((self.hostName, self.serverPort), MyServer)
       """
        self.app = gz.App("Menu des commandes du dossier", layout = "grid")
        self.app.when_closed = self.stopSystem
        
        self.TextIG = gz.Text(self.app, "Commandes visuelles", grid= [0,0])
        self.steps = gz.TextBox(self.app, text = '512', grid = [0,1])
        self.boutonUp = gz.PushButton(self.app, text = "Lever le dossier",grid = [0,2])
        self.boutonDown = gz.PushButton(self.app, text = "Baisser le dossier", grid = [0,3])
              
        
        self.boutonUp.when_left_button_pressed = self.up
        self.boutonDown.when_left_button_pressed= self.down
       

    def launch(self): # pour le main
        #self.ServerProcess.start()
        self.app.display()
    
    def up(self):
        n = int(self.steps.tk.get())
        self.moteur.forward(n)
        
    def down(self):
        n = int(self.steps.tk.get())
        self.moteur.backwards(n)
    
    def ServerUnlocked(self):
        print("Server started http://%s:%s" % (self.hostName, self.serverPort))
        self.webServer.serve_forever()
   
    def stopSystem(self):
        self.app.hide()
        #self.ServerProcess.terminate()
        print("Server stopped.")
       # self.ServerProcess = mp.Process(target = self.ServerUnlocked, args = ()) 



        
    
if __name__ == "__main__":
    interface = GUI()
    interface.launch()