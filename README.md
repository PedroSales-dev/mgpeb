# MGPEB — Módulo de Gerenciamento de Pouso e Estabilização de Base

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Status](https://img.shields.io/badge/Status-Concluído-brightgreen)
![Projeto](https://img.shields.io/badge/Tipo-Engenharia%20de%20Sistemas-orange)

---

## Visão Geral

O **MGPEB (Módulo de Gerenciamento de Pouso e Estabilização de Base)** é uma simulação de um sistema embarcado responsável por coordenar operações críticas de pouso em uma missão de colonização em Marte.

O projeto demonstra, de forma aplicada, como conceitos fundamentais da Ciência da Computação atuam em sistemas de alta criticidade, onde decisões impactam diretamente o sucesso da operação.

---

## Objetivo

Desenvolver um sistema capaz de:

* Gerenciar a sequência de pouso de módulos
* Avaliar condições operacionais em tempo quase real
* Priorizar decisões com base em dados de telemetria
* Tratar situações críticas (alertas)
* Registrar todas as decisões para auditoria

---

## Arquitetura do Sistema

```id="sys-arch"
Entrada de dados (telemetria)
            │
            ▼
   Ordenação por prioridade (Insertion Sort)
            │
            ▼
      Fila Orbital (FIFO)
            │
            ▼
   Motor de Decisão (Lógica Booleana)
   ┌───────────────┬───────────────┬───────────────┐
   ▼               ▼               ▼
AUTORIZADO       ALERTA          ADIADO
   │               │               │
   ▼               ▼               ▼
Lista         Pilha (LIFO)      Lista
   └───────────────┴───────────────┘
            ▼
        Histórico
```

---

##  Conceitos Aplicados

### Estruturas de Dados

| Estrutura       | Tipo      | Função                         |
| --------------- | --------- | ------------------------------ |
| Fila (`deque`)  | FIFO      | Controle da ordem de pouso     |
| Pilha (`list`)  | LIFO      | Tratamento de alertas críticos |
| Listas (`list`) | Indexadas | Histórico e estados            |

---

### Algoritmos

* **Insertion Sort** → Ordenação por prioridade
* **Busca Linear** → Localização flexível
* **Busca Binária** → Busca eficiente em dados ordenados

---

### Lógica de Decisão

```text id="logic"
AUTORIZADO = NOT ALERTA
             AND combustível ≥ 25%
             AND sensores ≥ 0.55
             AND vento ≤ 18 m/s
             AND zona liberada
```

Estados possíveis:

* **AUTORIZADO**
* **ALERTA**
* **ADIADO**

---

### Modelagem Matemática

O consumo de combustível é modelado por uma função exponencial:

```id="math"
C(t) = C0 · e^(-k·t)
```

Aplicação:

* Determinar o momento ideal de acionamento dos retrofoguetes
* Otimizar o consumo durante a descida

---

## Execução

### Pré-requisitos

* Python 3.8 ou superior

### Executar o sistema

```bash id="run"
python mgpeb.py
```

---

##  Exemplo de Saída

```text id="output"
HV-Medic-01   → AUTORIZADO
HV-Hydro-01   → ALERTA
HV-Comm-01    → ADIADO
```

---

## Estrutura do Projeto

```id="structure"
📁MGPEB/
│
├── README.md
├── mgpeb.py
├── Relatorio_MGPEB.pdf
└── anexo_estrutura_dados.md
```

---

## Decisões de Engenharia

O sistema foi projetado considerando restrições típicas de sistemas embarcados:

* Uso de `deque` para operações eficientes em fila (O(1))
* Uso de `list` para pilha pela simplicidade e desempenho
* Escolha do Insertion Sort por comportamento determinístico
* Ausência de bibliotecas externas para simular limitações reais

---

## Complexidade

| Componente     | Complexidade |
| -------------- | ------------ |
| Insertion Sort | O(n²)        |
| Busca Linear   | O(n)         |
| Busca Binária  | O(log n)     |
| Fila (`deque`) | O(1)         |
| Pilha (`list`) | O(1)         |

---

## 👨‍💻 Autor

Pedro Sales
FIAP — Ciência da Computação

---

## 📌 Considerações Finais

Este projeto demonstra que o desenvolvimento de software vai além da implementação de código.

Em sistemas críticos, como uma missão espacial, é essencial garantir que:

* As decisões sejam previsíveis
* Os algoritmos sejam eficientes
* As estruturas de dados sejam adequadas
* O sistema seja confiável

Cada escolha técnica impacta diretamente o resultado final.

---

Simulação concluída. Aguardando próxima janela orbital.
