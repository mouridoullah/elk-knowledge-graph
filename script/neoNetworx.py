from neo4j import GraphDatabase
import networkx as nx
import matplotlib.pyplot as plt

def main():
    # Connecter à la base de données Neo4j
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
    session = driver.session()

    # Requête Cypher pour récupérer les données de Neo4j
    query = 'MATCH (n)-[r]->(m) RETURN n,r,m'
    results = session.run(query)

    # Créer un graphe NetworkX à partir des données de Neo4j
    G = nx.Graph()
    for result in results:
        G.add_edge(result['n']['title'], result['m']['title'])
        # print(result['r']["keywords"])

    # Trouver tous les sous-graphes complets
    subgraphs = nx.find_cliques(G)

    # Afficher chaque sous-graphe complet
    for subgraph in subgraphs:
        print(subgraph, "taille: ",len(subgraph))
        H = G.subgraph(subgraph)
        nx.draw(H)
        plt.show()

    session.close()

if __name__ == "__main__":
    main()