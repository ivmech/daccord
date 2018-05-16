# Samur Domoticz Plugin
#
# Author: IVMECH Mechatronics
#
"""
<plugin key="Samur" name="Samur MainBoard with MQTT Interface" author="ivmech" version="1.0.0" wikilink="http://www.ivmech.com" externallink="https://www.ivmech.com">
    <params>
        <param field="Address" label="MQTT Server address" width="300px" required="true" default="127.0.0.1"/>
        <param field="Port" label="Port" width="300px" required="true" default="1883"/>
        <param field="Username" label="Username" width="300px"/>
        <param field="Password" label="Password" width="300px"/>
        <param field="Mode1" label="SamurID" width="150px" required="true" default="samur70"/>
    </params>
</plugin>
"""
import time
import Domoticz
#import paho.mqtt.client as mqtt

def on_connect(mosq, obj, rc):
    print("Connected to MQTT Broker")

# Define on_publish event Handler
def on_publish(client, userdata, mid):
    print("Message Published...")

class BasePlugin:

    def __init__(self):
        #self.var = 123
        return

    def onStart(self):
        Domoticz.Heartbeat(10)

        if (len(Devices) == 0):
            for n in range(1,13):
                Domoticz.Device(Name="Relay "+str(n), Unit=n, TypeName="Switch").Create()

            for n in range(1,4):
                Domoticz.Device(Name="Valve "+str(n), Unit=n+12, TypeName="Switch").Create()

            for n in range(1,9):
                Domoticz.Device(Name="Line "+str(n), Unit=n+15, Type=17, Switchtype=2).Create()

            Domoticz.Device(Name="PIR1", Unit=24, Type=17, Switchtype=8).Create()
            Domoticz.Device(Name="PIR2", Unit=25, Type=17, Switchtype=8).Create()
            Domoticz.Device(Name="Leak", Unit=26, Type=17, Switchtype=2).Create()
            Domoticz.Device(Name="Fire", Unit=27, Type=17, Switchtype=5).Create()
            Domoticz.Device(Name="Gas", Unit=28, Type=17, Switchtype=5).Create()
            Domoticz.Device(Name="Door", Unit=29, Type=17, Switchtype=11).Create()

        # Connect MQTT as Publisher
        self.Address = Parameters["Address"]
        self.Port = Parameters["Port"]
        self.samurid = Parameters["Mode1"]

        self.client = mqtt.Client()
        self.client.on_publish = on_publish
        self.client.on_connect = on_connect
        self.client.username_pw_set(Parameters["Username"], Parameters["Password"])

#        DumpConfigToLog()

    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        Command = Command.strip()
        action, sep, params = Command.partition(' ')
        action = action.capitalize()
        params = params.capitalize()
        nValue = 0
        if action == "On": nValue = 1
        Devices[Unit].Update(nValue=nValue, sValue=str(nValue))

        if Unit < 16:
            state = action.upper()

            if Unit < 13:
                relay = "K"+str(Unit)
            else:
                relay = "V"+str(Unit-12)

            MQTT_TOPIC = "%s/%s/set" % (self.samurid, relay)
            MQTT_MSG = state
#            MQTT_TOPIC = "%s/in" % self.samurid
#            MQTT_MSG = '{"command": "switchlight", "unit": %d, "switchcmd": "%s" }' % (Unit, action)

            self.client.connect(self.Address, int(self.Port), 45)
            self.client.publish(MQTT_TOPIC, MQTT_MSG)
            self.client.disconnect()

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        #Domoticz.Log("onHeartbeat called")
        pass

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data, Status, Extra):
    global _plugin
    _plugin.onMessage(Connection, Data, Status, Extra)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

def UpdateDevice(Unit, nValue, sValue):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it 
    if (Unit in Devices):
        if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue):
            Devices[Unit].Update(nValue, str(sValue))
            Domoticz.Log("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")
    return

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
