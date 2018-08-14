from pymongo import MongoClient

MONGODB_NAME = 'adtech'
MONGODB_TABLE = 'measure'

class Mongodb_helper(object):
    def __init__(self):
        self.client = MongoClient("localhost",27017)
        self.db = self.client[MONGODB_NAME]
        self.collection = self.db[MONGODB_TABLE]
    
    def Insert_Record(self, record):
        try:
            existing = self.collection.find({'image_name':record['image_name']})
            if existing.count() <=0:
                self.collection.insert(record)
                print('inserted record: ' + str(record))
        except Exception as e:
            print('Can not insert the record: {0}. Due to {1}'.format(str(record), e.__str__()))
    
    
    
    def Query(self, query_string, sort_string=None, top=10):
        try:
            if sort_string is None:
                return self.collection.find(query_string).limit(top)
            return self.collection.find(query_string).sort(sort_string, -1).limit(top)
        except Exception as e:
            print("Can not query the string. Due to {0}".format(e.__str__())) 

    def Drop_DataBase(self, databaseName):
        self.client.drop_database(databaseName)

def Clear_AllRecords_In_Table(databaseName, tableName, client):
    db = client[databaseName]
    collection = db[tableName]
    collection.remove()

def Insert_Data_IntoMongoDB(databBaseName, tableName, client, valueDic, updateColumn = '', updateKey = ''):
    db = client[databBaseName]
    collection = db[tableName]
    if updateColumn == '':
        collection.insert_one(valueDic)
    else:
        queryFilter = {updateColumn : updateKey}
        record = collection.find_one(queryFilter)
        if record is not None:
            collection.update_one(queryFilter, {'$set': valueDic})
        else:
            collection.insert_one(valueDic)