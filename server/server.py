# Import package
import paho.mqtt.client as mqtt
from coapthon.server.coap import CoAP
from server import *
import threading
import json
from database import Database
import tabulate
import time
import datetime
import logging


# Define Variables
MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 60
MQTT_TOPIC = "Infos"
MQTT_MSG = "I'm here MQTT"

ip = "::"
port = 5683



class MqttClient():
    # Define on connect event function
    # We shall subscribe to our Topic in this function
    def on_connect(self, client, mosq, obj, rc):
        # mqttc.subscribe(MQTT_TOPIC, 0)
        self.client.subscribe(MQTT_TOPIC, 0)

    # Define on_message event function.
    # This function will be invoked every time,
    # a new message arrives for the subscribed topic
    def on_message(self, client, userdata, msg):
        print ("Topic: " + str(msg.topic))
        print ("QoS: " + str(msg.qos))
        print ("Payload: " + str(msg.payload))
        receivedData = json.loads(msg.payload)
        temp = receivedData["temperature"]
        humidity = receivedData["humidity"]
        sun_light = receivedData["sun_light"]
        press = receivedData["pressure"]
        water = receivedData["mm_water"]
        ts = time.time()
        with self.connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `mqttsensors` (`temperature`, `humidity`,`sun light` ,`pressure`, `water`) VALUES (%s, %s, %s , %s, %s)"
            cursor.execute(sql, (temp, humidity, sun_light, press, water))
            print("Temperature : ")
            print(temp)
            print("Humidity : ")
            print(humidity)
            print("Sun_Light : ")
            print(sun_light)
            print("Pressure : ")
            print(press)
            print("Water on ground : ")
            print(water)



        # Commit changes
        self.connection.commit()

        with self.connection.cursor() as cursor2:
            sql = "SELECT * FROM `mqttsensors`"
            cursor2.execute(sql)
            results = cursor2.fetchall()
            header = results[0].keys()
            rows = [x.values() for x in results]
            print(tabulate.tabulate(rows,header,tablefmt='grid'))

    def mqtt_client(self):
        self.db = Database()
        self.connection = self.db.connect_dbs()
        print("Mqtt client starting")
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        try:
            self.client.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
            print("Connected\n")
        except Exception as e:
            print(str(e))
        self.client.loop_forever()


# Initiate MQTT Client
mqttc = MqttClient();
mqtt_thread = threading.Thread(target=mqttc.mqtt_client,args=(),kwargs={})
mqtt_thread.start()
# server = CoAPServer(ip, port)
try:
    print("Listening server....")
    # server.listen(100)
except KeyboardInterrupt:
    print("Server Shutdown")
    mqttc.kill()
    mqttc.join()
    # server.close()
    print("Exiting...")
mqttc.loop_forever()