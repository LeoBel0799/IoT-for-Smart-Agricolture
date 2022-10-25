import pymysql.cursors

# Connect to the database

'''
    Class Database: open a connection through mysql database, to database datacollector containing the coapsensors 
    table (with information about access and logout  , and log of intrution detection) and the mqttsensors (with information about room)
'''
class Database:
    conn = None

    def __init__(self):
        print("Instantiating!")

    def connect_dbs(self):

        if self.conn is not None:
            return self.conn
        else:
            self.conn = pymysql.connect(host='localhost',
                 user='root',
                 password='PASSWORD',
                 database='db',
                 cursorclass=pymysql.cursors.DictCursor)
            return self.conn
