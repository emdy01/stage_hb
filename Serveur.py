# Le programme Serveur est le serveur http pilotant le moteur en réponse à des requetes http
#
# Principes généraux
# - initialisation
#       Lecture des paramètres
#       initilisation du serveur
# - nouvelle architecture modulaire
# - Parsing des requests http
# - robustesse si parametres ko
# - logging
# - echanges en html pas en texte
# - tests aux limites
# - sécurité
# - versionning du code GIT


# Modules nécessaires
from http.server import BaseHTTPRequestHandler, HTTPServer
import sys
import json
import getopt

class MyServer(BaseHTTPRequestHandler):
    def _set_headers(self,httpcode):
        self.send_response(httpcode)                            # 200 pour ok 400 pour erreur 
        self.send_header('Content-type', 'application/json')    # format du retour en json
        self.end_headers()

    def usageApi(self):
        self._set_headers(200)
        output=json.dumps({ 'usage' : "/status pour statut du serveur, /up/n pour lever dossier, /down/n pour baisser dossier"})
        self.wfile.write(output.encode())   

    def usage():
        print("-p ou --port indique le port d'écoute (8080 par defaut)")
        print("--hostname indique le nom de host d'écoute ('' par defaut)")
        print("-h ou --help imprime ce message")

    def do_GET(self):
        global g_position, MAX_POSITION, MIN_POSITION
        pathList=self.path.strip('/').split('/') #decoupe le path de l'url dans une liste en supprimant les / des extrémités
        if len(pathList)==1:
            if pathList[0]=='':
                self.usageApi()
            else:
                if pathList[0] == "status":
                    output=json.dumps({'serveur': 'ok', 'position': str(g_position)})    
                    self._set_headers(200)
                    self.wfile.write(output.encode())
                else:
                    self._set_headers(400)
                    output=json.dumps({'msg': 'commande invalide', 'position': str(g_position)})
                    self.wfile.write(output.encode())
                    self.log_error("commande invalide")
        else:
            if len(pathList) != 2 :
                self._set_headers(400)
                output=json.dumps({'msg': 'commande invalide 2 arguments attendus', 'order': pathList, 'position': str(g_position)})
                self.wfile.write(output.encode())
                self.log_error("commande invalide 2 arguments attendus")
            else:
                commande=pathList[0]
                step=pathList[1]
                if commande == "up" or  commande == "down" :    
                    if step.isnumeric():     # si le pas demandé est bien un numerique
                        n=int(step)
                        if (n > 0):
                            if commande == "up":
                                if g_position + n > MAX_POSITION :        # si on dépasse le max on va a max
                                    n = MAX_POSITION-g_position
                                    g_position = MAX_POSITION
                                    self.log_message("self.moteur.forward("+str(n)+") MAX_POSITION atteint")  
                                    msg="leve de "+str(n)+" MAX_POSITION atteint"
                                else :
                                    g_position += n
                                    self.log_message("self.moteur.forward("+str(n)+")")  
                                    msg="leve de "+str(n)
                                #self.moteur.forward(n)  
                            elif  commande == "down":
                                if g_position - n < MIN_POSITION :        # si on dépasse le min on va a min
                                    n = g_position - MIN_POSITION
                                    g_position = MIN_POSITION
                                    self.log_message("self.moteur.backward("+str(n)+") MIN_POSITION atteint")  
                                    msg="baisse de "+str(n)+" MIN_POSITION atteint"
                                else :
                                    g_position -= n
                                    self.log_message("self.moteur.backward("+str(n)+")") 
                                    msg="baisse de "+str(n)
                                #self.moteur.backwards(n)

                            self._set_headers(200)
                            output=json.dumps({'msg': msg,'commande': commande, 'step': step, 'position': str(g_position)})
                            self.wfile.write(output.encode())
                        else :
                            self._set_headers(400)
                            output=json.dumps({'msg': 'pas du moteur invalide', 'order': commande, 'step': step, 'position': str(g_position)})
                            self.wfile.write(output.encode())
                            self.log_error("pas du moteur invalide")
                    else:
                        self._set_headers(400)
                        output=json.dumps({'msg': 'pas du moteur non numerique', 'order': commande, 'step': step, 'position': str(g_position)})
                        self.wfile.write(output.encode())
                        self.log_error("pas du moteur non numerique")
                else:
                    self._set_headers(400)
                    output=json.dumps({'msg': 'commande invalide', 'order': commande, 'step': step, 'position': str(g_position)})
                    self.wfile.write(output.encode())
                    self.log_error("commande invalide")



if __name__ == "__main__":
    serverPort = 8080           #port par defaut
    hostName =""                #host d'écoute par default
    g_position = 0              #position du lit, on considère que le lit est à la position 0 au depart
                                #Procédure d'initialisation de la position du lit à 0avec un capteur à implémenter 
    MAX_POSITION = 13824        #position max du dossier - valeur experimentale mesurée
    MIN_POSITION = 0            #position min du dossier


    try:                                
        opts, args = getopt.getopt(sys.argv[1:], "h:p:", ["help","port=","hostname="])  #le programme supporte 3 paramètres : -h ou --help  -p ou --port et hostname
    except getopt.GetoptError:          
        usage()                         
        sys.exit(2)                     
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()                     
            sys.exit()                     
        elif opt in ("-p", "--port"):
            if arg.isnumeric() :
                serverPort = int(arg)             
            else :
                print("port doit etre numerique, valeur par defaut prise")
        elif opt in ("--hostname"):
            hostName = arg               
    print("Server starting http://%s:%s" % (hostName, serverPort))
    webServer = HTTPServer((hostName, serverPort), MyServer)
    webServer.serve_forever()