import pygame.locals
import random
import concurrent.futures
import threading
"""
At this chess game, the player plays always with white pieces and
the bot always with black ones, for the sake of making programming less
laborius.


The pieces positions are in the form (0-7,0-7) in order to make it easier
to create loops with python's range().

Bu the board is actually 900x900 pixels and have a 50-pixels edge, which means that the positions
will have to be converted to a (50-850,50-850).

"""
def look(posicao): #Convert (50-850,50-850) to (0-7,0-7)
    return (int((posicao[0] - 50)//100),int((posicao[1] - 50)//100))

def deslook(posicao):#Convert (0-7,0-7) to (50-850,50-850)
    return(posicao[0]*100 + 50,posicao[1]*100 + 50)

"""Function that returns what piece is in a board position, from a list "listapeca"
that of pieces that are in the game"""
def get_peca(posicao,listapeca):
    for peca in listapeca:
        if peca.pos == posicao:
            return peca
    return []

def pontuar(listapeca):
    soma = 0
    for i in listapeca:
        soma = soma + i.valor
    return soma


#Defines a class for pieces, it will be the mother-class of the other classes
class Peca():
    def blit_pos(self):
        return (self.pos[0]*100 + 50,self.pos[1]*100 + 50)

    def ver(self,a_,lista_):
        for p in lista_:
            if p.pos == a_:
                if p.cor == self.cor:
                    return (True,False) # (QUEBRAR O LOOP, PREENCHER A CASA "a")
                else:
                    return (True,True)
        return (False, True)

    #Function for moving pieces
    def move(self,posicao,lista_peca):
        pos_anterior = self.pos
        self.vez_de_jogar = False
        peca_ant = get_peca(posicao,lista_peca)
        if peca_ant != []:
            lista_peca.remove(peca_ant)
        self.pos = (posicao)
        self.count = peca.count + 1

        #castling move
        if type(self) == Rei:
            if self.pos[0] - pos_anterior[0] == -2:
                torre = get_peca((pos_anterior[0] - 4,pos_anterior[1]),lista_peca)
                torre.move((self.pos[0] + 1,self.pos[1]),lista_peca)
            elif self.pos[0] - pos_anterior[0] == 2:
                torre = get_peca((pos_anterior[0] + 3,pos_anterior[1]),lista_peca)
                torre.move((self.pos[0] - 1,self.pos[1]),lista_peca)
                
        #At this game, the pawn transform automatically into a queen when reaching the edge of the board
        if type(self) == Peao:
            if self.cor == 2:
                if self.pos[1] == 7:
                    rainha = Rainha(posicao,lista_peca,2)
                    lista_peca.remove(self)
            if self.cor == 1:
                if self.pos[1] == 0:
                    rainha = Rainha(posicao,lista_peca,1)
                    lista_peca.remove(self)
                    
        #Detect if any king is dead
        if type(peca_ant) == Rei:
            if peca_ant.cor == 1:
                return (False,True)
            if peca_ant.cor == 2:
                return (True,False)
        return (False,False)

"""
This function simulates an "imaginary game" where:

primeira_jogada : the first play
listapeca : the list of pieces in game
nturnos : number of turns

In this simulation, the bot and the player play randomly, except for
when the king can be captured.

it returns the board score for the black pieces after "nturnos" turns.
The value of pieces are declared in their classes.
"""
def simulate(primeira_jogada,listapeca,nturnos): #primeira_jogada = [(pos1),(pos2)]
    lista_fake = []
    n = 0
    listadeposlistapeca = []
    for i in listapeca:
        listadeposlistapeca.append(i.pos)
    for i in listapeca:
        a = type(i)(i.pos,lista_fake,i.cor)

    turno = False
    """print(listadepos)
    print(listadeposlistapeca)
    print(get_peca(primeira_jogada[0],lista_fake))
    print(get_peca(primeira_jogada[0],listapeca))"""
    get_peca(primeira_jogada[0],lista_fake).move(primeira_jogada[1],lista_fake)
    while n < nturnos:
        if turno:
            possibilidades = []
            for peca in lista_fake:
                if peca.cor == 2:
                    rang = peca.get_range(lista_fake)
                    for i in rang:
                        possibilidades.append([peca,i])
            escolha = random.choice(possibilidades)
            for k in possibilidades:
                if type(get_peca(possibilidades[1],lista_fake)) == Rei:
                    escolha = k
            escolha[0].move(escolha[1],lista_fake)
            #print(str(type(escolha[0])) + str(escolha[1]))
            n = n + 1
            turno = False
        if not turno:
            possibilidades = []
            for peca in lista_fake:
                if peca.cor == 1:
                    rang = peca.get_range(lista_fake)
                    for i in rang:
                        possibilidades.append([peca,i])
            escolha = random.choice(possibilidades)
            for k in possibilidades:
                if type(get_peca(possibilidades[1],lista_fake)) == Rei:
                    escolha = k
            escolha[0].move(escolha[1],lista_fake)
            n = n + 1
            turno = True
    return pontuar(lista_fake)

"""
This function simulates 200 games for 6 turns for each possible play in the board,
then it gets the average of the board score for each possible play and choose the highest.

"""
def montecarlo(listapeca):
    print("processando...")
    alcance = []
    for peca in listapeca:
        if peca.cor == 2:
            rang = peca.get_range(listapeca)
            for i in rang:
                alcance.append([peca.pos,i])
    for pj in alcance:
        soma = 0
        listathreads = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = [executor.submit(simulate,pj,listapeca,6) for i in range(200)]
            for r in concurrent.futures.as_completed(results):
                soma = soma + r.result()
        media = soma/50
        pj.append(media)
    melhor = [(-1,-2),(-3,-4),-150]
    for pj in alcance:
        if pj[2] > melhor[2]:
            melhor = pj
    print("processamento terminado!")
    return [get_peca(melhor[0],listapeca),melhor[1]]
"""
Class for king

the pieces recieves:
a postion "pos" (tuple)
a list "lista_peca" (list)
a color "cor" (int) : if cor == 1: the piece is white
                    : if cor == 2: the piece is black
"""
class Rei(Peca):
    def __init__(self,pos,lista_peca,cor):
        self.count = 0
        self.valor = 50
        self.pos = pos
        lista_peca.append(self)
        self.blit = True
        self.cor = cor
        self.vez_de_jogar = False
        if cor  == 1:
            self.image = pygame.image.load("rei branco.png")
            self.valor = -self.valor
        if cor == 2:
            self.image = pygame.image.load("rei preto.png")

    def ver_rei(self,a_,listapeca_):
        for p in listapeca_:
            if p.pos == a_:
                if p.cor == self.cor:
                    return False
        return True

    #The get_range function id defined for all pieces class
    #It returns all the positions this piece can move in the moment it is called
    def get_range(self,listapeca):
        lista = []
        for i in range(-1,2):
            a = (self.pos[0] + i,self.pos[1] - 1)
            if not a[0] < 0 and not a[0] > 7:
                if not a[1] < 0 and not a[1] > 7:
                    if self.ver_rei(a,listapeca):
                        lista.append(a)
                        
        for i in range(-1,2):
            a = (self.pos[0] + i,self.pos[1] + 1)
            if not a[0] < 0 and not a[0] > 7:
                if not a[1] < 0 and not a[1] > 7:
                    if self.ver_rei(a,listapeca):
                        lista.append(a)

        a = (self.pos[0] - 1,self.pos[1])
        if not a[0] < 0 and not a[0] > 7:
            if not a[1] < 0 and not a[1] > 7:
                    if self.ver_rei(a,listapeca):
                        lista.append(a)
                        
        a = (self.pos[0] + 1,self.pos[1])
        if not a[0] < 0 and not a[0] > 7:
            if not a[1] < 0 and not a[1] > 7:
                    if self.ver_rei(a,listapeca):
                        lista.append(a)
        if self.count == 0:
            peca1 = get_peca((self.pos[0] + 3,self.pos[1]),listapeca)
            peca2 = get_peca((self.pos[0] - 4,self.pos[1]),listapeca)
            if type(peca1) == Torre:
                if peca1.count == 0 and peca1.cor == self.cor:
                    if get_peca((self.pos[0] + 1,self.pos[1]),listapeca) == [] and get_peca((self.pos[0] + 2,self.pos[1]),listapeca) == []:
                        lista.append((self.pos[0] + 2,self.pos[1]))
            if type(peca2) == Torre:
                if peca2.count == 0 and peca2.cor == self.cor:
                    if get_peca((self.pos[0] -1,self.pos[1]),listapeca) == [] and get_peca((self.pos[0] -2,self.pos[1]),listapeca) == [] and get_peca((self.pos[0] -3,self.pos[1]),listapeca) == []:
                        lista.append((self.pos[0] - 2,self.pos[1]))
        return lista

#Class for queen
class Rainha(Peca):
    def __init__(self,pos,lista_peca,cor):
        self.count = 0
        self.valor = 9
        self.pos = pos
        lista_peca.append(self)
        self.blit = True
        self.cor = cor
        self.vez_de_jogar = False
        if cor  == 1:
            self.image = pygame.image.load("rainha branca.png")
            self.valor = -self.valor
        if cor == 2:
            self.image = pygame.image.load("rainha preta.png")

    def get_range(self,listapeca):
        lista = []
        
        x = self.pos[0]
        y = self.pos[1]
        while x < 7:
            a = (x + 1,y)
            brk = False
            cond = self.ver(a,lista_peca)
            brk = cond[0]
            if cond[1]:
                lista.append(a)
            if brk:
                break
            x = x + 1
            
        x = self.pos[0]
        y = self.pos[1]
        while x > 0:
            a = (x - 1,y)
            brk = False
            cond = self.ver(a,lista_peca)
            brk = cond[0]
            if cond[1]:
                lista.append(a)
            if brk:
                break
            x = x - 1
            
        x = self.pos[0]
        y = self.pos[1]
        while y < 7:
            a = (x,y + 1)
            brk = False
            cond = self.ver(a,lista_peca)
            brk = cond[0]
            if cond[1]:
                lista.append(a)
            if brk:
                break
            y = y + 1
            
        x = self.pos[0]
        y = self.pos[1]
        while y > 0:
            a = (x,y - 1)
            brk = False
            cond = self.ver(a,lista_peca)
            brk = cond[0]
            if cond[1]:
                lista.append(a)
            if brk:
                break
            y = y - 1
            
        x = self.pos[0]
        y = self.pos[1]
        while x < 7 and y < 7:
            a = (x + 1,y + 1)
            brk = False
            cond = self.ver(a,lista_peca)
            brk = cond[0]
            if cond[1]:
                lista.append(a)
            if brk:
                break
            x = x + 1
            y = y + 1
            
        x = self.pos[0]
        y = self.pos[1]
        while x > 0 and y < 7:
            a = (x - 1,y + 1)
            brk = False
            cond = self.ver(a,lista_peca)
            brk = cond[0]
            if cond[1]:
                lista.append(a)
            if brk:
                break
            x = x - 1
            y = y + 1
            
        x = self.pos[0]
        y = self.pos[1]
        while x > 0 and y > 0:
            a = (x - 1,y - 1)
            brk = False
            cond = self.ver(a,lista_peca)
            brk = cond[0]
            if cond[1]:
                lista.append(a)
            if brk:
                break
            x = x - 1
            y = y - 1
            
        x = self.pos[0]
        y = self.pos[1]
        while x < 7 and y > 0:
            a = (x + 1,y - 1)
            brk = False
            cond = self.ver(a,lista_peca)
            brk = cond[0]
            if cond[1]:
                lista.append(a)
            if brk:
                break
            x = x + 1
            y = y - 1
            
        return lista

#Class for tower
class Torre(Peca):
    def __init__(self,pos,lista_peca,cor):
        self.valor = 5
        self.count = 0
        self.pos = pos
        lista_peca.append(self)
        self.blit = True
        self.cor = cor
        self.vez_de_jogar = False
        if cor  == 1:
            self.image = pygame.image.load("torre branca.png")
            self.valor = -self.valor
        if cor == 2:
            self.image = pygame.image.load("torre preta.png")

    def get_range(self,listapeca):
        lista = []
        
        x = self.pos[0]
        y = self.pos[1]
        while x < 7:
            a = (x + 1,y)
            brk = False
            cond = self.ver(a,lista_peca)
            brk = cond[0]
            if cond[1]:
                lista.append(a)
            if brk:
                break
            x = x + 1
            
        x = self.pos[0]
        y = self.pos[1]
        while x > 0:
            a = (x - 1,y)
            brk = False
            cond = self.ver(a,lista_peca)
            brk = cond[0]
            if cond[1]:
                lista.append(a)
            if brk:
                break
            x = x - 1
            
        x = self.pos[0]
        y = self.pos[1]
        while y < 7:
            a = (x,y + 1)
            brk = False
            cond = self.ver(a,lista_peca)
            brk = cond[0]
            if cond[1]:
                lista.append(a)
            if brk:
                break
            y = y + 1
            
        x = self.pos[0]
        y = self.pos[1]
        while y > 0:
            a = (x,y - 1)
            brk = False
            cond = self.ver(a,lista_peca)
            brk = cond[0]
            if cond[1]:
                lista.append(a)
            if brk:
                break
            y = y - 1

        return lista

#Class for bishop
class Bispo(Peca):
    def __init__(self,pos,lista_peca,cor):
        self.valor = 3
        self.count = 0
        self.pos = pos
        lista_peca.append(self)
        self.blit = True
        self.cor = cor
        self.vez_de_jogar = False
        if cor  == 1:
            self.image = pygame.image.load("bispo branco.png")
            self.valor = -self.valor
        if cor == 2:
            self.image = pygame.image.load("bispo preto.png")

    def get_range(self,listapeca):
        lista = []
        x = self.pos[0]
        y = self.pos[1]
        
        while x < 7 and y < 7:
            a = (x + 1,y + 1)
            brk = False
            cond = self.ver(a,lista_peca)
            brk = cond[0]
            if cond[1]:
                lista.append(a)
            if brk:
                break
            x = x + 1
            y = y + 1
            
        x = self.pos[0]
        y = self.pos[1]
        while x > 0 and y < 7:
            a = (x - 1,y + 1)
            brk = False
            cond = self.ver(a,lista_peca)
            brk = cond[0]
            if cond[1]:
                lista.append(a)
            if brk:
                break
            x = x - 1
            y = y + 1
            
        x = self.pos[0]
        y = self.pos[1]
        while x > 0 and y > 0:
            a = (x - 1,y - 1)
            brk = False
            cond = self.ver(a,lista_peca)
            brk = cond[0]
            if cond[1]:
                lista.append(a)
            if brk:
                break
            x = x - 1
            y = y - 1
            
        x = self.pos[0]
        y = self.pos[1]
        while x < 7 and y > 0:
            a = (x + 1,y - 1)
            brk = False
            cond = self.ver(a,lista_peca)
            brk = cond[0]
            if cond[1]:
                lista.append(a)
            if brk:
                break
            x = x + 1
            y = y - 1

        return lista

#Class for horse
class Cavalo(Peca):
    def __init__(self,pos,lista_peca,cor):
        self.valor = 3
        self.count = 0
        self.pos = pos
        lista_peca.append(self)
        self.blit = True
        self.cor = cor
        self.vez_de_jogar = False
        if cor  == 1:
            self.image = pygame.image.load("cavalo branco.png")
            self.valor = -self.valor
        if cor == 2:
            self.image = pygame.image.load("cavalo preto.png")

    def get_range(self,listapeca):
        ref = [[1,2],[1,-2],[-1,2],[-1,-2],[2,1],[2,-1],[-2,1],[-2,-1]]
        lista = []
        for i in ref:
            x = self.pos[0]
            y = self.pos[1]
            a = (x + i[0],y + i[1])
            if 0 <= a[0] <= 7 and 0 <= a[1] <= 7:
                ver_cavalo = self.ver(a,listapeca) #(cont loop, adotar a)
                if ver_cavalo[1]:
                    lista.append(a)
        return lista

#Class for pawn
class Peao(Peca):
    def __init__(self,pos,lista_peca,cor):
        self.valor = 1
        self.count = 0
        self.pos = pos
        lista_peca.append(self)
        self.blit = True
        self.cor = cor
        self.vez_de_jogar = False
        if cor  == 1:
            self.image = pygame.image.load("peao branco.png")
            self.valor = -self.valor
        if cor == 2:
            self.image = pygame.image.load("peao preto.png")

    def get_range(self,listapeca):
        dont_append_c = False
        dont_append_d = False
        lista = []
        x = self.pos[0]
        y = self.pos[1]
        if self.cor == 2:
            a = (self.pos[0] - 1,self.pos[1] + 1)
            b = (self.pos[0] + 1,self.pos[1] + 1)
            c = (self.pos[0],self.pos[1] + 1)
            d = (self.pos[0],self.pos[1] + 2)
            for peca in listapeca:
                if peca.pos == a:
                    if peca.cor == 1:
                        lista.append(a)
                if peca.pos == b:
                    if peca.cor == 1:
                        lista.append(b)
                if peca.pos == c:
                    dont_append_c = True
                if peca.pos == d:
                    dont_append_d = True
            if not dont_append_c:
                lista.append(c)
            if not dont_append_d:
                if self.count == 0:
                    lista.append(d)
            return lista
        if self.cor == 1:
            a = (self.pos[0] - 1,self.pos[1] - 1)
            b = (self.pos[0] + 1,self.pos[1] - 1)
            c = (self.pos[0],self.pos[1] - 1)
            d = (self.pos[0],self.pos[1] - 2)
            for peca in listapeca:
                if peca.pos == a:
                    if peca.cor == 2:
                        lista.append(a)
                if peca.pos == b:
                    if peca.cor == 2:
                        lista.append(b)
                if peca.pos == c:
                    dont_append_c = True
                if peca.pos == d:
                    dont_append_d = True
            if not dont_append_c:
                lista.append(c)
            if not dont_append_d:
                if self.count == 0:
                    lista.append(d)
            return lista

pygame.init()
superjanela = True

#This loop is ended only when the game window is closed
while superjanela:

    #Some pygame definitions
    tela = pygame.display.set_mode((900,900))
    pygame.display.set_caption("Projeto Xadrez")
    fundo = pygame.image.load("tabuleiro.png")
    fumaca = pygame.image.load("fumaca.png")

    font = pygame.font.Font("freesansbold.ttf",36)

    textbrancas = font.render("Brancas Ganharam",True,(150,150,150),(0,0,0))
    textbrancas_rect = textbrancas.get_rect()
    textbrancas_rect.center = (450,450)

    textpretas = font.render("Pretas Ganharam",True,(150,150,150),(0,0,0))
    textpretas_rect = textpretas.get_rect()
    textpretas_rect.center = (450,300)

    texto_abaixo = font.render("Clique em qualquer ponto para reiniciar",True,(150,150,150),(0,0,0))
    texto_abaixo_rect = texto_abaixo.get_rect()
    texto_abaixo_rect.center = (450,600)


    janelaaberta = True
    lista_peca = []
    
    """"
    "posmouse" represents where is the mouse position when there is a mouse button up
    It starts in a random negative position in order to don't activate nothing if
    none mouse button has been pressed and up
    """
    posmouse = (-300,-300)
    
    #if "turno" is true, it is the white turn of play
    turno = True

    #Organization of the pieces over the board
    for i in range(2):
        torre = Torre((0,7 - 7*i),lista_peca,i +1)
        torre = Torre((7,7 - 7*i),lista_peca,i +1)
    for i in range(2):
        cavalo = Cavalo((1,7 - 7*i),lista_peca,i +1)
        cavalo = Cavalo((6,7 - 7*i),lista_peca,i +1)
    for i in range(2):
        bispo = Bispo((2,7 - 7*i),lista_peca,i +1)
        bispo = Bispo((5,7 - 7*i),lista_peca,i +1)
    for i in range(2):
        rainha = Rainha((3,7 - 7*i),lista_peca,i + 1)
    for i in range(2):
        rei = Rei((4,7 - 7*i),lista_peca,i + 1)
    for i in range(8):
        peao = Peao((i,6),lista_peca,1)
    for i in range(8):
        peao = Peao((i,1),lista_peca,2)

    brancas_ganharam = False
    pretas_ganharam = False
    
    #This loop is ended if someone wins the game
    while janelaaberta:
        posmouse = (-300,-300)
        rele = False
        rele2 = 0
        
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                janelaaberta = False
                superjanela = False
            if i.type == pygame.MOUSEBUTTONUP:
                posmouse = pygame.mouse.get_pos()
                
        tela.blit(fundo,(0,0))
        
        for peca in lista_peca:
            if peca.blit:
                tela.blit(peca.image,peca.blit_pos())
                
        if turno: 
            for peca in lista_peca:
                #vez_de_jogar == True means that the player clicked over the piece
                if peca.vez_de_jogar:
                    rang = peca.get_range(lista_peca)
                    if rang == []:
                        continue
                    for i in rang:
                        #"fumaca" is the green spot for positions the player can move the pieces
                        tela.blit(fumaca,(deslook(i)))
                        if look(posmouse) == i:
                            brancas_ganharam = peca.move(i,lista_peca)[0]
                            turno = False
                            rele = True
                    if posmouse != (-300,-300) and look(posmouse) not in rang:
                        peca.vez_de_jogar = False
                    if rele:
                        peca.vez_de_jogar = False

            #Scheme for changing the selected piece if another is selected
            for peca in lista_peca:

                if peca.cor == 1:
                    if look(posmouse) == peca.pos and not rele:
                        for peca2 in lista_peca:
                            if peca2 != peca:
                                if peca2.vez_de_jogar:
                                    peca2.vez_de_jogar = False
                        if peca.vez_de_jogar == False:
                            peca.vez_de_jogar = True
                        else:
                            peca.vez_de_jogar = False
                            
        #"turno" is false, so bot is playing
        else:
            possibilidades = []
            escolha = montecarlo(lista_peca)
            pretas_ganharam = escolha[0].move(escolha[1],lista_peca)[1]
            turno = True

        #If the black ones won:
        if pretas_ganharam:
            tela.blit(textpretas,textpretas_rect)
            tela.blit(texto_abaixo,texto_abaixo_rect)
            pygame. display.update()
            while True:
                x = False
                for i in pygame.event.get():
                    if i.type == pygame.MOUSEBUTTONUP:
                        x = True
                    if i.type == pygame.QUIT:
                        pygame.quit()
                if x:
                    break
            janelaaberta = False
            
        #If the white ones won:
        if brancas_ganharam:
            tela.blit(textbrancas,textbrancas_rect)
            tela.blit(texto_abaixo,texto_abaixo_rect)
            pygame.display.update()
            while True:
                x = False
                for i in pygame.event.get():
                    if i.type == pygame.MOUSEBUTTONUP:
                        x = True
                    if i.type == pygame.QUIT:
                        pygame.quit()
                if x:
                    break
            janelaaberta = False
        pygame.display.update()

pygame.quit()
