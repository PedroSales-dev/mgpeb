"""
=============================================================================
  MGPEB — Módulo de Gerenciamento de Pouso e Estabilização de Base
  Missão: Hélio Vermelho | FIAP 2026 — Ciência da Computação
  Autor:  Pedro Sales — RM572709
=============================================================================

  Este módulo implementa o sistema de controle de pousos da Missão Hélio
  Vermelho, responsável por coordenar a sequência de descida de seis
  unidades de infraestrutura na superfície marciana. O sistema integra:

    - Estruturas lineares (fila FIFO, pilha LIFO, listas de estado)
    - Algoritmos de ordenação (Insertion Sort) e busca (linear e binária)
    - Lógica booleana para autorização/bloqueio de pouso
    - Modelagem matemática do consumo de combustível por fase de descida
    - Relatório final de operação

  Bibliotecas utilizadas: random, math, collections (deque) — apenas
  recursos da biblioteca padrão do Python, sem dependências externas.
=============================================================================
"""

import math
import random
from collections import deque


# ─────────────────────────────────────────────────────────────────────────────
#  SEÇÃO 1 — DEFINIÇÃO DOS MÓDULOS DA MISSÃO
# ─────────────────────────────────────────────────────────────────────────────

def gerar_modulos():
    """
    Cria e retorna a lista mestre dos seis módulos da Missão Hélio Vermelho.

    Atributos fixos (definidos pela missão):
        nome              — identificador da unidade
        tipo              — categoria funcional
        prioridade        — 1 (máxima) a 6 (básica)

    Atributos variáveis (gerados via random, simulando telemetria real):
        combustivel_pct   — percentual de combustível restante (0.0 – 100.0)
        massa_kg          — massa total do módulo em quilogramas
        integ_sensores    — índice de integridade dos sensores (0.0 – 1.0)
        cond_vento        — velocidade do vento em Marte em m/s (0 – 25)
        zona_liberada     — booleano: área de pouso mapeada e liberada
        hora_orbita       — hora estimada de chegada à órbita (HH:MM)
        criticidade_carga — nível de urgência da carga embarcada (1 – 5)
    """

    random.seed()   # seed variável para simular execuções distintas

    modulos_base = [
        {"nome": "HV-Medic-01",  "tipo": "Suporte Médico e Biológico", "prioridade": 1},
        {"nome": "HV-Hab-01",    "tipo": "Habitação Modular",           "prioridade": 2},
        {"nome": "HV-Solar-01",  "tipo": "Geração de Energia Solar",    "prioridade": 3},
        {"nome": "HV-Hydro-01",  "tipo": "Aquaponia e Suporte Alimentar","prioridade": 4},
        {"nome": "HV-Comm-01",   "tipo": "Comunicações e Telemetria",   "prioridade": 5},
        {"nome": "HV-Mining-01", "tipo": "Mineração e Recursos Locais", "prioridade": 6},
    ]

    modulos = []
    for base in modulos_base:
        hora_h = random.randint(0, 23)
        hora_m = random.randint(0, 59)
        modulo = {
            **base,
            "combustivel_pct": round(random.uniform(8.0, 100.0), 1),
            "massa_kg":        random.randint(3_000, 14_000),
            "integ_sensores":  round(random.uniform(0.0, 1.0), 2),
            "cond_vento":      round(random.uniform(0.0, 25.0), 1),
            "zona_liberada":   random.choice([True, True, True, False]),
            "hora_orbita":     f"{hora_h:02d}:{hora_m:02d}",
            "criticidade_carga": random.randint(1, 5),
        }
        modulos.append(modulo)

    return modulos


# ─────────────────────────────────────────────────────────────────────────────
#  SEÇÃO 2 — MODELAGEM MATEMÁTICA
#  Função: Consumo de Combustível por Fase de Descida
#
#  O consumo de combustível ao longo da descida segue um modelo exponencial
#  negativo, pois os retrofoguetes operam em alta intensidade nos primeiros
#  segundos e reduzem progressivamente o empuxo conforme a velocidade cai:
#
#      C(t) = C0 * e^(-k * t)
#
#  Onde:
#    C0  — taxa de consumo inicial (kg/s) — proporcional à massa do módulo
#    k   — constante de decaimento (s⁻¹) — depende da eficiência do motor
#    t   — tempo decorrido na fase de frenagem (segundos)
#
#  Interpretação qualitativa:
#    - Quando t → 0  : consumo máximo C0 (pleno empuxo inicial)
#    - Quando t aumenta: consumo decresce exponencialmente (frenagem suave)
#    - Quando k aumenta: decaimento mais rápido → pouso mais eficiente
#    - Quando k diminui: decaimento lento → consumo alto por mais tempo
#
#  Decisão de engenharia:
#    O instante ótimo de acionamento dos retrofoguetes é calculado como o
#    ponto em que C(t) cai abaixo de 30% de C0, garantindo que o combustível
#    restante seja suficiente para a estabilização final (hovering).
# ─────────────────────────────────────────────────────────────────────────────

def calcular_consumo(massa_kg, t, k=0.04):
    """
    Calcula a taxa de consumo de combustível (kg/s) no instante t.

    Parâmetros:
        massa_kg (int)  : massa do módulo — determina C0 = massa / 2000
        t        (float): tempo em segundos desde início da frenagem
        k        (float): constante de decaimento (padrão: 0.04 s⁻¹)

    Retorna:
        float: taxa de consumo em kg/s
    """
    c0 = massa_kg / 2000.0   # taxa inicial proporcional à massa
    return round(c0 * math.exp(-k * t), 3)


def instante_acionamento_retrofoguetes(massa_kg, k=0.04, limiar=0.30):
    """
    Determina o instante t* em que a taxa de consumo cai abaixo de
    `limiar * C0`, indicando o momento seguro para redução do empuxo.

    Resolução analítica:  t* = -ln(limiar) / k

    Parâmetros:
        massa_kg (int)  : massa do módulo
        k        (float): constante de decaimento
        limiar   (float): fração de C0 que define o gatilho (padrão: 30%)

    Retorna:
        float: tempo em segundos
    """
    t_estrela = -math.log(limiar) / k
    return round(t_estrela, 1)


def exibir_modelagem_matematica(modulo):
    """Imprime a análise matemática de consumo para um módulo específico."""
    nome  = modulo["nome"]
    massa = modulo["massa_kg"]
    k     = 0.04
    c0    = round(massa / 2000.0, 3)
    t_str = instante_acionamento_retrofoguetes(massa, k)

    print(f"\n  {'─'*54}")
    print(f"  📐 Modelagem Matemática — {nome}")
    print(f"  {'─'*54}")
    print(f"  Função : C(t) = C0 · e^(-k·t)")
    print(f"  C0 (taxa inicial) = {massa} / 2000 = {c0} kg/s")
    print(f"  k  (decaimento)   = {k} s⁻¹")
    print()
    print(f"  {'t (s)':>6}  {'C(t) kg/s':>10}  {'% de C0':>8}")
    print(f"  {'─'*30}")
    for t in [0, 10, 20, 30, 40, 60, 90, int(t_str)]:
        ct  = calcular_consumo(massa, t, k)
        pct = round((ct / c0) * 100, 1) if c0 > 0 else 0
        marcador = " ← t* (acionamento ótimo)" if t == int(t_str) else ""
        print(f"  {t:>6}  {ct:>10}  {pct:>7}%{marcador}")
    print(f"\n  → Acionamento recomendado dos retrofoguetes: t* = {t_str}s")
    print(f"  → Nesse instante, consumo é 30% do valor inicial.")


# ─────────────────────────────────────────────────────────────────────────────
#  SEÇÃO 3 — LÓGICA BOOLEANA DE DECISÃO DE POUSO
#
#  Expressões booleanas modeladas:
#
#  ALERTA_CRITICO = (combustivel_pct < 15) OR (integ_sensores < 0.25)
#
#  AUTORIZADO = NOT ALERTA_CRITICO
#             AND (combustivel_pct >= 25)
#             AND (integ_sensores >= 0.55)
#             AND (cond_vento <= 18.0)
#             AND (zona_liberada == True)
#
#  Diagrama de portas (representação ASCII):
#
#   combustivel >= 25%  ─┐
#   sensores   >= 0.55  ─┤ AND ─┐
#   vento      <= 18    ─┤      ├─ AND ──► AUTORIZADO
#   zona_livre = True   ─┘      │
#                               │
#   comb < 15%  ─┐              │
#                ├─ OR  ──► NOT ┘
#   sensor< 0.25 ┘
# ─────────────────────────────────────────────────────────────────────────────

def avaliar_pouso(modulo):
    """
    Aplica a lógica booleana de decisão ao módulo e retorna o status:
        'AUTORIZADO' — todas as condições operacionais satisfeitas
        'ALERTA'     — condições críticas impeditivas detectadas
        'ADIADO'     — condições insuficientes mas não críticas
    """
    comb    = modulo["combustivel_pct"]
    sensor  = modulo["integ_sensores"]
    vento   = modulo["cond_vento"]
    zona    = modulo["zona_liberada"]

    # Porta OR → condições que acionam alerta imediato
    alerta_critico = (comb < 15.0) or (sensor < 0.25)

    if alerta_critico:
        return "ALERTA"

    # Porta AND → todas precisam ser verdadeiras para autorizar
    comb_ok   = comb   >= 25.0
    sensor_ok = sensor >= 0.55
    vento_ok  = vento  <= 18.0
    zona_ok   = zona   == True

    autorizado = comb_ok and sensor_ok and vento_ok and zona_ok

    if autorizado:
        return "AUTORIZADO"
    else:
        return "ADIADO"


# ─────────────────────────────────────────────────────────────────────────────
#  SEÇÃO 4 — ALGORITMO DE ORDENAÇÃO (INSERTION SORT)
#
#  O Insertion Sort foi escolhido por seu comportamento determinístico e
#  previsível: complexidade O(n²) no pior caso, mas O(n) quando a lista
#  já está parcialmente ordenada — situação comum em filas de pouso onde
#  módulos chegam já com prioridade pré-estabelecida.
#
#  Em sistemas embarcados com memória restrita, a ordenação in-place do
#  Insertion Sort é preferível a algoritmos que exigem estruturas auxiliares.
# ─────────────────────────────────────────────────────────────────────────────

def insertion_sort_por_prioridade(lista):
    """
    Ordena a lista de módulos em ordem crescente de prioridade
    usando o algoritmo Insertion Sort (in-place).

    Parâmetros:
        lista (list): lista de dicionários de módulos

    Retorna:
        list: lista ordenada (a mesma lista, modificada in-place)
    """
    for i in range(1, len(lista)):
        chave = lista[i]
        j = i - 1
        # Desloca elementos maiores para a direita
        while j >= 0 and lista[j]["prioridade"] > chave["prioridade"]:
            lista[j + 1] = lista[j]
            j -= 1
        lista[j + 1] = chave
    return lista


# ─────────────────────────────────────────────────────────────────────────────
#  SEÇÃO 5 — ALGORITMOS DE BUSCA
# ─────────────────────────────────────────────────────────────────────────────

def busca_linear_por_tipo(lista, tipo_alvo):
    """
    Busca linear: percorre a lista sequencialmente procurando módulos
    cujo campo 'tipo' contenha o termo buscado (case-insensitive).

    Complexidade: O(n)
    Uso ideal: lista não ordenada ou busca por correspondência parcial.

    Retorna:
        list: lista de módulos encontrados (vazia se nenhum)
    """
    resultado = []
    for modulo in lista:
        if tipo_alvo.lower() in modulo["tipo"].lower():
            resultado.append(modulo)
    return resultado


def busca_binaria_por_prioridade(lista_ordenada, prioridade_alvo):
    """
    Busca binária: divide e conquista sobre lista JÁ ORDENADA por prioridade.

    Pré-condição: lista deve estar ordenada crescentemente por 'prioridade'.
    Complexidade: O(log n)
    Uso ideal: localização rápida em filas de pouso já classificadas.

    Retorna:
        dict | None: módulo encontrado ou None se não existir
    """
    esq, dir = 0, len(lista_ordenada) - 1

    while esq <= dir:
        meio = (esq + dir) // 2
        prio_meio = lista_ordenada[meio]["prioridade"]

        if prio_meio == prioridade_alvo:
            return lista_ordenada[meio]
        elif prio_meio < prioridade_alvo:
            esq = meio + 1
        else:
            dir = meio - 1

    return None   # prioridade não encontrada


def busca_menor_combustivel(lista):
    """
    Busca linear do módulo com menor nível de combustível.
    Útil para identificar unidades em situação crítica de recursos.

    Complexidade: O(n)
    """
    if not lista:
        return None

    menor = lista[0]
    for modulo in lista[1:]:
        if modulo["combustivel_pct"] < menor["combustivel_pct"]:
            menor = modulo
    return menor


# ─────────────────────────────────────────────────────────────────────────────
#  SEÇÃO 6 — ESTRUTURAS DE DADOS LINEARES
# ─────────────────────────────────────────────────────────────────────────────

def inicializar_estruturas():
    """
    Inicializa e retorna as três estruturas de dados do MGPEB:

    fila_orbital  (deque) — FIFO: módulos ordenados aguardando avaliação
    pilha_alertas (list)  — LIFO: módulos com falhas críticas (mais recente = topo)
    historico     (list)  — registro cronológico de todas as decisões
    """
    fila_orbital  = deque()   # FIFO — deque garante O(1) em ambas as pontas
    pilha_alertas = []        # LIFO — operado com append/pop
    historico     = []        # histórico completo para auditoria
    return fila_orbital, pilha_alertas, historico


# ─────────────────────────────────────────────────────────────────────────────
#  SEÇÃO 7 — FUNÇÕES DE EXIBIÇÃO
# ─────────────────────────────────────────────────────────────────────────────

LINHA = "═" * 60
SUBLINHA = "─" * 60

def cabecalho():
    print(f"\n{LINHA}")
    print("  MGPEB — Missão Hélio Vermelho")
    print("  Módulo de Gerenciamento de Pouso e Estabilização de Base")
    print(f"  Pedro Sales | RM572709 | FIAP 2026")
    print(f"{LINHA}\n")


def exibir_modulo(modulo, idx=None):
    """Imprime os atributos de um módulo de forma legível."""
    prefixo = f"[{idx}] " if idx is not None else "    "
    zona    = "✔ Liberada" if modulo["zona_liberada"] else "✘ Bloqueada"
    print(f"  {prefixo}{modulo['nome']} ({modulo['tipo']})")
    print(f"       Prioridade  : {modulo['prioridade']} | Criticidade: {modulo['criticidade_carga']}/5")
    print(f"       Combustível : {modulo['combustivel_pct']}% | Massa: {modulo['massa_kg']} kg")
    print(f"       Sensores    : {modulo['integ_sensores']} | Vento: {modulo['cond_vento']} m/s")
    print(f"       Zona        : {zona} | Órbita: {modulo['hora_orbita']}")


def exibir_resultado(modulo, status, t_pouso):
    """Imprime o resultado da decisão de pouso com formatação visual."""
    simbolo = {"AUTORIZADO": "✔", "ALERTA": "⚠", "ADIADO": "↺"}
    cores   = {"AUTORIZADO": "AUTORIZADO", "ALERTA": "ALERTA CRÍTICO", "ADIADO": "ADIADO"}
    print(f"  {simbolo.get(status, '?')} {modulo['nome']:15s} → {cores[status]}")


# ─────────────────────────────────────────────────────────────────────────────
#  SEÇÃO 8 — SIMULAÇÃO PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def executar_simulacao():
    """
    Ponto de entrada principal da simulação MGPEB.

    Fluxo de execução:
      1. Geração dos módulos com atributos aleatórios (telemetria simulada)
      2. Ordenação por prioridade via Insertion Sort
      3. Carga na fila orbital (FIFO)
      4. Demonstração de buscas (linear e binária)
      5. Avaliação booleana de cada módulo da fila
         → AUTORIZADO: registra em lista 'pousados'
         → ALERTA    : empilha na pilha_alertas (LIFO) + lista 'criticos'
         → ADIADO    : registra em lista 'adiados'
      6. Tratamento da pilha de alertas
      7. Modelagem matemática (módulo de maior massa)
      8. Relatório final de operação
    """

    cabecalho()

    # ── 1. Geração dos módulos ───────────────────────────────────────────────
    print(f"  {'─'*54}")
    print("  ► FASE 1 — Cadastro dos Módulos da Missão")
    print(f"  {'─'*54}")
    modulos = gerar_modulos()
    for i, m in enumerate(modulos, 1):
        exibir_modulo(m, i)
    print()

    # ── 2. Ordenação via Insertion Sort ─────────────────────────────────────
    print(f"  {'─'*54}")
    print("  ► FASE 2 — Ordenação por Prioridade (Insertion Sort)")
    print(f"  {'─'*54}")
    modulos_ordenados = insertion_sort_por_prioridade(list(modulos))
    for m in modulos_ordenados:
        print(f"  Prioridade {m['prioridade']} → {m['nome']}")
    print()

    # ── 3. Carga na fila FIFO ───────────────────────────────────────────────
    fila_orbital, pilha_alertas, historico = inicializar_estruturas()
    for m in modulos_ordenados:
        fila_orbital.append(m)

    print(f"  {'─'*54}")
    print(f"  ► FASE 3 — Fila Orbital Carregada ({len(fila_orbital)} módulos)")
    print(f"  {'─'*54}")
    for i, m in enumerate(fila_orbital, 1):
        print(f"  [{i}] {m['nome']}")
    print()

    # ── 4. Demonstração de Buscas ────────────────────────────────────────────
    print(f"  {'─'*54}")
    print("  ► FASE 4 — Demonstração de Algoritmos de Busca")
    print(f"  {'─'*54}")

    # Busca linear por tipo
    termo = "energia"
    resultado_linear = busca_linear_por_tipo(modulos, termo)
    print(f"  Busca Linear por tipo '{termo}':")
    if resultado_linear:
        for m in resultado_linear:
            print(f"    → Encontrado: {m['nome']}")
    else:
        print(f"    → Nenhum módulo encontrado para '{termo}'.")

    # Busca binária por prioridade
    prio_alvo = 3
    resultado_bin = busca_binaria_por_prioridade(modulos_ordenados, prio_alvo)
    print(f"\n  Busca Binária por prioridade {prio_alvo}:")
    if resultado_bin:
        print(f"    → Encontrado: {resultado_bin['nome']}")
    else:
        print(f"    → Prioridade {prio_alvo} não encontrada.")

    # Busca do menor combustível
    menor = busca_menor_combustivel(modulos)
    print(f"\n  Módulo com menor combustível:")
    print(f"    → {menor['nome']} com {menor['combustivel_pct']}%")
    print()

    # ── 5. Avaliação booleana da fila ────────────────────────────────────────
    print(f"  {'─'*54}")
    print(f"  ► FASE 5 — Autorização de Pouso (Lógica Booleana)")
    print(f"  {'─'*54}")

    pousados  = []
    adiados   = []
    criticos  = []

    while fila_orbital:
        modulo = fila_orbital.popleft()    # remove da frente da fila FIFO
        status = avaliar_pouso(modulo)
        t_simul = round(random.uniform(45.0, 90.0), 1)

        registro = {**modulo, "status": status, "t_descida_s": t_simul}
        historico.append(registro)

        exibir_resultado(modulo, status, t_simul)

        if status == "AUTORIZADO":
            pousados.append(registro)
        elif status == "ALERTA":
            pilha_alertas.append(registro)   # push na pilha LIFO
            criticos.append(registro)
        else:
            adiados.append(registro)

    print()

    # ── 6. Tratamento da pilha de alertas ────────────────────────────────────
    if pilha_alertas:
        print(f"  {'─'*54}")
        print(f"  ► FASE 6 — Tratamento de Alertas (Pilha LIFO)")
        print(f"  {'─'*54}")
        print(f"  {len(pilha_alertas)} alerta(s) na pilha. Processando do topo...\n")
        while pilha_alertas:
            emergencia = pilha_alertas.pop()    # pop do topo (LIFO)
            print(f"  ⚠  Protocolo de emergência acionado: {emergencia['nome']}")
            print(f"     Combustível: {emergencia['combustivel_pct']}% | "
                  f"Sensores: {emergencia['integ_sensores']}")
        print()
    else:
        print("  ► FASE 6 — Nenhum alerta crítico registrado.\n")

    # ── 7. Modelagem matemática ───────────────────────────────────────────────
    print(f"  {'─'*54}")
    print("  ► FASE 7 — Modelagem Matemática do Consumo")
    print(f"  {'─'*54}")
    modulo_ref = max(modulos, key=lambda m: m["massa_kg"])
    exibir_modelagem_matematica(modulo_ref)
    print()

    # ── 8. Relatório Final ────────────────────────────────────────────────────
    print(f"\n{LINHA}")
    print("  RELATÓRIO FINAL — MGPEB | Missão Hélio Vermelho")
    print(LINHA)
    print(f"  Total de módulos avaliados : {len(historico)}")
    print(f"  ✔  Pousados com sucesso    : {len(pousados)}")
    print(f"  ↺  Pouso adiado            : {len(adiados)}")
    print(f"  ⚠  Alertas críticos        : {len(criticos)}")
    print()

    if pousados:
        print("  Módulos pousados:")
        for m in pousados:
            print(f"    · {m['nome']} ({m['tipo']})")

    if adiados:
        print("\n  Módulos com pouso adiado:")
        for m in adiados:
            print(f"    · {m['nome']} — verificar: "
                  f"comb={m['combustivel_pct']}%, "
                  f"vento={m['cond_vento']}m/s, "
                  f"zona={'OK' if m['zona_liberada'] else 'BLOQUEADA'}")

    if criticos:
        print("\n  Módulos em situação crítica:")
        for m in criticos:
            print(f"    · {m['nome']} — comb={m['combustivel_pct']}%, "
                  f"sensor={m['integ_sensores']}")

    print(f"\n{LINHA}")
    print("  Simulação concluída. Aguardando próxima janela orbital.")
    print(f"{LINHA}\n")


# ─────────────────────────────────────────────────────────────────────────────
#  PONTO DE ENTRADA
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    executar_simulacao()
