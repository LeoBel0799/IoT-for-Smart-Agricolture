from coapthon.client.helperclient import HelperClient
import json
from database import Database
import tabulate
import logging
import time
import datetime

class MotionResource :
    def __init__(self,source_address,resource):
        # Initialize mote resource fields
        self.db = Database()
        self.connection = self.db.connect_dbs()
        print("Conncected to Collector DB")
        self.address = source_address
        self.resource = resource
        self.actuator_resource = "alert_actuator"
        self.isClosed = "F";
        self.opening = 90;
        self.isActive = "F";
        # Start observing for updates
        self.start_observing()
        print("Motion resource inizitialized")

    def presence_callback_observer(self, response):
        print("Callback called, resource arrived")
        print(response.payload)
        if response.payload is not None:
            print(response.payload)
            nodeData = json.loads(response.payload)
            # read from payload of client
            isClosed = nodeData["closed"].split(" ")
            info = nodeData["active"].split(" ")
            opening = nodeData["opening"].split(" ")
            print("Detection value node :")
            print(isClosed)
            print(info)
            print(opening)
            self.isClosed = isClosed[0]
            self.isActive = info[0]
            self.opening = opening[0];
            # when occour an intrusion a query is executed
            if self.isClosed == 'T':
                response = self.client.post(self.actuator_resource,"state=1")
                # query quando è aperto
                self.execute_query_motion(1)
            else:
                response = self.client.post(self.actuator_resource,"state=0")
                self.execute_query_motion(0)
        else:
            print("Payload empty")
            return;



    def execute_query_motion(self, closed):
        print(self.connection)
        with self.connection.cursor() as cursor:
            ts = time.time()
            timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            opening = str(self.opening)
            activation = str(self.isActive)
            sql = "INSERT INTO `coapsensorsmotion` (`closed`,`activation`,`opening`,`timestamp`) VALUES (%s,%s,%s,%s)"
            cursor.execute(sql, (closed,activation,opening,timestamp))



        self.connection.commit()
        # Show data log
        with self.connection.cursor() as cursor2:
            sql = "SELECT * FROM `coapsensorsmotion`"
            cursor2.execute(sql)
            results = cursor2.fetchall()
            header = results[0].keys()
            rows = [x.values() for x in results]
            print(tabulate.tabulate(rows,header,tablefmt='grid'))



    def start_observing(self):
        logging.getLogger("coapthon.server.coap").setLevel(logging.WARNING)
        logging.getLogger("coapthon.layers.messagelayer").setLevel(logging.WARNING)
        logging.getLogger("coapthon.client.coap").setLevel(logging.WARNING)
        self.client = HelperClient(self.address)
        self.client.observe(self.resource,self.presence_callback_observer)