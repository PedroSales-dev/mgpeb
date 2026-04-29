# Anexo Técnico — Estruturas de Dados no MGPEB
## Missão Hélio Vermelho | Pedro Sales — RM572709 | FIAP 2026

---

## Visão Geral

O MGPEB (Módulo de Gerenciamento de Pouso e Estabilização de Base) da Missão Hélio
Vermelho opera sob restrições severas de hardware embarcado: memória limitada,
processamento reduzido e necessidade de comportamento determinístico. Nesse contexto,
a escolha das estruturas de dados não é estética — é uma decisão de engenharia.

Três estruturas lineares sustentam toda a lógica operacional do sistema:

| Estrutura        | Princípio | Implementação Python   | Papel no MGPEB                     |
|------------------|-----------|------------------------|------------------------------------|
| Fila (`deque`)   | FIFO      | `collections.deque`    | Tráfego orbital e sequência de pouso |
| Pilha (`list`)   | LIFO      | `list` com `append/pop`| Gestão de emergências críticas     |
| Lista (`list`)   | Indexada  | `list`                 | Histórico, pousados, adiados       |

---

## 1 ◆ Fila Orbital — FIFO (First-In, First-Out)

### Conceito

A fila garante que o **primeiro módulo a entrar seja o primeiro a ser processado**.
Isso é essencial para preservar a hierarquia de prioridade estabelecida pelo
Insertion Sort antes do carregamento: uma vez que a fila está ordenada por
prioridade, o mecanismo FIFO assegura que essa ordem seja respeitada durante
toda a sequência de pousos.

### Justificativa da Implementação

Foi utilizado `collections.deque` em vez de `list` convencional porque:

- `list.pop(0)` desloca todos os elementos → complexidade **O(n)**
- `deque.popleft()` remove da frente sem deslocamento → complexidade **O(1)**

Em sistemas embarcados, onde cada ciclo de CPU conta, essa diferença é crítica.

### Diagrama de Operação

```
Estado inicial após Insertion Sort:
┌─────────────┬───────────┬────────────┬────────────┬───────────┬─────────────┐
│ HV-Medic-01 │ HV-Hab-01 │ HV-Solar-01│ HV-Hydro-01│ HV-Comm-01│ HV-Mining-01│
│  Prio: 1    │  Prio: 2  │  Prio: 3  │  Prio: 4  │  Prio: 5  │   Prio: 6   │
└─────────────┴───────────┴────────────┴────────────┴───────────┴─────────────┘
   ↑ popleft()                                                   append() ↑
   (saída — FIFO)                                               (entrada)

Após processar HV-Medic-01:
┌───────────┬────────────┬────────────┬───────────┬─────────────┐
│ HV-Hab-01 │ HV-Solar-01│ HV-Hydro-01│ HV-Comm-01│ HV-Mining-01│
└───────────┴────────────┴────────────┴───────────┴─────────────┘
```

### Trecho do Código

```python
from collections import deque

# Inicialização da fila orbital
fila_orbital = deque()

# Carregamento após ordenação por prioridade
for modulo in modulos_ordenados:
    fila_orbital.append(modulo)          # enqueue — O(1)

# Processamento sequencial dos módulos
while fila_orbital:
    modulo = fila_orbital.popleft()      # dequeue — O(1)
    status = avaliar_pouso(modulo)
    # ... tomada de decisão
```

---

## 2 ◆ Pilha de Alertas — LIFO (Last-In, First-Out)

### Conceito

A pilha opera de forma invertida à fila: **o último elemento inserido é o
primeiro a ser removido**. No MGPEB, isso é semanticamente correto para
emergências: a falha mais recente tende a refletir as condições atuais do
ambiente marciano e, portanto, exige atenção imediata.

### Justificativa da Implementação

A `list` nativa do Python é usada diretamente porque:

- `list.append()` adiciona ao topo → **O(1)**
- `list.pop()` remove do topo → **O(1)**
- Não há necessidade de remover do início, eliminando a motivação para `deque`

### Diagrama de Operação

```
Cenário: três módulos em alerta são inseridos sequencialmente

Inserção (push):          Remoção (pop):
                          ┌─────────────────┐
push(HV-Hab-01)  →  [1]   │  HV-Mining-01   │ ← pop() — tratado primeiro
push(HV-Hydro-01)→  [2]   ├─────────────────┤
push(HV-Mining-01)→ [3]   │  HV-Hydro-01    │
                          ├─────────────────┤
                          │  HV-Hab-01      │ ← inserido primeiro, sai por último
                          └─────────────────┘
                             BASE DA PILHA
```

### Trecho do Código

```python
pilha_alertas = []          # lista operando como pilha LIFO

# Push: módulo crítico entra no topo
if status == "ALERTA":
    pilha_alertas.append(modulo)   # O(1)

# Pop: tratamento em ordem reversa de inserção (LIFO)
while pilha_alertas:
    emergencia = pilha_alertas.pop()          # O(1) — sempre do topo
    print(f"Protocolo de emergência: {emergencia['nome']}")
    # acionar sistemas de contenção...
```

---

## 3 ◆ Listas de Estado — Indexadas

### Conceito

As listas armazenam módulos que já saíram da fila orbital, organizados
conforme o resultado da avaliação booleana. São estruturas de **acesso
aleatório** por índice e permitem análises posteriores, auditoria e
geração de relatórios.

### Três listas de estado no MGPEB

| Lista       | Conteúdo                                  | Operações típicas          |
|-------------|-------------------------------------------|----------------------------|
| `pousados`  | Módulos com pouso autorizado e concluído  | append, iteração, busca    |
| `adiados`   | Módulos aguardando nova janela de pouso   | append, iteração, triagem  |
| `historico` | Registro completo de todas as decisões    | append, auditoria completa  |

### Justificativa

Ao contrário da fila e da pilha, as listas não impõem uma ordem de acesso.
Isso é intencional: históricos e registros de estado precisam ser consultados
em qualquer posição, filtrados por critério e transformados em relatórios.
A flexibilidade supera a necessidade de garantir ordem de acesso.

### Trecho do Código

```python
pousados  = []
adiados   = []
historico = []

# Registro por estado após avaliação
registro = {**modulo, "status": status}
historico.append(registro)           # sempre registra tudo

if status == "AUTORIZADO":
    pousados.append(registro)
elif status == "ADIADO":
    adiados.append(registro)

# Busca do módulo com menor combustível entre os pousados
if pousados:
    critico = min(pousados, key=lambda m: m["combustivel_pct"])
    print(f"Menor combustível pousado: {critico['nome']} → {critico['combustivel_pct']}%")
```

---

## 4 ◆ Comparativo de Complexidade

| Operação            | `list` (início) | `list` (fim) | `deque` (início) | `deque` (fim) |
|---------------------|-----------------|--------------|------------------|---------------|
| Inserção            | O(n)            | **O(1)**     | **O(1)**         | **O(1)**      |
| Remoção             | O(n)            | **O(1)**     | **O(1)**         | **O(1)**      |
| Acesso por índice   | **O(1)**        | **O(1)**     | O(n)             | O(n)          |
| Busca linear        | O(n)            | O(n)         | O(n)             | O(n)          |

**Conclusão de engenharia:** `deque` é superior para fila (acesso nas duas
pontas); `list` é superior para pilha (acesso apenas no fim) e para histórico
(acesso por índice). O MGPEB usa cada estrutura onde ela é ótima.

---

## 5 ◆ Relação entre Estruturas e Fases da Simulação

```
MÓDULOS GERADOS
      │
      ▼
[Insertion Sort] ────────────► Lista temporária ordenada
                                        │
                                        ▼
                              ┌─────────────────┐
                              │  FILA ORBITAL   │  (deque FIFO)
                              │  popleft() →    │
                              └────────┬────────┘
                                       │ avaliação booleana
                         ┌─────────────┼─────────────┐
                         ▼             ▼             ▼
                    AUTORIZADO       ALERTA        ADIADO
                         │             │             │
                         ▼             ▼             ▼
                   lista pousados  pilha alertas  lista adiados
                         │             │             │
                         └─────────────┴─────────────┘
                                       │
                                       ▼
                               lista historico
                            (auditoria completa)
```

---

*Anexo elaborado por Pedro Sales — RM572709 | FIAP 2026 — Ciência da Computação*
