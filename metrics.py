import pandas as pd
import networkx as nx
import numpy as np


def calculate_network_metrics(passes_df):
    """
    Função baseada em rede jogador-jogador.
    Mantida apenas para análise auxiliar ou comparação histórica.
    Não representa a metodologia principal de redes espaciais por zonas.
    """

    G = nx.DiGraph()

    for _, row in passes_df.iterrows():
        G.add_edge(
            row['playerId'],
            row['passRecipientId'],
            weight=max(float(row.get('EPV', 0.0)), 0.0)
        )

    metrics = {}

    if G.number_of_nodes() == 0 or G.number_of_edges() == 0:
        return {
            'coeficiente_de_agrupamento_local': 0.0,
            'densidade': 0.0,
            'comprimento_medio_do_caminho_mais_curto': np.nan,
            'dispersao_da_centralidade': 0.0,
            'maximo_autovalor': 0.0,
            'centralidade_de_intermediacao_media': 0.0,
            'pagerank_medio': 0.0,
            'pagerank_maximo': 0.0,
            'pagerank_desvio': 0.0,
            'pagerank_entropia': 0.0,
        }

    metrics['coeficiente_de_agrupamento_local'] = nx.average_clustering(G, weight='weight')
    metrics['densidade'] = nx.density(G)

    subgraphs = [G.subgraph(c).copy() for c in nx.strongly_connected_components(G) if len(c) > 1]

    if subgraphs:
        metrics['comprimento_medio_do_caminho_mais_curto'] = float(np.mean([
            nx.average_shortest_path_length(subgraph, weight='weight')
            for subgraph in subgraphs
        ]))
    else:
        metrics['comprimento_medio_do_caminho_mais_curto'] = np.nan

    degree_centrality = nx.degree_centrality(G)
    metrics['dispersao_da_centralidade'] = float(np.std(list(degree_centrality.values())))

    adjacency_matrix = nx.adjacency_matrix(G, weight='weight').todense()
    eigenvalues = np.linalg.eigvals(adjacency_matrix)
    metrics['maximo_autovalor'] = float(np.max(np.abs(eigenvalues)))

    betweenness_centrality = nx.betweenness_centrality(G, weight='weight', normalized=True)
    metrics['centralidade_de_intermediacao_media'] = float(np.mean(list(betweenness_centrality.values())))

    pagerank = nx.pagerank(G, weight='weight')

    if pagerank:
        pr_vals = np.array(list(pagerank.values()), dtype=float)

        metrics['pagerank_medio'] = float(np.mean(pr_vals))
        metrics['pagerank_maximo'] = float(np.max(pr_vals))
        metrics['pagerank_desvio'] = float(np.std(pr_vals))

        eps = 1e-12
        pr_entropy = float(-(pr_vals * np.log(pr_vals + eps)).sum())
        metrics['pagerank_entropia'] = float(pr_entropy / np.log(len(pr_vals) + eps))
    else:
        metrics['pagerank_medio'] = 0.0
        metrics['pagerank_maximo'] = 0.0
        metrics['pagerank_desvio'] = 0.0
        metrics['pagerank_entropia'] = 0.0

    return metrics