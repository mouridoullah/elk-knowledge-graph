from pymongo import MongoClient
from tika import parser
import os


client = MongoClient('mongodb://localhost:27017/')
db = client['dbDocument']
collection = db['test']

folder_path = {'fr':"/home/mandiaye/LORIA/dataPdf",
               'ang':"/home/mandiaye/LORIA/pdfs-master/essaie/dodo"}

file_names = os.listdir(folder_path['ang'])


# loop through the file names
for file_name in file_names:
    # construct the full path to the file
    file_path = os.path.join(folder_path['ang'], file_name)
    
    # parse the file with Tika
    parsed = parser.from_file(file_path)
    
    # extract the content and metadata
    content = parsed["content"]
    metadata = parsed["metadata"]
    
    # filter the metadata for "title", "creator" and "created"
    title = metadata.get("pdf:docinfo:title")
    creator = metadata.get("pdf:docinfo:creator")
    created = metadata.get("pdf:docinfo:created")
    
    if content is None:
        continue
    # create a document to insert into MongoDB
    document = {
        "content": " ".join(content.replace("\n", " ").replace("  ", " ").split()),
        "title": " ".join(file_name.rsplit(".", 1)[0].replace("\n", " ").replace("  ", " ").split()),
        "creator": creator,
        "created": created
        # "file_name": file_name
    }
    # print(document)
    # insert the document into the collection
    collection.insert_one(document)

# close the MongoDB connection
client.close()
