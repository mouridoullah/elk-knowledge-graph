# Import des bibliothèques nécessaires
import pymongo
from transformers import pipeline
from neo4j import GraphDatabase
from transformers import AutoTokenizer, AutoModelForTokenClassification

def main():
    # Connexion à la base de données MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["dbDocument"]
    collection = db["test"]

    setModel = {'fr':'Jean-Baptiste/camembert-ner', 
                'ang':'Jean-Baptiste/roberta-large-ner-english'}
    
    # Initialisation du modèle NER HuggingFace francais
    tokenizer = AutoTokenizer.from_pretrained(setModel["fr"])
    model = AutoModelForTokenClassification.from_pretrained(setModel["fr"])

    ner_model = pipeline('ner', model=model, tokenizer=tokenizer, aggregation_strategy="simple")

    # Connexion à Neo4j
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

    # Boucle sur tous les documents de la collection MongoDB
    for document in collection.find():
        # Création d'un noeud pour le document dans Neo4j
        with driver.session() as session:
            session.run("MERGE (d:Document {id: $id, title: $title})", id=str(document["_id"]), title=document["title"])
            
        segments = segment_text(document['content'], 200)
        for segment in segments:

            # Extraction des NER à partir du contenu du document
            ner_output = ner_model(segment)
            # afficherEntity(ner_model, ner_output)
            # Boucle sur tous les NER extraits
            for entity in ner_output:
                text = " ".join(entity["word"].replace("\n", " ").replace("  ", " ").split())
                # Création d'un noeud pour chaque NER dans Neo4j
                if len(entity["word"].strip()) > 4:
                    # if entity["entity_group"] not in ['MISC']:
                        with driver.session() as session:
                            session.run("MERGE (n:NamedEntity {name: $name, entity: $entity})", name=text, entity=entity["entity_group"])
                
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

def afficherEntity(ner, nes):
    cur = None
    agg = []
    for ne in nes: 
        entity=ne['entity_group']
        if entity != cur: 
            if cur is None: 
                cur = entity
            if agg: 
                print(cur, ner.tokenizer.convert_tokens_to_string(agg))
                agg = []
                cur = entity
        agg.append(ne['word'])
    print(cur, ner.tokenizer.convert_tokens_to_string(agg))
    
if __name__ == "__main__":
    main()


# MATCH (n:Document{id: '63db6e54c106aadd8c36eb5c'})-[:HAS_ENTITY]->(m:NamedEntity) return *