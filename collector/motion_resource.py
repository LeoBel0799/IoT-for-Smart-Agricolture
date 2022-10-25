
from coapthon.client.helperclient import HelperClient
import json
from database import Database
import tabulate
import logging

class MotionResource :
    def __init__(self,source_address,resource):
        # Initialize mote resource fields
        self.db = Database()
        self.connection = self.db.connect_dbs()
        self.address = source_address
        self.resource = resource
        self.actuator_resource = "alert_actuator"
        self.isDetected = "F";
        self.intensity = 10;
        self.isActive = "F";
        # Start observing for updates
        self.start_observing()
        print("Mechanical Cover inizitialized")

    def presence_callback_observer(self, response):
        print("Callback called, resource arrived")
        print(response.payload)
        if response.payload is not None:
            print(response.payload)
            nodeData = json.loads(response.payload)
            # read from payload of client
            closed = nodeData["closed"].split(" ")
            active = nodeData["active"].split(" ")
            degreeOpen = nodeData["opening degree"].split(" ")
            print("Detection value node :")
            print(closed)
            print(active)
            print(degreeOpen)
            self.closed = closed[0]
            self.active = active[0]
            self.degreeOpening = degreeOpen[0];
            # when occour an intrusion a query is executed
            if self.closed == 'T':
                response = self.client.post(self.actuator_resource,"state=1")
                # query quando è aperto
                self.execute_query_cover(1)
            else:
                response = self.client.post(self.actuator_resource,"state=0")
                self.execute_query_cover(0)
        else:
            return;



    def execute_query_cover(self, value):

        print(self.connection)
        with self.connection.cursor() as cursor:
            degree = str(self.degreeOpening)
            on = str(self.active)
            sql = "INSERT INTO `coapsensorsmotion` (`value`,`on`,`degree`) VALUES (%s,%s,%s)"
            cursor.execute(sql, (value,on,degree))

        # connection is not autocommit by default. So you must commit to save
        # your changes.
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
