
from coapthon.client.helperclient import HelperClient
import json
from database import Database
import tabulate
import logging

class AlertResource :
    def __init__(self,source_address,resource):
        # Initialize mote resource fields
        self.db = Database()
        self.connection = self.db.connect_dbs()
        self.address = source_address
        self.resource = resource
        self.actuator_resource = "alert_actuator"
        self.intensity = 90;
        self.isActive = "F";
        # Start observing for updates
        self.start_observing()
        print("Mechanical cover actuator initialized")


    def presence_callback_observer(self, response):
        print("Callback called, resource arrived")
        if response.payload is not None:
            print(response.payload)
            nodeData = json.loads(response.payload)
            # read from payload of client
            active = nodeData["active"].split(" ")
            degreeOp = nodeData["degreeOpening"].split(" ")
            print("Detection mechanical cover degree status :")
            print(active)
            print(degreeOp)
            self.closed = active[0]
            self.degree = degreeOp[0];
            # when an intrusion occurs a query is executed
            if self.closed == 'T':
                #response = self.client.post(self.actuator_resource,"state=1")
                self.execute_query(1)
            else:
                #response = self.client.post(self.actuator_resource,"state=1")
                self.execute_query(0)

    def execute_query(self , value):
        print(self.connection)
        with self.connection.cursor() as cursor:
            intensity = str(self.intensity)
            sql = "INSERT INTO `coapsensorsalarm` (`active`, `degreeOp`) VALUES (%s, %s)"
            cursor.execute(sql, (value, intensity))
        # connection is not autocommit by default. So you must commit to save
        # your changes.
        self.connection.commit()
        # Show data log
        with self.connection.cursor() as cursor2:
            sql = "SELECT * FROM `coapsensorsalarm`"
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
