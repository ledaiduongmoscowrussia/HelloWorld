from pymongo import MongoClient
MONGO_URI = 'mongodb://ledaiduongvnth:leduysao290893@ds225028.mlab.com:25028/checkscoretin'
client = MongoClient(MONGO_URI)
db = client.get_database()


def AddDocumentToColection(colection, document):
    col = db[colection]
    doc_id = col.insert_one(document).inserted_id
    return doc_id
def ReadDocumentFromColection(colection, dict):
    col = db[colection]
    docs = col.find(dict)
    return docs
def ReadNumberOfDocuments(colection):
    col = db[colection]
    num = col.count()
    return num

