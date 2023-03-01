import warnings
warnings.filterwarnings('ignore')

# Import des bibliothèques nécessaires
import pymongo
from neo4j import GraphDatabase
from transformers import pipeline
import wikipediaapi

def wikipedia_page_exists(title):
    wiki = wikipediaapi.Wikipedia('en')
    page = wiki.page(title)
    return page.exists()

# Function to parse the generated text and extract the triplets
def extract_triplets(text):
    triplets = []
    relation, subject, relation, object_ = '', '', '', ''
    text = text.strip()
    current = 'x'
    for token in text.replace("<s>", "").replace("<pad>", "").replace("</s>", "").split():
        if token == "<triplet>":
            current = 't'
            if relation != '':
                triplets.append({'head': subject.strip(), 'type': relation.strip(),'tail': object_.strip()})
                relation = ''
            subject = ''
        elif token == "<subj>":
            current = 's'
            if relation != '':
                triplets.append({'head': subject.strip(), 'type': relation.strip(),'tail': object_.strip()})
            object_ = ''
        elif token == "<obj>":
            current = 'o'
            relation = ''
        else:
            if current == 't':
                subject += ' ' + token
            elif current == 's':
                object_ += ' ' + token
            elif current == 'o':
                relation += ' ' + token
    if subject != '' and relation != '' and object_ != '':
        triplets.append({'head': subject.strip(), 'type': relation.strip(),'tail': object_.strip()})
    return triplets

def segment_text(text, chunk_size):
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

# Créez une instance de GraphDatabase
uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))

triplet_extractor = pipeline('text2text-generation', model='Babelscape/rebel-large', tokenizer='Babelscape/rebel-large')
ner_model = pipeline('ner', model='Jean-Baptiste/roberta-large-ner-english', tokenizer='Jean-Baptiste/roberta-large-ner-english', aggregation_strategy="simple")

# Connexion à la base de données MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["dbDocument"]
collection = db["test"]

# Boucle sur tous les documents de la collection MongoDB
for document in collection.find():    
    segments = segment_text(document['content'], 200)
    
    for segment in segments:
        # We need to use the tokenizer manually since we need special tokens.
        extracted_text = triplet_extractor.tokenizer.batch_decode([triplet_extractor(segment, return_tensors=True, return_text=False)[0]["generated_token_ids"]])

        extracted_triplets = extract_triplets(extracted_text[0])
        # Exécutez une transaction pour ajouter des nœuds et des relations au graphe

        with driver.session() as session:
            for triplet in extracted_triplets:
                ner_head = ner_model(triplet['head'])
                ner_tail = ner_model(triplet['tail'])

                for dict1, dict2 in zip(ner_head, ner_tail):
                    wordHead, entityHead = dict1['word'].strip(), dict1['entity_group']
                    wordTail, entityTail = dict2['word'].strip(), dict2['entity_group']
                    relation_type = triplet['type'].replace(' ', '_').split("<")[0].strip()

                    page = wikipedia_page_exists(wordHead)
                    if page:
                        session.run("MERGE (h:" + entityHead + " {name: $head}) "
                                    "MERGE (t:" + entityTail + " {name: $tail}) "
                                    "MERGE (h)-[:" + relation_type + "]->(t) "
                                    "WITH h, t "
                                    "MERGE (a:Document{id: $id, title: $title}) "
                                    "WITH a, h, t "
                                    "MERGE (a)-[:MENTIONED]->(h) "
                                    "MERGE (a)-[:MENTIONED]->(t)",head=wordHead, tail=wordTail, id=str(document["_id"]), title=document["title"])
                    else:
                        continue



