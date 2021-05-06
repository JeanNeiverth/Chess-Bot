# Chess-Bot
Um jogo de Xadrez jogado por um jogador contra um bot que usa a estratégia de Monte Carlo.

![Capturar](https://user-images.githubusercontent.com/79885562/117321868-e14f5480-ae63-11eb-88d1-f0cb6cea5ee6.JPG)

Peculiaridades desse jogo em relação ao xadrez tradicional:

Para deixar a programação menos trabalhosa, alguns detalhes foram deixados de lado.

1. O jogador sempre está com as peças brancas e o bot, com as pretas;
2. Quando um peão chega ao fim do tabuleiro, ele automaticamente se transforma em uma rainha, ao invés de dar a possibilidade de escolha de qualquer peça;
3. Não existe a jogada em que um peão captura outro "en passant".


Sobre a estratégia de Monte Carlo:

No xadrez, é possível fazer um cálculo da pontuação do tabuleiro, onde cada tipo de peça vale uma certa quantia de pontos. No nosso caso, a pontuação se dá da seguinte forma:

Peão: 1 ponto
Bispo: 3 pontos
Cavalo: 3 pontos
Torre: 5 pontos
Rainha: 9 pontos
Rei: 50 pontos
OBS: normalmente não se atribui pontos ao Rei, porque quando ele morre, o jogo acaba. Mas nesse caso é um pouco diferente e logo isso será melhor explicado.

A estratégia consiste no seguinte: quando é a vez do bot, ele observa todas as possibilidades de jogadas que ele pode fazer. Para cada jogada, ele simula 200 jogos imaginários por 6 turnos à frente. Nesses jogos imaginários, ele supõe que o jogador E ELE jogarão aleatoriamente, exceto pela ocasião onde se pode capturar o rei.
Ao fim de cada "jogo imaginário", ele coleta a pontuação do tabuleiro. Ao fim dos 200 jogos imaginários (de uma possível jogada), ele faz a média das pontuações obtidas. Ao final, ele escolhe qual jogada possui a melhor média de pontos.

É um pouco contraintuitivo pensar que ele chegará em uma boa resposta com jogos aleatórios, mas um grande número de jogadas garante uma tendência estatística consideravelmente precisa, que é onde está o coração dessa estratégia.

Sobre o rei valer 50 pontos: teoricamente, a pontuação do tabuleiro quando o rei inimigo é capturado deveria ser infinita, pois é o máximo onde se pode chegar. Mas isso iria bagunçar a matemática da média, então foi mais conveniente dar um valor alto ao rei e deixar ele continuar jogando mesmo com o rei capturado (apenas nos jogos imaginários, claro).


Resultados:
Ele é razoavelmente "inteligente", exceto pelo fato de algumas jogadas agressivas "bobas" que ele faz.
Por exemplo:
![Capturar2](https://user-images.githubusercontent.com/79885562/117328592-28404880-ae6a-11eb-997e-f60dabea9b31.JPG)

Após movimentar a rainha para onde ela está, ele entendeu que a melhor jogada foi avançar o peão pra frente, apesar de eu poder simplesmente capturá-lo com a rainha.Faz sentido, porque, para ele, eu tenho algo próximo de 1 em 20 de chance de capturar o peão, quando, na verdade, essa chance é de quase 100%.

Algo interessante a se pensar é "por que ele não avançou com o peão da torre pra cima da rainha?". Acredito que isso aconteceu porque 200 partidas ainda é uma amostragem não suficiente. Se em 1 em cada 20 partidas a rainha captura o peão, teríamos 10 jogos imaginários onde isso aconteceria, o que quer dizer que ele teria 10 jogos para montar uma estatística sobre a chance de a torre dele capturar a rainha de volta, o que não retorna algo preciso.

Por uma questão de processamento, falta de otimização, demora e paciência do jogador, 200 jogos imaginários é um número "ideal", já que não valeria a pena ter um bot que jogasse um pouco melhor mas que demorasse 2 minutos para isso. O tempo atual de resposta dele é de mais ou menos 15 segundos.


