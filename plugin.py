# HTU20D Temp/humidity sensor via I2C Python Plugin for Domoticz
#
# Author: Alex Nijmeijer
#
# Required Python Packages
#   pyftdi
#
"""
<plugin key="HTU20D_FTDI" name="HTU20D Temp/humidity sensor via I2C" author="Alex Nijmeijer" version="1.0.0">
    <params>
        <param field="Address" label="FTDI Port" width="150px" required="true" default="ftdi://ftdi:232h:1/1"/>
    </params>
</plugin>
"""

import Domoticz
import pyftdi.i2c  as I2c
import time



class BasePlugin:
    def __init__(self):
        return

    def crc_check(self, data, crc):
        remainder = data<<8
        remainder |= crc
        divsor = 0x988000

        for i in range(0, 16):
            if remainder & 1 << (23 - i):
                remainder ^= divsor
            divsor >>= 1

        if remainder == 0:
            #print ("CRC matched")
            return True
        else:
            #print ("CRC error")
            return False



    def onStart(self):
        Domoticz.Log("onStart called FTDI-address=" + Parameters["Address"])

        self.i2c = I2c.I2cController()
        self.i2c.configure(Parameters["Address"], frequency=10e3) # Address example "ftdi://ftdi:232h:1/1"

        if (len(Devices) == 0):
          Domoticz.Device(Name="Temp+Hum", Unit=1, Type=82, Subtype=1).Create()
          Domoticz.Log("Devices created.")

        DumpConfigToLog()
        #for Device in Devices:
        #  Devices[Device].Update(nValue=Devices[Device].nValue, sValue=Devices[Device].sValue, TimedOut=1)
        Domoticz.Heartbeat(5)

    def onStop(self):
        Domoticz.Log("onStop called")
        self.i2c.terminate()

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Log("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        #Domoticz.Log("onHeartbeat called")
        #take measurement
        #self.i2c.write(0x27,[])
        #time.sleep(0.5)
        #readout (max 5 attempts)
        try:
          status=4
          i = 5
          while (i>0) and (status>0) :
              
            crc_ok = True
            
            #perform humidity measurement
            a=self.i2c.write(0x40,[0xe5])
            #readout
            hum_data=self.i2c.read(0x40,3)
            data = (hum_data[0] <<8 | hum_data[1]) 
            crc=hum_data[2]
            if self.crc_check(data, crc) == False:
              crc_ok=False
            hum=round(-6 + 125*(data&0xFFFC)/(2**16),1)
            time.sleep(1)
            #perform temp measurement
            a=self.i2c.write(0x40,[0xe3])
            time.sleep(1)
            #readout
            temp_data=self.i2c.read(0x40,3)
            data = (temp_data[0] <<8 | temp_data[1])
            crc=temp_data[2]
            if self.crc_check(data, crc) == False:
              crc_ok=False
            temp=round(-46.85 + 175.72*(data&0xFFFC)/(2**16),2)
            #self.i2c.terminate()
   
            if crc_ok == True :
                 status=0
              
            i -= 1
          Domoticz.Log("onHeartbeat: iteration " + str(5-i))

        except:
          Domoticz.Log("I2c read failed")
          status=5

        # Only when we know it is a valid sample, forward it
        #if (len(a)==4) :
        #  Domoticz.Log("onHeartbeat: iteration " + str(a[0])+ " " + #str(a[1])+ " " +str(a[2])+ " " +str(a[3]) )

        
        if (status==0) : 
            UpdateDevice(1, temp, hum)
        else :
            Domoticz.Log("onHeartbeat: unexpected status=" + str(status))


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

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

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



def UpdateDevice(Unit, temp, hum):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it 
    if (Unit in Devices):
        #if (Devices[Unit].nValue != temp) or (Devices[Unit].sValue != sValue):
            Devices[Unit].Update(0, str(temp) + ";" + str(hum) + ";0")
            Domoticz.Log("Update "+str(temp)+";"+str(hum)+" ("+Devices[Unit].Name+")")
    return
