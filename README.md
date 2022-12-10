# IoT for Smart Agricolture

Project’s goal is to build and set up an automatic system to protect grapes from bad weather conditions or may be used to save other agricultural products.
Application turns out to be useful in the countryside, in particular in Italy, where bad weather conditions are not so frequent and when they do occur they usually produce economic and environmental disasters.
To solve this problem, the physical part of the project is composed of two mechanical covers that are closed when bad weather comes in.
The two covers are side-located to grape marquees and both have a 90° opening radius. Application is composed by two main units:

- MQTT sensors (3) worry about ground real time conditions measuring temperature,rain water, humidity, pressure and actual weather;
- COAP sensors (2) interface with MQTT sensors to activate the two covers when bad conditions are detected. Based on how bad the weather is, covers can reach. different   opening degrees.
  When covers start to move an alarm is triggered. This alarm can be turned off with a button.

Sensors interact with a python application that works as a server collecting data and saving them into a MySQL database. Moreover, server deals with sensors sending response data.
Grafana, that is a visual-real time dashboard is then used to plot out what is saved on MySQL.

                              ![image](https://user-images.githubusercontent.com/60001748/206859585-58d223e1-94e5-4703-a419-37528e72b788.png)
