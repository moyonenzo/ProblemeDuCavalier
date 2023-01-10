from tkinter import *
import asyncio
import time
import math

def run_in_background(f):
    """
    description : permet d'executer la fonction associé de manière asynchrone
    """
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, **kwargs)
    return wrapped

class PLATEAU:
    """
    description : plateau d'echec de x*x cases répondant au problème parcours du cavalier.
    """
    def __init__(self,size):
        """
        description : initialise les attributs nécessaires et lance le jeu
        entrée : taille du plateau
        """
        self.w,self.h=600,600
        self.size = size

        self.root = Tk()
        self.root.geometry("{}x{}".format(self.w,self.h))
        self.root.resizable(False, False)

        colors = ["black","white"]
        color=1

        self.root.title('Problème du cavalier ({}x{})'.format(size,size))

        self.frame_list = []
        self.Jouer()

        self.root.mainloop()

    @run_in_background
    def DrawTravel(self,path):
        """
        description : affiche sur l'interface le chemin d'une solution
        entrée : liste de listes comportant des frames tkinter
        """
        i = 0
        for case in path:
            canvas = None
            
            if case == path[0]:
                canvas = Canvas(case,width=self.w//self.size,height=self.h//self.size, bg = "light green")
            elif case == path[-1]:
                canvas = Canvas(case,width=self.w//self.size,height=self.h//self.size, bg = "light blue")
            elif case["bg"] == "white":
                canvas = Canvas(case,width=self.w//self.size,height=self.h//self.size, bg = "#DADADA")
            elif case["bg"] == "black":
                canvas = Canvas(case,width=self.w//self.size,height=self.h//self.size, bg = "gray")

            canvas.create_text ( (self.w//self.size)//2 , (self.h//self.size)//2 , text = str(i), font=("Courier", 18, "italic"))
            canvas.place(x=-2,y=-2)
            i+=1

            time.sleep(.5)

        self.root.geometry("{}x{}".format(self.w,self.h + 50))
        self.replay_button = Button(self.root, text="rejouer", command=self.Jouer)
        self.replay_button.place(x = 275, y = 610)

    def Jouer(self):
        """
        description : crée le plateau de jeu
        """
        self.root.geometry("{}x{}".format(self.w,self.h))
        self.root.title('Problème du cavalier ({}x{})'.format(self.size,self.size))
        
        if self.frame_list != []:
            for row in self.frame_list:
                for case in row:
                    case.destroy()

        colors = ["black","white"]
        color=1

        self.frame_list = []
        for row in range(self.size):
            self.frame_list.append([])
            for column in range(self.size):
                frame = Frame(self.root,width=self.w//self.size,height=self.h//self.size, bg=colors[color])
                frame.grid(row=row,column=column)
                frame.bind("<Button-1>",self.OnClick)

                self.frame_list[row].append(frame)

                if color==0: color=1
                else: color=0
            
            if self.size%2 == 0:
                if color==0: color=1
                else: color=0

    def OnClick(self,event):
        """
        description : se déclenche lors d'un clic sur une case et organise l'execution des taches répondant au problème
        entrée : informations sur la case cliquée
        """
        for row in self.frame_list:
            for frame in row:
                frame.unbind("<Button-1>")

        graphe = self.CreateGraphe(self.frame_list)

        self.root.title("Problème du cavalier ({}x{}) | Recherche d'une solution".format(self.size,self.size))
        try:
            chemin =  self.parcours(graphe,event.widget)
        except IndexError:
            self.root.title('Problème du cavalier ({}x{}) | Aucune solution trouvée'.format(self.size,self.size))
            
            self.root.geometry("{}x{}".format(self.w,self.h + 50))
            self.replay_button = Button(self.root, text="rejouer", command=self.Jouer)
            self.replay_button.place(x = 275, y = 610)
            return
        
        
        self.root.title('Problème du cavalier ({}x{}) | Solution trouvée'.format(self.size,self.size))
        self.DrawTravel(chemin)

    def GetFrameCoords(self,frames,frame):
        """
        description : renvoie les coordonnées (x,y) d'une frame tkinter dans la liste <frames>
        entrée : liste de listes comportant des frames tkinter, frame tkinter
        sortie : tuple de coordonées
        """
        for row in frames:
            if frame in row:
                return (frames.index(row),row.index(frame)) 

    def GetCoordsFrame(self,frames,coords):
        """
        description : renvoie la frame correspondante aux coordonées dans la liste <frames>
        entrée : liste de listes comportant des frames tkinter, tuple de coordonées
        sortie : frame tkinter
        """
        y,x = coords
        return frames[y][x]

    def GetPossibleMoves(self,coords):
        """
        description : calcule et renvoie les différents mouvements possibles a partie de la position <coords> entrée
        entrée : tuple de coordonnées
        sortie : liste des mouvements possibles a partir de la position entrée
        """
        yI,xI = coords[0],coords[1]
            
        all_p = [(yI-2,xI+1),(yI-2,xI-1),(yI+2,xI+1),(yI+2,xI-1),(yI-1,xI+2),(yI-1,xI-2),(yI+1,xI+2),(yI+1,xI-2)]
        possibilitys = []
            
        for p in all_p:
            if p[0] >= 0 and p[1] >= 0 and p[0] <= self.size-1 and p[1] <= self.size-1:
                possibilitys.append(p)
        return possibilitys

    def CreateGraphe(self,frames):
        """
        description : crée le graphe correspondant au plateau d'echec par rapport aux mouvements d'un cavalier
        entrée : liste de listes comportant des frames tkinter
        sortie : dictionnaire correspondant a un graphe
        """
        G = {}
        for row in frames:
            for frame in row:
                moves = self.GetPossibleMoves(self.GetFrameCoords(frames,frame))
                G[frame] = [self.GetCoordsFrame(frames,coords) for coords in moves]
        return G

    def parcours(self,G,racine):
        """
        description : recherche et renvoie le parcours pour lequel, avec le déplacement d'un cavalier, toutes les cases d'un plateau sont parcourus une et une seule fois
        entrée : dictionnaire correspondant a un graphe, racine du graphe
        sortie : liste correspondant à un parcours
        """
        visites = {racine:[]}
        file = [racine]
        while len(file) < len(G):
            max_voisins = (None,math.inf)
            for som in G[racine]:
                if ( som not in visites ) and ( som not in visites[racine] ):
                    if len(G[som]) < max_voisins[1]:
                        max_voisins = (som,len(G[som]))             
            
            if max_voisins[0] != None:
                visites[racine].append(max_voisins[0])
                visites[max_voisins[0]] = []
                file.append(max_voisins[0])
                racine = max_voisins[0]
            else:
                r = file.pop()
                visites.pop(r)
                racine = file[-1]
        return file

class HOME:
    """
    description : menu principal permettant de configurer la taille du plateau et de lancer la partie
    """
    def __init__(self):
        """
        description : crée le menu
        """
        w,h=400,200

        root = Tk()
        root.geometry(f"{w}x{h}")
        root.resizable(False, False)
        root.title("Problème Du Cavalier | Menu Principal")

        #

        canvas = Canvas(root,width=500,height=75)
        canvas.pack()
        canvas.create_text ( w//2 , 50 , text = "Problème Du Cavalier", font=("Courier", 18, "bold"))

        size_entry = Entry(root, width=30)
        size_entry.insert(0, 'Taille du plateau') # placeholder
        size_entry.pack(pady=5)

        def start():
            """
            description : vérifie la valeur entrée et ouvre la fenetre de jeu si valide
            """
            try:
                if int(size_entry.get()) >= 3:  
                    plateau = PLATEAU(int(size_entry.get()))
            except:
                ...

        start_button = Button(root, text="START", command=start)
        start_button.pack(pady=20)

        #

        root.mainloop()

if __name__ == "__main__":
    HOME()