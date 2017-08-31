from pymongo import MongoClient
import datetime
import sys

def TestCappedDB():
    #print "Starting SaveToMongoDB"

    # Create the collection and Indexes
    try:
        client = MongoClient("172.25.11.94", 27017, connect=False)
        # client = MongoClient("172.25.11.23", 27017)
        # Specify the database name at that IP address. (Database Name = InternetDashboard)
        db = client.test2
    except:
        print "Couldn't connect to %(server)s , is MongoDB running?" % {'server': "172.11.25.94"}
        sys.exit(1)

    # Add db command to collections to the databases if they don't exist
    try:
        db_collections = db.collection_names()

        if 'results' not in db_collections:
            db.create_collection('results', capped=True, size=500, max=500)

        for x in range(0,1000):
            res = {}
            res['entry'] = x
            res['createdAt'] = datetime.datetime.now() # Get the time now in UTC format
            dbResult = db.results.insert_one(res)

    except Exception as e:
        print e

def main(argv):
    # Jan 1 2017 = 1483228800
    # Jan 10 2017 = 1484006400
    #saveToMongoDB(1483228800, 1484006400)
    TestCappedDB()


if __name__ == '__main__':
    main(sys.argv[1:])