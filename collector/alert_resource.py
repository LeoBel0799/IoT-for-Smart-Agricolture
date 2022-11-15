from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource
from coapthon.client.helperclient import HelperClient
from coapthon.messages.request import Request
from coapthon.messages.response import Response
from coapthon import defines
import json
import time
import server
import threading
from database import Database
import tabulate
import logging
class AlertResource :
    def __init__(self,source_address,resource):
        # Initialize mote resource fields
        self.db = Database()
        self.connection = self.db.connect_dbs()
        print("Conncected to Collector DB")
        self.address = source_address
        self.resource = resource
        self.actuator_resource = "alert_actuator"
        self.opening = 90;
        self.isActive = "F";
        # Start observing for updates
        self.start_observing()
        print("Alert resource initialized")


    def presence_callback_observer(self, response):
        print("Callback called, resource arrived")
        if response.payload is not None:
            print(response.payload)
            nodeData = json.loads(response.payload)
            # read from payload of client
            active = nodeData["active"].split(" ")
            opening = nodeData["opening"].split(" ")
            print("Detection mechanical cover degree status :")
            print(active)
            print(opening)
            self.isClosed = active[0]
            self.opening = opening[0];
            # when an intrusion occurs a query is executed
            if self.isClosed == 'T':
                #response = self.client.post(self.actuator_resource,"state=1")
                self.execute_query(1)
            else:
                #response = self.client.post(self.actuator_resource,"state=1")
                self.execute_query(0)
        else:
            print("Payload empty")


    def execute_query(self , value):
        print(self.connection)
        with self.connection.cursor() as cursor:
            opening = str(self.opening)
            sql = "INSERT INTO `coapsensorsalarm`(`value`, `opening`) VALUES (%s, %s)"
            cursor.execute(sql, (value, opening))
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
