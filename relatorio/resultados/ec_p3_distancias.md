# EC-P3 — Distancias dos vertices 10, 20 e 30 ate o vertice 100

Distancias obtidas rodando o algoritmo de fonte unica a partir do
vertice 100 sobre o grafo com as **arestas invertidas** (d(v→100) = d_invertido(100→v)).

| grafo         | algoritmo    | d(10→100) | d(20→100) | d(30→100) | ciclo neg. |
|---------------|--------------|-----------|-----------|-----------|------------|
| grafo_W_1.txt | Bellman-Ford | 8.3000    | 3.5900    | 6.6800    | SIM        |
| grafo_W_2.txt | Bellman-Ford | 10.4700   | 8.4800    | 8.7100    | nao        |
| grafo_W_2.txt | Dijkstra     | 10.4700   | 8.4800    | 8.7100    | —          |
| grafo_W_3.txt | Bellman-Ford | 4.6300    | 5.4200    | 4.6700    | nao        |
| grafo_W_3.txt | Dijkstra     | 4.6300    | 5.4200    | 4.6700    | —          |

### Notas

- **grafo_W_1.txt**: possui arestas negativas — Dijkstra inaplicavel; apenas Bellman-Ford.
