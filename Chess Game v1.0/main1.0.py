import pygame.locals
import random
import concurrent.futures
import threading
"""
As posições das peças estão na forma (0-7,0-7), mas o tabuleiro é 900x900 pixels
e tem umas borda de 50 pixels, portanto, como cada quadrado tem 100x100 pixels,
no pygame as posições estão na forma (50-850,50,850).

As funções "look" e "deslook" fazem aconversão de uma para outra.
"""
def look(posicao): #Convert (50-850,50-850) to (0-7,0-7)
    return (int((posicao[0] - 50)//100),int((posicao[1] - 50)//100))

def deslook(posicao):#Convert (0-7,0-7) to (50-850,50-850)
    return(posicao[0]*100 + 50,posicao[1]*100 + 50)

"""
Existe uma lista de peças no jogo, que possui todas as peças vivas.
Para ver se há uma peça em uma certa posição, pode-se usar a função
"get_peca", que retorna a peça ou uma lista vazia, se não há peça na posição
"""
def get_peca(posicao,listapeca):
    for peca in listapeca:
        if peca.pos == posicao:
            return peca
    return []
"""
Faz o cálculo da pontuação do tabuleiro para as peças pretas (que sempre é o bot)
cada peça tem o seu valor definido no __init__ da classe
"""
def pontuar(listapeca):
    soma = 0
    for i in listapeca:
        soma = soma + i.valor
    return soma


#Define a classe mãe das peças, que possui algumas funções básicas
class Peca():
    def blit_pos(self):
        return deslook(self.pos)

    """
A função "ver" atua sempre junto com a get_range(ver as classes das peças)
Ela serve para quebrar os loops quando a função get_range encontra uma outra peça,
de modo que uma torre preta não possa capturar outra peça preta ou que ela não "atropele"
outras peças, "pulando por cima" delas
    """
    def ver(self,a_,lista_):
        for p in lista_:
            if p.pos == a_:
                if p.cor == self.cor:
                    return (True,False) # (QUEBRAR O LOOP, PREENCHER A CASA "a")
                else:
                    return (True,True)
        return (False, True)
    """
Função para mover peças, removendo as peças capturadas da lista de peças

Se o rei branco é capturado, retorna (False,True)
Se o rei preto é capturado, retorna (True, False)
Se nenhum deles foi capturado, retorna (False,False)

Serve para detectar o fim de jogo e quem ganhou, além de mover as peças
    """
    def move(self,posicao,lista_peca):
        pos_anterior = self.pos
        self.vez_de_jogar = False
        peca_ant = get_peca(posicao,lista_peca)
        if peca_ant != []:
            lista_peca.remove(peca_ant)
        self.pos = (posicao)
        self.count = peca.count + 1

        #Roque
        if type(self) == Rei:
            if self.pos[0] - pos_anterior[0] == -2:
                torre = get_peca((pos_anterior[0] - 4,pos_anterior[1]),lista_peca)
                torre.move((self.pos[0] + 1,self.pos[1]),lista_peca)
            elif self.pos[0] - pos_anterior[0] == 2:
                torre = get_peca((pos_anterior[0] + 3,pos_anterior[1]),lista_peca)
                torre.move((self.pos[0] - 1,self.pos[1]),lista_peca)
                
        #Quando o peão chega à última casa
        if type(self) == Peao:
            if self.cor == 2:
                if self.pos[1] == 7:
                    rainha = Rainha(posicao,lista_peca,2)
                    lista_peca.remove(self)
            if self.cor == 1:
                if self.pos[1] == 0:
                    rainha = Rainha(posicao,lista_peca,1)
                    lista_peca.remove(self)
                    
        #Detecta se algum rei foi capturado
        if type(peca_ant) == Rei:
            if peca_ant.cor == 1:
                return (False,True)
            if peca_ant.cor == 2:
                return (True,False)
        return (False,False)

"""
Função que simula alguns turnos "imaginários" à partir de uma primeira jogada

Ela cria uma "lista_fake" idêntica à lista de peças original e trabalha com essa
lista para não alterar o tabuleiro original

Função retorna a pontuação do tabuleiro após "nturnos" turnos
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
Simula 200 jogos por 6 turnos para cada peça e retorna a melhor jogada
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
        #Usa o multithreading do python para acelerar o processamento
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = [executor.submit(simulate,pj,listapeca,6) for i in range(200)]
            for r in concurrent.futures.as_completed(results):
                soma = soma + r.result()
        media = soma/50
        pj.append(media)
    melhor = [(-1,-2),(-3,-4),-150] # pontuação arbitrária e impossível apenas para começar o "recorde"
    for pj in alcance:
        if pj[2] > melhor[2]:
            melhor = pj
    print("processamento terminado!")
    return [get_peca(melhor[0],listapeca),melhor[1]]
"""
Classe para o rei

Todas as peças recebem uma:
posição: tupla do tipo (0-7,0-7)
lista de peças (tabuleiro que será inserida)
cor: se for 1: peça é branca, se for 2: peça é preta

No __init__ das classes de peças, elas recebem:
Um count = 0, que indica quantas vezes elas já se moveram,
importante para o caso dos peões ou para fazer o roque
Um valor: cada classe tem seu valor, o rei vale 50.
Um blit = True, quando a peça não precisar ser mostrada, ele é alterado para False
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
            
    #Função ver adaptada para o rei, pois ele só anda uma casa
    def ver_rei(self,a_,listapeca_):
        for p in listapeca_:
            if p.pos == a_:
                if p.cor == self.cor:
                    return False
        return True

    #Todas as classes tem um get_range próprio, que retorna para onde elas podem jogar
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
        #Roque
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

#Classe para rainha
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

#Classe para torre
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

#Classe para bispo
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

#Classe para cavalo
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

#Classe para peão
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

#While que ficará aberto até que se feche a janela do pygame
while superjanela:

    #Definições de tela do pygame e de textos caso alguém ganhe
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
    "posmouse" é a posição do mouse quando o botão do mouse é clicado.
    Começa em (-300,-300) para não "confundir" o programa, dado que ele
    "precisa" saber onde está sendo clicado
    """
    posmouse = (-300,-300)
    
    #Se turno == True, é a vez das brancas
    turno = True

    #Organiza as peças no tabuleiro
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
    
    #Loop que roda até alguem ganhar o jogo
    while janelaaberta:
        posmouse = (-300,-300)
        """
rele e rele2 são condições associadas com a questão de troca da vez das peças de
jogar. Por exemplo, se eu clico em uma peça e depois clico em algum canto do tabuleiro,
Ele tira a vez daquela peça
        """
        rele = False
        rele2 = 0

        #Analisa os cliques da tela
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                janelaaberta = False
                superjanela = False
            if i.type == pygame.MOUSEBUTTONUP:
                posmouse = pygame.mouse.get_pos()

        #blita o tabuleiro e as peças depois
        tela.blit(fundo,(0,0))
        
        for peca in lista_peca:
            if peca.blit:
                tela.blit(peca.image,peca.blit_pos())
                
        if turno: 
            for peca in lista_peca:
                #vez_de_jogar == True quer dizer que o jogador clicou em uma peça branca
                if peca.vez_de_jogar:
                    rang = peca.get_range(lista_peca)
                    if rang == []:
                        continue
                    for i in rang:
                        #"fumaca" é o fundinho verde que fica nas posições possíveis de jogar
                        tela.blit(fumaca,(deslook(i)))
                        if look(posmouse) == i:
                            #Se as brancas capturam o rei preto: elas ganharam
                            brancas_ganharam = peca.move(i,lista_peca)[0]
                            turno = False
                            rele = True
                    if posmouse != (-300,-300) and look(posmouse) not in rang:
                        peca.vez_de_jogar = False
                    if rele:
                        peca.vez_de_jogar = False

            #Esquema para trocar qual peça vai jogar caso o jogador clique em outra peça
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
                            
        #Se "turno" é falso, pretas jogam
        else:
            possibilidades = []
            escolha = montecarlo(lista_peca)
            #Se elas capturaram o rei branco, elas ganham:
            pretas_ganharam = escolha[0].move(escolha[1],lista_peca)[1]
            turno = True

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
