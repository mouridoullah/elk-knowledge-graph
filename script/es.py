from elasticsearch import Elasticsearch
from neo4j import GraphDatabase

def main():
    # Connexion à la base de données Neo4j et Elasticsearch
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
    session = driver.session()
    es = Elasticsearch("http://localhost:9200")

    term = input("Entrez une chaîne de caractères (appuyez sur Entrée pour quitter) : ")

    while term != "":
        source = ['file_name', 'title', 'creator', 'created', 'mongo_id']
        documents = es.search(index="mongo_index", query={"match": {"content": term}}, source=source) # , size=3

        print("Got %d Hits:" % documents['hits']['total']['value'])
        # Print the keys of the response
        for document in documents['hits']['hits']:
            print(document)


            id = document["_source"]["mongo_id"]
            # filename = document["_source"]["file_name"]
            title = document["_source"]["title"]
            try:

                creator = document["_source"]["creator"]
                created = document["_source"]["created"]
            except KeyError:
                # title = filename = document["_source"]["file_name"]
                creator = "unknown"
                created = "unknown"

        # trier la liste selon la clé "score"
        # data.sort(key=lambda x: x["_score"])

            query = """
                        MERGE (d:Document {id: $id})
                        ON CREATE SET d.title = $title
                        SET d.creator = $creator
                        SET d.created = $created
                    """
            session.run(query, id=id, title=title, creator=creator, created=created)

        # Boucle pour créer les relations
        
        for i in range(len(documents['hits']['hits'])):
            for j in range(i+1, len(documents['hits']['hits'])):
                query = """
                            MATCH (a:Document),(b:Document) 
                            WHERE a.id = $node_id_1 AND b.id = $node_id_2 
                            MERGE (a)-[r:RELATES_TO]-(b) 
                            ON CREATE SET r.keywords = [$term] 
                            ON MATCH SET r.keywords = r.keywords + $term
                        """
                node_id_1 = documents['hits']['hits'][i]["_source"]["mongo_id"]
                node_id_2 = documents['hits']['hits'][j]["_source"]["mongo_id"]
                session.run(query, {"node_id_1": node_id_1, "node_id_2": node_id_2, "term": term})


        term = input("Entrez une chaîne de caractères (appuyez sur Entrée pour quitter) : ")

    session.close()

if __name__ == "__main__":
    main()

# """
# "match": cette requête permet de rechercher un terme ou une phrase dans un champ spécifique. 
#           Elle est utilisée pour effectuer des recherches de type "correspondance exacte".

# "fuzzy": cette requête permet de rechercher un terme ou une phrase en utilisant une recherche approximative. 
#           Elle est utilisée pour effectuer des recherches de type "recherche de proximité".

# "term": cette requête permet de rechercher un terme exact dans un champ spécifique. 
#           Elle est utilisée pour effectuer des recherches de type "correspondance exacte" sur des
#            champs qui ne sont pas analysés, comme les champs numériques ou les champs booléens.

# "range": cette requête permet de rechercher des documents qui ont des valeurs dans un certain intervalle pour un champ spécifique.

# "bool": cette requête permet de combiner plusieurs requêtes en utilisant 
#           des opérateurs booléens (ET, OU, NOT) pour affiner les résultats de recherche.

# "nested": cette requête permet de rechercher dans des champs qui sont des objets imbriqués.
# """

# """
# body = {
#     "query": {
#         "match": {
#             "field_name": "search term"
#         }
#     }
# }

# body = {
#     "query": {
#         "term": {
#             "field_name": "search term"
#         }
#     }
# }

# body = {
#     "query": {
#         "fuzzy": {
#             "field_name": {
#                 "value": "search term",
#                 "fuzziness": 2
#             }
#         }
#     }
# }

# body = {
#     "query": {
#             "wildcard": {
#                 "message": {
#                     "value": "chat*"
#                 }
#             }
#         }
#     }
# }

# body = {
#     "query": {
#         "range": {
#             "field_name": {
#                 "gte": "lower_bound",
#                 "lte": "upper_bound"
#             }
#         }
#     }
# }

# body = {
#     "query": {
#         "bool": {
#             "must": [
#                 {"match": {"field_name": "search term 1"}},
#                 {"match": {"field_name": "search term 2"}}
#             ],
#             "must_not": {
#                 "match": {"field_name": "search term 3"}
#             }
#         }
#     }
# }

# body = {
#     "query": {
#         "nested": {
#             "path": "nested_field_name",
#             "query": {
#                 "match": {
#                     "nested_field_name.sub_field_name": "search term"
#                 }
#             }
#         }
#     }
# }
# """

# killall5 -9

# MATCH ()-[r]-() RETURN r ORDER BY size(r.keywords) DESC
# MATCH (n)-[r]->(m) WHERE 'web' in r.keywords RETURN *
# MATCH (n) WHERE n.titre in ['strong', 'especially', 'wall', 'pull', 'box', 'ever', 'respond'] return *


# /home/mandiaye/anaconda3/bin/python -m pip install wikipedia-api