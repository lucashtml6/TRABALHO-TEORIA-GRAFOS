# EC-P3 — Tempo medio de execucao (media de 10 rodadas, sem I/O)

| grafo         | n       | m         | Bellman-Ford (ms) | Dijkstra (ms) | Dijkstra/BF |
|---------------|---------|-----------|-------------------|---------------|-------------|
| grafo_W_1.txt | 25,000  | 549,953   | 0.58              | —             | —           |
| grafo_W_2.txt | 25,000  | 824,964   | 536.29            | 235.57        | 0.44×       |
| grafo_W_3.txt | 100,000 | 6,099,941 | 4832.24           | 3263.40       | 0.68×       |
