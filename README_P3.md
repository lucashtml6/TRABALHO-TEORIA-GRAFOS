# Parte 3 — Grafos Direcionados, Dijkstra e Bellman-Ford

> Base para os slides (Claude Design). Foco nos **estudos de caso**.
> COS 242 — Teoria dos Grafos · Universidade Federal de Viçosa

---

## O que foi construído

A biblioteca das Partes 1 e 2 ganhou três capacidades novas:

1. **Grafos direcionados com pesos** — uma única flag `directed` na representação. Cada linha `u v w` do arquivo vira o arco `u → v`.
2. **BFS, DFS e Dijkstra em grafos direcionados** — funcionam **sem alteração**: sempre percorreram o grafo pelas arestas de saída.
3. **Bellman-Ford** — caminhos mínimos com **pesos negativos**, **detecção de ciclo negativo** e as **duas otimizações** vistas em aula.

**Ideia-chave que destrava os estudos de caso — o grafo invertido:** para achar a distância **DE** vários vértices **ATÉ** o vértice 100 com um algoritmo de fonte única, invertemos todas as arestas e rodamos **uma vez** a partir de 100. Resultado: `d(v → 100) = d_invertido(100 → v)` para todos os `v` de uma só vez.

---

## A pergunta dos estudos de caso

> Qual a distância dos vértices **10, 20 e 30** até o vértice **100**, em cada grafo?
> Quanto tempo leva? Dá para resolver com Dijkstra quando não há pesos negativos?

5 grafos direcionados, de 25 mil a 10 milhões de vértices. Só o **`grafo_W_1`** tem arestas negativas.

---

## 📊 Estudo de caso 1 — Distâncias até o vértice 100

| grafo     |        n | Bellman-Ford (10→100 / 20→100 / 30→100) | Dijkstra | Ciclo negativo? |
|-----------|---------:|:----------------------------------------|:---------|:---------------:|
| grafo_W_1 |   25 000 | **indefinido** (ciclo negativo!)        | n/a      | 🔴 **SIM**      |
| grafo_W_2 |   25 000 | 10,47 / 8,48 / 8,71                      | **igual** ✅ | não          |
| grafo_W_3 |  100 000 | 4,63 / 5,42 / 4,67                       | **igual** ✅ | não          |
| grafo_W_4 | 1 000 000 | INVIÁVEL (memória)                      | —        | —               |
| grafo_W_5 |10 000 000 | INVIÁVEL (memória)                      | —        | —               |

### 💡 Destaques

- **`grafo_W_1` tem um ciclo negativo** alcançável até o 100. Com um ciclo negativo, **não existe distância mínima** — dá para rodar em volta dele baixando o custo para sempre. A resposta certa não é um número: é a flag "ciclo negativo". É exatamente por isso que **Dijkstra não serve aqui**.
- Nos grafos sem peso negativo, **Bellman-Ford e Dijkstra dão a mesma resposta, dígito a dígito** — validação cruzada das duas implementações e do truque do grafo invertido.
- Distâncias **pequenas e parecidas** (efeito *mundo pequeno*). Quanto mais **denso** o grafo, **menor** a distância: `grafo_W_3` (mais arestas) tem caminhos mais baratos que `grafo_W_2`.

---

## ⏱️ Estudo de caso 2 — Tempo de execução (média de 10 rodadas)

| grafo     | Bellman-Ford | Dijkstra |  Quem ganha?         |
|-----------|-------------:|---------:|:---------------------|
| grafo_W_1 |   0,6 ms*    | —        | * aborta no ciclo    |
| grafo_W_2 |    536 ms    |  236 ms  | Dijkstra ~2,3× 🏆    |
| grafo_W_3 |  4 832 ms    | 3 263 ms | Dijkstra ~1,5× 🏆    |
| grafo_W_4 |  INVIÁVEL    | INVIÁVEL | memória > 16 GB      |
| grafo_W_5 |  INVIÁVEL    | INVIÁVEL | memória > 16 GB      |

### 💡 Destaques

- **Dijkstra é mais rápido** onde é aplicável: finaliza cada vértice **uma vez só**. O Bellman-Ford reprocessa vértices até estabilizar.
- A vantagem do Dijkstra **encolhe** em grafos densos (2,3× → 1,5×): o custo passa a ser dominado pela varredura das arestas, que os dois pagam.
- **As otimizações são tudo.** O Bellman-Ford ingênuo faria V−1 varreduras completas — no `grafo_W_3` seriam **~600 bilhões** de operações por execução (dezenas de minutos). Com as duas otimizações, ele converge em **poucas rodadas** → ~5 s. **Sem elas, o estudo de caso seria impossível.**

---

## 🔧 As duas otimizações do Bellman-Ford

| # | Otimização | Em uma frase |
|---|------------|--------------|
| 1 | **Parada antecipada** | Se uma rodada não melhora nada, acabou — não precisa das V−1 passadas. |
| 2 | **Só os vértices atualizados** | Só relaxa as arestas de quem mudou na rodada anterior (conjunto ativo / SPFA). |

**Detecção de ciclo negativo (bônus técnico):** em vez de esperar V iterações, verificamos o **grafo de predecessores** — qualquer ciclo ali já é negativo. Detectamos o ciclo do `grafo_W_1` em **frações de milissegundo**, no instante em que ele se fecha.

---

## ▶️ Como rodar

```bash
# Demo: grafo direcionado pequeno (exemplo do CLRS) com Bellman-Ford,
# grafo invertido, comparação BF vs Dijkstra e detecção de ciclo negativo
python main_p3.py

# Estudos de caso nos grafos direcionados (GRAFOS 3/)
python estudos/ec_p3_runner.py --only 1 2 3
```

Os grafos ficam na pasta `GRAFOS 3/` (`grafo_W_1.txt` … `grafo_W_5.txt`). Resultados em `relatorio/resultados/`.

---

## 📌 Mensagens para levar

1. **Direção quase de graça** — uma flag, e BFS/DFS/Dijkstra continuam funcionando.
2. **Grafo invertido** resolve "distância até um alvo" com uma única busca.
3. **Pesos negativos exigem Bellman-Ford**; Dijkstra falha — e `grafo_W_1` mostra por quê (ciclo negativo ⇒ distância indefinida).
4. **Sem peso negativo, Dijkstra vence** no tempo, mas os dois concordam na resposta.
5. **As otimizações transformam Θ(V·E) em viável** — são elas que permitem rodar em milhões de arestas.

📄 Relatório completo: [relatorio/relatorio_P3.md](relatorio/relatorio_P3.md)
