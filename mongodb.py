from pymongo import MongoClient
from MongoDB_settingsVlad import MONGODB, MONGODB_LINK,CLUSTER


mdb=MongoClient(MONGODB_LINK)[CLUSTER][MONGODB]
