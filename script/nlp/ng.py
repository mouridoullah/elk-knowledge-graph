# Import des bibliothèques nécessaires
import pymongo
from transformers import pipeline
from neo4j import GraphDatabase
from transformers import AutoTokenizer, AutoModelForTokenClassification


from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# nltk.download('punkt')
# nltk.download('stopwords')

def main():
    # Connexion à la base de données MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["dbDocument"]
    collection = db["test"]

    # Initialisation du modèle NER HuggingFace
    tokenizer = AutoTokenizer.from_pretrained("Jean-Baptiste/roberta-large-ner-english")
    model = AutoModelForTokenClassification.from_pretrained("Jean-Baptiste/roberta-large-ner-english")
    ner_model = pipeline('ner', model=model, tokenizer=tokenizer, aggregation_strategy="simple")
    # ner_model = pipeline("ner", model="Jean-Baptiste/roberta-large-ner-english")

    # Connexion à Neo4j
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

    # Boucle sur tous les documents de la collection MongoDB
    for document in collection.find():
        # Création d'un noeud pour le document dans Neo4j
        with driver.session() as session:
            session.run("MERGE (d:Document {id: $id, title: $title})", id=str(document["_id"]), title=document["file_name"])
            
        # Extraction des NER à partir du contenu du document
        ner_output = ner_model(document["content"])
        # afficherEntity(ner_model, ner_output)

        # Boucle sur tous les NER extraits
        for entity in ner_output:
            # Création d'un noeud pour chaque NER dans Neo4j
            with driver.session() as session:
                session.run("MERGE (n:NamedEntity {name: $name, entity: $entity})", name=entity["word"], entity=entity["entity_group"])
            
            # Création d'une relation entre le document et chaque NER dans Neo4j
            with driver.session() as session:
                query = """
                            MATCH (d:Document), (n:NamedEntity) 
                            WHERE d.id = $document_id
                            AND n.name = $ner_name 
                            MERGE (d)-[:HAS_ENTITY]->(n)
                        """
                session.run(query, document_id=str(document["_id"]), ner_name=entity["word"])


def segment_text(text, max_len):
    segments = []
    if len(text) <= max_len:
        return [text]
    else:
        start = 0
        end = max_len
        while end < len(text):
            while text[end] != " " and end > start:
                end -= 1
            segments.append(text[start:end].strip())
            start = end
            end += max_len
        segments.append(text[start:].strip())
        return segments

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