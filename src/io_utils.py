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
    directed: bool = False,
    reverse: bool = False,
) -> Graph:
    """
    Le um grafo de um arquivo texto.

    Formato esperado:
        - linha 1: numero de vertices N
        - linhas seguintes: 'u v' (Parte 1) ou 'u v w' (Parte 2, w = peso real)

    O formato (ponderado ou nao) e detectado automaticamente pelo numero de
    tokens na primeira aresta (2 -> nao ponderado; 3 -> ponderado).

    `directed` (Parte 3): se True, cada linha 'u v [w]' representa o arco
    direcionado u -> v (a direcao segue a ordem dos vertices na linha). Se
    False (default), a aresta e nao-direcionada (compatibilidade Parte 1/2).

    `reverse`: se True (so faz sentido com directed=True), inverte cada arco
    na carga (u -> v vira v -> u), produzindo o grafo transposto sem custo de
    memoria extra. Util para o estudo de caso "distancia ATE o vertice 100".

    O loader e otimizado para grafos grandes: le o arquivo inteiro de uma
    vez, faz um unico `str.split()`, e popula a lista de adjacencia
    *diretamente* (bypass do `add_edge`, que faria validacao por aresta).
    Para `representation='matrix'`, usamos `add_edge` normal (a matriz
    nao se beneficia tanto, e e usada apenas em grafos pequenos).

    Comentarios iniciados com '#' ou linhas em branco sao ignorados — mas
    apenas no cabecalho. Para arquivos muito grandes assumimos formato
    estrito ja a partir da primeira aresta.
    """
    path = Path(path)
    if representation == "list":
        return _load_list_fast(path, dedup, directed, reverse)
    elif representation == "matrix":
        return _load_matrix(path, dedup, directed, reverse)
    else:
        raise ValueError(
            f"representation deve ser 'list' ou 'matrix', recebido: {representation!r}"
        )


def _load_list_fast(
    path: Path, dedup: bool, directed: bool = False, reverse: bool = False
) -> Graph:
    """Loader rapido especifico para lista de adjacencia.

    Le todo o arquivo de uma vez, tokeniza em uma chamada e popula
    diretamente `_adj`. Em grafos grandes (milhoes de arestas), e
    ~5-10x mais rapido que iterar linha a linha.
    """
    with path.open("r", encoding="utf-8") as f:
        # 1) consome cabecalhos (linhas em branco / comentarios) e le N
        n = None
        while n is None:
            line = f.readline()
            if not line:
                raise ValueError(f"arquivo vazio ou sem header: {path}")
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            try:
                n = int(s)
            except ValueError as e:
                raise ValueError(
                    f"primeira linha deve ser o numero de vertices, encontrei: {s!r}"
                ) from e

        # 2) le o resto do arquivo de uma vez (texto bruto)
        rest = f.read()

    graph = GraphList(n, directed=directed)
    if not rest.strip():
        return graph  # grafo sem arestas

    tokens = rest.split()
    n_tok = len(tokens)
    if n_tok == 0:
        return graph

    # 3) detecta formato a partir do numero total de tokens vs numero de linhas
    #    (estimativa pela primeira linha)
    first_nl = rest.find("\n")
    first_line = rest[:first_nl] if first_nl != -1 else rest
    first_parts = first_line.split()
    if len(first_parts) == 2:
        weighted = False
        cols = 2
    elif len(first_parts) == 3:
        weighted = True
        cols = 3
    else:
        raise ValueError(
            f"primeira aresta mal formatada (esperado 'u v' ou 'u v w'): {first_line!r}"
        )
    if n_tok % cols != 0:
        raise ValueError(
            f"numero de tokens ({n_tok}) nao e multiplo de {cols} — arquivo malformado"
        )

    # 4) preenche _adj diretamente — bypass add_edge para velocidade.
    #    Em grafo direcionado registramos so o arco u -> v (ou v -> u se
    #    reverse=True); em grafo nao-direcionado registramos as duas pontas.
    adj = graph._adj
    has_neg = False
    weighted_flag = False
    if weighted:
        m = 0
        for i in range(0, n_tok, 3):
            u = int(tokens[i])
            v = int(tokens[i + 1])
            if u == v:
                continue
            w = float(tokens[i + 2])
            if directed:
                if reverse:
                    adj[v].append((u, w))
                else:
                    adj[u].append((v, w))
            else:
                adj[u].append((v, w))
                adj[v].append((u, w))
            m += 1
            if w != 1.0:
                weighted_flag = True
            if w < 0.0:
                has_neg = True
    else:
        m = 0
        for i in range(0, n_tok, 2):
            u = int(tokens[i])
            v = int(tokens[i + 1])
            if u == v:
                continue
            if directed:
                if reverse:
                    adj[v].append((u, 1.0))
                else:
                    adj[u].append((v, 1.0))
            else:
                adj[u].append((v, 1.0))
                adj[v].append((u, 1.0))
            m += 1

    graph._m = m
    graph._is_weighted = weighted_flag or weighted
    graph._has_negative_weight = has_neg

    if dedup:
        graph.deduplicate()
    return graph


def _load_matrix(
    path: Path, dedup: bool, directed: bool = False, reverse: bool = False
) -> Graph:
    """Loader linha-a-linha para matriz. Mantemos o caminho simples — a
    matriz e usada so em grafos pequenos onde performance nao e critica."""
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

        graph = GraphMatrix(n, directed=directed)
        weighted = None

        for line_num, raw in enumerate(f, start=2):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if weighted is None:
                weighted = len(parts) == 3
            u, v = int(parts[0]), int(parts[1])
            if directed and reverse:
                u, v = v, u
            if weighted:
                graph.add_edge(u, v, float(parts[2]))
            else:
                graph.add_edge(u, v)

        if weighted:
            graph._mark_weighted()

    if dedup:
        graph.deduplicate()
    return graph


def _fix_mojibake(s: str) -> str:
    """Tenta corrigir UTF-8 duplamente codificado (mojibake CP1252-via-UTF-8).

    Se a string contem sequencias caracteristicas de mojibake (ex. 'Ã‰' para
    'É', 'Ã¡' para 'á'), reencodamos como CP1252 e re-decodificamos como
    UTF-8. Em caso de falha (a string ja estava certa), retornamos o original.
    """
    if "Ã" not in s and "Â" not in s:
        return s
    try:
        return s.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def load_vertex_labels(
    path: PathLike,
    fix_mojibake: bool = True,
) -> tuple[dict[int, str], dict[str, int]]:
    """Le um arquivo de mapeamento 'id,nome' (uma linha por vertice).

    Retorna (id_to_name, name_to_id). Usado pela rede de colaboracao
    (estudos da Parte 2). Encoding UTF-8.

    Se fix_mojibake=True (default), tenta corrigir nomes que sofreram
    dupla codificacao (UTF-8 lido como CP1252 e re-encodado em UTF-8) —
    sintoma comum em arquivos editados em editores Windows com encoding
    errado. Sem isso, "Éva Tardos" aparece como "Ã‰va Tardos" no Python.
    """
    path = Path(path)
    id_to_name: dict[int, str] = {}
    name_to_id: dict[str, int] = {}
    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\r\n")
            if not line:
                continue
            idx = line.find(",")
            if idx == -1:
                continue
            try:
                vid = int(line[:idx])
            except ValueError:
                continue
            name = line[idx + 1:].strip()
            if fix_mojibake:
                name = _fix_mojibake(name)
            id_to_name[vid] = name
            name_to_id[name] = vid
    return id_to_name, name_to_id


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
