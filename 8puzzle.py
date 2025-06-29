import random
import copy
from collections import deque
import heapq

# ------------------------------------------
# Olá! Sou a Amanda e nessa primeira parte do trabalho meu código implementa Busca em Largura, Busca em Profundidade e Custo Uniforme.
# ------------------------------------------

# Estado objetivo padrão do 8-Puzzle
GOAL = [1, 2, 3, 4, 5, 6, 7, 8, 0]

# Função que retorna apenas estados solúveis
def estado_soluvel(estado):
    inversoes = 0
    lista = [x for x in estado if x != 0]
    for i in range(len(lista)):
        for j in range(i+1, len(lista)):
            if lista[i] > lista[j]:
                inversoes += 1
    return inversoes % 2 == 0

# Função para gerar um estado inicial aleatório
def gerar_estado_inicial():
    estado = list(range(9))
    random.shuffle(estado)

    while not estado_soluvel(estado):
        random.shuffle(estado)

    return estado

# Função para gerar os sucessores de um estado (movimentos válidos)
def sucessores(estado, tipo):
    idx = estado.index(0)  # localiza o espaço vazio
    moves = []
    row, col = divmod(idx, 3)
    # ações: cima, baixo, esquerda, direita
    dirs = [(-1,0),(1,0),(0,-1),(0,1)]

    if tipo == 1:
        random.shuffle(dirs)

    for dr, dc in dirs:
        r, c = row + dr, col + dc
        if 0 <= r < 3 and 0 <= c < 3:
            new_idx = r * 3 + c
            new_state = estado.copy()
            # troca o espaço vazio com a peça alvo
            new_state[idx], new_state[new_idx] = new_state[new_idx], new_state[idx]
            moves.append(new_state)
    return moves

# Função de custo conforme o tipo (C1, C2, C3, C4)
def custo(estado1, estado2, tipo):
    idx1 = estado1.index(0)
    idx2 = estado2.index(0)
    row1, col1 = divmod(idx1, 3)
    row2, col2 = divmod(idx2, 3)
    dr, dc = abs(row1 - row2), abs(col1 - col2)

    if tipo == 'C1':
        return 2  # todos os movimentos custam 2
    elif tipo == 'C2':
        return 2 if dr else 3  # vertical = 2, horizontal = 3
    elif tipo == 'C3':
        return 3 if dr else 2  # vertical = 3, horizontal = 2
    elif tipo == 'C4':
        base = 2 if dr else 3
        # penaliza se o movimento levar o espaço para o centro
        if row2 == 1 and col2 == 1:
            return 5
        return base

# Funções heurística (H1 e H2)
def heuristica(estado, tipo):
    valor = 0

    #Cálculo da Heuristica H1(Número de peças no lugar errado)
    if(tipo == "H1"):
        for s in range(9):
            if estado[s] != GOAL[s] and estado[s] != 0:
                valor+=1

    #Cálculo da Heurística H2(Distância Manhattan)
    if(tipo == "H2"):
        for s in range(9):
            if s != 0:
                idx1, idx2 = estado.index(s), GOAL.index(s)
                row1, col1 = divmod(idx1, 3)
                row2, col2 = divmod(idx2, 3)
                valor += abs(row1 - row2) + abs(col1 - col2)

    valor *= 2        
    return valor

# ------------------------------------------
# Busca em Largura (Breadth-First Search)
# ------------------------------------------
def busca_largura(inicial, tipoMov):
    visitados = set()
    fila = deque([(inicial, [])])
    nos_gerados = 1
    while fila:
        estado, caminho = fila.popleft()
        visitados.add(tuple(estado))
        if estado == GOAL:
            return caminho + [estado], nos_gerados, len(visitados)
        for s in sucessores(estado, tipoMov):
            if tuple(s) not in visitados:
                fila.append((s, caminho + [estado]))
                nos_gerados += 1
    return None, nos_gerados, len(visitados)

# ------------------------------------------
# Busca em Profundidade (Depth-First Search)
# ------------------------------------------
def busca_profundidade(inicial, tipoMov):
    limite = 100
    visitados = set()
    pilha = [(inicial, [])]
    nos_gerados = 1

    while pilha:
        estado, caminho = pilha.pop()
        visitados.add(tuple(estado))

        if estado == GOAL:
            return caminho + [estado], nos_gerados, len(visitados)

        if len(caminho) < limite:
            for s in sucessores(estado, tipoMov):
                if tuple(s) not in visitados:
                    pilha.append((s, caminho + [estado]))
                    nos_gerados += 1

    return None, nos_gerados, len(visitados)


# def busca_profundidade(inicial, tipoMov):
#     visitados = set()
#     pilha = [(inicial, [])]
#     nos_gerados = 1
#     while pilha:
#         estado, caminho = pilha.pop()
#         visitados.add(tuple(estado))
#         if estado == GOAL:
#             return caminho + [estado], nos_gerados, len(visitados)
#         for s in sucessores(estado, tipoMov):
#             if tuple(s) not in visitados:
#                 pilha.append((s, caminho + [estado]))
#                 nos_gerados += 1
#     return None, nos_gerados, len(visitados)

# ------------------------------------------
# Busca de Custo Uniforme (Uniform Cost Search)
# ------------------------------------------
def busca_custo_uniforme(inicial,tipo, tipoMov):
    visitados = set()
    heap = [(0, inicial, [])]  # heap = fila de prioridade
    nos_gerados = 1
    while heap:
        cost, estado, caminho = heapq.heappop(heap)
        if tuple(estado) in visitados:
            continue
        visitados.add(tuple(estado))
        if estado == GOAL:
            return caminho + [estado], cost, nos_gerados, len(visitados)
        for s in sucessores(estado, tipoMov):
            if tuple(s) not in visitados:
                c = custo(estado, s, tipo)
                heapq.heappush(heap, (cost + c, s, caminho + [estado]))
                nos_gerados += 1
    return None, float('inf'), nos_gerados, len(visitados)

# ------------------------------------------
# Busca Gulosa
# ------------------------------------------
def busca_gulosa(estado_inicial, tipo_custo, tipo_heuristica, tipoMov):
    estado_inicial = tuple(estado_inicial)
    visitados = set()
    heap = [(heuristica(estado_inicial, tipo_heuristica), estado_inicial, [])]
    nos_gerados = 1

    while heap:
        h, estado, caminho = heapq.heappop(heap)

        if estado in visitados:
            continue
        visitados.add(estado)

        if estado == tuple(GOAL):
            caminho_completo = caminho + [estado]
            custo_total = 0
            for i in range(len(caminho_completo) - 1):
                custo_total += custo(caminho_completo[i], caminho_completo[i+1], tipo_custo)
            return caminho_completo, custo_total, nos_gerados, len(visitados)

        for s in sucessores(list(estado), tipoMov):
            s_tuple = tuple(s)
            if s_tuple not in visitados:
                h_val = heuristica(s_tuple, tipo_heuristica)
                heapq.heappush(heap, (h_val, s_tuple, caminho + [estado]))
                nos_gerados += 1

    return None, float('inf'), nos_gerados, len(visitados)


# ------------------------------------------
# Busca A*
# ------------------------------------------
def busca_a_star(estado_inicial, tipo_custo, tipo_heuristica, tipoMov):
    estado_inicial = tuple(estado_inicial)
    visitados = set()
    heap = [(heuristica(estado_inicial, tipo_heuristica), 0, estado_inicial, [])]  # (f, g, estado, caminho)
    nos_gerados = 1

    while heap:
        f, g, estado, caminho = heapq.heappop(heap)

        if estado in visitados:
            continue
        visitados.add(estado)

        if list(estado) == GOAL:
            return caminho + [estado], g, nos_gerados, len(visitados)
        
        for s in sucessores(list(estado), tipoMov):
            s_tuple = tuple(s)
            if s_tuple not in visitados:
                custo_transicao = custo(estado, s_tuple, tipo_custo)
                novo_g = g + custo_transicao
                h = heuristica(s_tuple, tipo_heuristica)
                heapq.heappush(heap, (novo_g + h, novo_g, s_tuple, caminho + [estado]))
                nos_gerados += 1

    return None, float('inf'), nos_gerados, len(visitados)


# ------------------------------------------
# Execução da Parte 1 (30 execuções com C1-C4)
# ------------------------------------------
for i in range(30):

    inicial = gerar_estado_inicial()

    print(f"\n=== Execução {i+1} ===")
    print(f"Estado Inicial: {inicial}")

    for func in ['C1', 'C2', 'C3', 'C4']:
        # Busca em Largura
        print(f"\n[Busca em Largura] - Função de custo: {func}")
        caminho, nos_gerados, nos_visitados = busca_largura(inicial, 0)
        custo_total = sum(custo(caminho[i], caminho[i+1], func) for i in range(len(caminho)-1)) if caminho else float('inf')
        print(f"Caminho Final: {caminho[-1] if caminho else 'ERRO'} | Custo: {custo_total} | Nós gerados: {nos_gerados} | Nós visitados: {nos_visitados}")

        # Busca em Profundidade
        print(f"\n[Busca em Profundidade] - Função de custo: {func}")
        caminho, nos_gerados, nos_visitados = busca_profundidade(inicial, 0)
        custo_total = sum(custo(caminho[i], caminho[i+1], func) for i in range(len(caminho)-1)) if caminho else float('inf')
        print(f"Caminho Final: {caminho[-1] if caminho else 'ERRO'} | Custo: {custo_total} | Nós gerados: {nos_gerados} | Nós visitados: {nos_visitados}")

        # Busca de Custo Uniforme
        print(f"\n[Busca de Custo Uniforme] - Função de custo: {func}")
        caminho, custo_final, nos_gerados, nos_visitados = busca_custo_uniforme(inicial, func, 0)
        print(f"Caminho Final: {caminho[-1] if caminho else 'ERRO'} | Custo: {custo_final} | Nós gerados: {nos_gerados} | Nós visitados: {nos_visitados}")

# ------------------------------------------


# ------------------------------------------
# Execução da Parte 2 (30 execuções Custo Uniforme x A*)

for i in range(30):
        inicial = gerar_estado_inicial()
        print(f"\n=== Execução {i+1} ===")
        print(f"Estado Inicial: {inicial}")
        # Busca de Custo Uniforme
        for func in ['C1', 'C2', 'C3', 'C4']:
            print(f"\n[Busca de Custo Uniforme] - Função de custo: {func}")
            caminho, custo_final, nos_gerados, nos_visitados = busca_custo_uniforme(inicial, func, 0)
            print(f"Caminho Final: {caminho[-1] if caminho else 'ERRO'} | Custo: {custo_final} | Nós gerados: {nos_gerados} | Nós visitados: {nos_visitados}")
       
        #Busca A*
        for func in ['C1', 'C2', 'C3', 'C4']:
            for h in ['H1', 'H2']:
                print(f"\n[Busca A*] - Heurística: {h} | Função de custo: {func}")
                caminho, custo_final, nos_gerados, nos_visitados = busca_a_star(inicial, func, h, 0)
                print(f"Caminho Final: {caminho[-1] if caminho else 'ERRO'} | Custo: {custo_final} | Heusística: {h} | Nós gerados: {nos_gerados} | Nós visitados: {nos_visitados}")

# ------------------------------------------

# ------------------------------------------
# Execução da Parte 3 (30 execuções Busca Gulosa x A*)
for i in range(30):
    inicial = gerar_estado_inicial()
    print(f"\n=== Execução {i+1} ===")
    print(f"Estado Inicial: {inicial}")
    for h in ['H1', 'H2']:
        for func in ['C1','C2','C3','C4']:
            print(f"\n[Busca gulosa] - Função de custo: {func} | Heurística: {h}")
            caminho, custo_final, nos_gerados, nos_visitados = busca_gulosa(inicial, func, h, 0)
            print(f"Caminho Final: {caminho[-1] if caminho else 'ERRO'} | Custo: {custo_final} | Heusística: {h} | Nós gerados: {nos_gerados} | Nós visitados: {nos_visitados}")

    for func in ['C1', 'C2', 'C3', 'C4']:
        for h in ['H1', 'H2']:
            print(f"\n[Busca A*] - Função de custo: {func} | Heurística: {h}")
            caminho, custo_final, nos_gerados, nos_visitados = busca_a_star(inicial, func, h, 0)
            print(f"Caminho Final: {caminho[-1] if caminho else 'ERRO'} | Custo: {custo_final} | Heusística: {h} | Nós gerados: {nos_gerados} | Nós visitados: {nos_visitados}")

# ------------------------------------------

# ------------------------------------------
# Execução da Parte 4 (15 execuções Largura x Profundidade com randomização da vizinhança)

for i in range(15):
    inicial = gerar_estado_inicial()
    print(f"\n=== Execução {i+1} ===")
    print(f"Estado Inicial: {inicial}")
    # inicial = [7, 5, 8, 4, 6, 0, 2, 3, 1]

    for j in range(10):
        for func in ['C1', 'C2', 'C3', 'C4']:
            # Busca em Largura
            print(f"\n[Busca em Largura] - Função de custo: {func}")
            caminho, nos_gerados, nos_visitados = busca_largura(inicial, 1)
            custo_total = sum(custo(caminho[i], caminho[i+1], func) for i in range(len(caminho)-1)) if caminho else float('inf')
            print(f"Caminho Final: {caminho[-1] if caminho else 'ERRO'} | Custo: {custo_total} | Nós gerados: {nos_gerados} | Nós visitados: {nos_visitados}")
    
    for k in range(10):
        for func in ['C1', 'C2', 'C3', 'C4']:
            print(f"\n[Busca em Profundidade] - Função de custo: {func}")
            caminho, nos_gerados, nos_visitados = busca_profundidade(inicial, 1)
            custo_total = sum(custo(caminho[i], caminho[i+1], func) for i in range(len(caminho)-1)) if caminho else float('inf')
            print(f"Caminho Final: {caminho[-1] if caminho else 'ERRO'} | Custo: {custo_total} | Nós gerados: {nos_gerados} | Nós visitados: {nos_visitados}")


# ------------------------------------------
