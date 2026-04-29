import statistics
from pathlib import Path
from typing import Literal, Union, TYPE_CHECKING

from .graph_base import Graph
from .graph_list import GraphList
from .graph_matrix import GraphMatrix

if TYPE_CHECKING:
    from .algorithms import ConnectedComponents, SearchResult

Representation = Literal["list", "matrix"]
PathLike = Union[str, Path]


def load_graph(
    path: PathLike,
    representation: Representation = "list",
    dedup: bool = True,
) -> Graph:
    """
    Le um grafo nao-direcionado de um arquivo texto.

    Formato esperado:
        - linha 1: numero de vertices N
        - linhas seguintes: pares "u v" representando arestas
          (vertices em 1..N, separados por espaco ou tab)

    Linhas em branco e comentarios iniciados com '#' sao ignorados.

    Quando dedup=True (padrao), arestas repetidas no arquivo sao
    eliminadas (chamando graph.deduplicate() apos a carga). Em listas
    de adjacencia, a operacao e feita por vertice para evitar pico de
    memoria; em matriz, a propria estrutura ja descarta duplicatas.
    """
    path = Path(path)
    if representation == "list":
        graph_cls = GraphList
    elif representation == "matrix":
        graph_cls = GraphMatrix
    else:
        raise ValueError(
            f"representation deve ser 'list' ou 'matrix', recebido: {representation!r}"
        )

    with path.open("r", encoding="utf-8") as f:
        first = _next_meaningful_line(f)
        if first is None:
            raise ValueError(f"arquivo vazio: {path}")
        try:
            n = int(first)
        except ValueError as e:
            raise ValueError(
                f"primeira linha deve ser o numero de vertices, encontrei: {first!r}"
            ) from e

        graph = graph_cls(n)

        for line_num, raw in enumerate(f, start=2):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) != 2:
                raise ValueError(
                    f"linha {line_num} mal formatada (esperado 'u v'): {line!r}"
                )
            u, v = int(parts[0]), int(parts[1])
            graph.add_edge(u, v)

    if dedup:
        graph.deduplicate()

    return graph


def _next_meaningful_line(f) -> str | None:
    for raw in f:
        line = raw.strip()
        if line and not line.startswith("#"):
            return line
    return None


def write_search_tree(result: "SearchResult", path: PathLike) -> None:
    """Escreve a arvore de busca (BFS ou DFS) em um arquivo texto.

    Formato:
        # cabecalho informando algoritmo, raiz e contagens
        v pai nivel        (uma linha por vertice alcancado)
    Vertices nao alcancados sao listados ao final como comentario.
    """
    path = Path(path)
    n = len(result.level) - 1
    reached = [v for v in range(1, n + 1) if result.level[v] != -1]
    unreached = [v for v in range(1, n + 1) if result.level[v] == -1]

    with path.open("w", encoding="utf-8") as f:
        f.write(f"# algoritmo: {result.algorithm.upper()}\n")
        f.write(f"# raiz: {result.root}\n")
        f.write(f"# vertices alcancados: {len(reached)} / {n}\n")
        f.write("# v pai nivel\n")
        for v in reached:
            f.write(f"{v} {result.parent[v]} {result.level[v]}\n")
        if unreached:
            f.write(f"# vertices nao alcancados ({len(unreached)}): ")
            f.write(" ".join(str(v) for v in unreached[:50]))
            if len(unreached) > 50:
                f.write(f" ... (+{len(unreached) - 50} omitidos)")
            f.write("\n")


def write_components(
    cc: "ConnectedComponents",
    path: PathLike,
    list_vertices: bool = True,
    max_vertices_per_component: int | None = None,
) -> None:
    """Escreve as componentes conexas em um arquivo texto.

    Lista as componentes em ordem decrescente de tamanho.
    Se list_vertices=False, omite a lista de vertices (util para
    grafos enormes onde so o tamanho importa). max_vertices_per_component
    limita quantos vertices de cada componente sao impressos.
    """
    path = Path(path)
    with path.open("w", encoding="utf-8") as f:
        f.write(f"# numero de componentes: {cc.count}\n")
        if cc.count > 0:
            f.write(f"# tamanho da maior: {len(cc.largest)}\n")
            f.write(f"# tamanho da menor: {len(cc.smallest)}\n")
        f.write("\n")
        for idx, comp in enumerate(cc.components, start=1):
            f.write(f"componente {idx}: tamanho={len(comp)}")
            if list_vertices:
                vs = comp
                truncated = False
                if (
                    max_vertices_per_component is not None
                    and len(vs) > max_vertices_per_component
                ):
                    vs = vs[:max_vertices_per_component]
                    truncated = True
                f.write("  vertices: " + " ".join(str(v) for v in vs))
                if truncated:
                    f.write(
                        f" ... (+{len(comp) - max_vertices_per_component} omitidos)"
                    )
            f.write("\n")


def _degree_stats(graph: Graph) -> dict:
    """Calcula min/max/medio/mediano dos graus do grafo."""
    n = graph.n_vertices
    degrees = [graph.degree(v) for v in range(1, n + 1)]
    if n == 0:
        return {"min": 0, "max": 0, "avg": 0.0, "median": 0.0}
    return {
        "min": min(degrees),
        "max": max(degrees),
        "avg": sum(degrees) / n,
        "median": statistics.median(degrees),
    }


def write_summary(
    graph: Graph,
    path: PathLike,
    components: "ConnectedComponents | None" = None,
    include_component_vertices: bool = False,
    max_vertices_per_component: int | None = 20,
) -> None:
    """Gera um arquivo-texto com as estatisticas pedidas pela Funcionalidade 2.

    Inclui: numero de vertices, numero de arestas, grau minimo, grau
    maximo, grau medio, mediana de grau e informacoes das componentes
    conexas (numero, tamanhos e, opcionalmente, lista de vertices).

    Se `components` nao for fornecido, e calculado internamente via
    connected_components(graph).
    """
    if components is None:
        # import local para evitar ciclo
        from .algorithms import connected_components
        components = connected_components(graph)

    stats = _degree_stats(graph)
    path = Path(path)

    with path.open("w", encoding="utf-8") as f:
        f.write("# Resumo do grafo\n")
        f.write(f"n_vertices = {graph.n_vertices}\n")
        f.write(f"n_arestas  = {graph.n_edges}\n")
        f.write(f"grau_min    = {stats['min']}\n")
        f.write(f"grau_max    = {stats['max']}\n")
        f.write(f"grau_medio  = {stats['avg']:.4f}\n")
        f.write(f"grau_mediano= {stats['median']}\n")
        f.write("\n")

        f.write("# Componentes conexas\n")
        f.write(f"n_componentes  = {components.count}\n")
        if components.count > 0:
            f.write(f"maior_tamanho  = {len(components.largest)}\n")
            f.write(f"menor_tamanho  = {len(components.smallest)}\n")
        f.write("\n")

        for idx, comp in enumerate(components.components, start=1):
            f.write(f"componente {idx}: tamanho={len(comp)}")
            if include_component_vertices:
                vs = comp
                truncated = False
                if (
                    max_vertices_per_component is not None
                    and len(vs) > max_vertices_per_component
                ):
                    vs = vs[:max_vertices_per_component]
                    truncated = True
                f.write("  vertices: " + " ".join(str(v) for v in vs))
                if truncated:
                    f.write(
                        f" ... (+{len(comp) - max_vertices_per_component} omitidos)"
                    )
            f.write("\n")
