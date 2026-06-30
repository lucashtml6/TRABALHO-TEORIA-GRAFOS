# EC9 — Tempo medio do Dijkstra (vetor vs heap)

| grafo         | n       | m         | heap (ms/fonte) | k_heap | vetor (ms/fonte) | k_vetor | speedup vec/heap |
|---------------|---------|-----------|-----------------|--------|------------------|---------|------------------|
| grafo_W_1.txt | 10,000  | 209,957   | 102.32          | 100    | 2850.85          | 100     | 27.9×            |
| grafo_W_2.txt | 25,000  | 824,937   | 606.87          | 100    | 17859.04         | 30      | 29.4×            |
| grafo_W_3.txt | 100,000 | 6,099,868 | 17223.78        | 100    | 497288.28        | 5       | 28.9×            |

Observacao: a versao com vetor e Theta(V^2). Em grafos grandes
reduzimos `k_vetor` para que o estudo termine — o tempo *medio* por
fonte permanece comparavel entre as colunas.

### Grafos pulados

- **grafo_W_4.txt** (n = 1.000.000): INVIAVEL — carga ultrapassa a memoria disponivel
  (Python atinge ~8,5 GB de RSS quando restam apenas 1,4 GB livres do sistema de 16 GB).
- **grafo_W_5.txt** (n = 10.000.000): INVIAVEL — mesma razao, escala ainda maior.

Para esses grafos seria necessario um loader otimizado (numpy.loadtxt + CSR) e/ou mais RAM.
