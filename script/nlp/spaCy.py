import warnings
warnings.filterwarnings('ignore')

# Import des bibliothèques nécessaires
import pymongo
from neo4j import GraphDatabase
import spacy

def main():
    # Connexion à la base de données MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["dbDocument"]
    collection = db["test"]

    setModel = {'fr':'fr_core_news_lg',
                'ang':'en_core_web_lg'}

    # Initialisation du modèle NER spaCy
    nlp = spacy.load(setModel['fr'])

    # Connexion à Neo4j
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

    # Boucle sur tous les documents de la collection MongoDB
    for document in collection.find():
        # Création d'un noeud pour le document dans Neo4j
        with driver.session() as session:
            query = "MERGE (d:Document {id: $id, title: $title})"
            session.run(query, id=str(document["_id"]), title=document["title"])
		
        segments = segment_text(document['content'], 200)
        for segment in segments:
            # Chargement du corpus
            doc = nlp(segment)
            # Extraction 
            for ent in doc.ents:
                text = " ".join(ent.text.replace("\n", " ").replace("  ", " ").split())
                if ent.label_ not in ['CARDINAL', 'ORDINAL']:
                    if len(ent.text.strip()) > 4 and len(ent.text.strip()) < 20:
                    # print(ent.text, ent.label_)
                        with driver.session() as session:
                            query = "MERGE (n:NamedEntity {name: $name, entity: $entity})"
                            session.run(query, name=text, entity=ent.label_)

                # Création d'une relation entre le document et chaque NER dans Neo4j
                with driver.session() as session:
                    query = """
                                MATCH (d:Document), (n:NamedEntity) 
                                WHERE d.id = $document_id
                                AND n.name = $ner_name 
                                MERGE (d)-[:HAS_ENTITY]->(n)
                            """
                    session.run(query, document_id=str(document["_id"]), ner_name=text)

def segment_text(text, chunk_size):
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

if __name__ == "__main__":
    main()
