#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Fan Python Plugin
#
# Author: Filip Demaertelaere
#
# Plugin to get data of the BMW.
# Implemenation based on https://github.com/bimmerconnected/bimmer_connected
#
"""
<plugin key="Bmw" name="Bmw" author="Filip Demaertelaere" version="1.0.0">
    <params>
        <param field="Mode1" label="Username" width="200px" required="true" default=""/>
        <param field="Mode2" label="Password" width="200px" required="true" default="" password="true"/>
        <param field="Mode4" label="VIN" width="200px" required="true" default=""/>
        <param field="Mode5" label="Minutes between update" width="120px" required="true" default="5"/>
        <param field="Mode3" label="API Type" width="200px" required="true" default="">
            <options>
                <option label="Legacy" value="Legacy"/>
                <option label="New" value="New" default="New"/>
            </options>
        </param>
        <param field="Mode6" label="Debug" width="120px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="True"/>
            </options>
        </param>
    </params>
</plugin>
"""

#IMPORTS
import sys
major,minor,x,y,z = sys.version_info
sys.path.append('/usr/lib/python3/dist-packages')
sys.path.append('/usr/local/lib/python'+str(major)+'.'+str(minor)+'/dist-packages')
import Domoticz
import urllib.parse
import datetime
import json

#DEVICES TO CREATE
_UNIT_MILEAGE = 1
_UNIT_DOORS = 2
_UNIT_WINDOWS = 3
_UNIT_REMAIN_RANGE_FUEL = 4
_UNIT_REMAIN_RANGE_ELEC = 5
_UNIT_CHARGING = 6
_UNIT_CHARGING_REMAINING = 7
_UNIT_BAT_LEVEL = 8

#DEFAULT IMAGE
_IMAGE = "Bmw"

#THE HAERTBEAT IS EVERY 10s
_MINUTE = 6

#VALUE TO INDICATE THAT THE DEVICE TIMED-OUT
_TIMEDOUT = 1

#DEBUG
_DEBUG_OFF = 0
_DEBUG_ON = 1

#BMW Information
LIDS = ['doorDriverFront', 'doorPassengerFront', 'doorDriverRear', 'doorPassengerRear', 'hood', 'trunk']
WINDOWS = ['windowDriverFront', 'windowPassengerFront', 'windowDriverRear', 'windowPassengerRear', 'rearWindow', 'sunroof']

################################################################################
# Start Plugin
################################################################################

class BasePlugin:

    def __init__(self):
        self.debug = _DEBUG_OFF
        self.token_expiration = None
        self.oauth_token = None
        self.errorLevel = 0
        self.runAgain = _MINUTE
        return

    def onStart(self):
        Domoticz.Debug("onStart called")

        # Debugging On/Off
        if Parameters["Mode6"] == "Debug":
            self.debug = _DEBUG_ON
        else:
            self.debug = _DEBUG_OFF
        Domoticz.Debugging(self.debug)

        # Check if images are in database
        if _IMAGE not in Images:
            Domoticz.Image("Bmw.zip").Create()

        # Create devices (USED BY DEFAULT)
        CreateDevicesUsed()

        # Create devices (NOT USED BY DEFAULT)
        CreateDevicesNotUsed()

        # Set all devices as timed out
        TimeoutDevice(All=True)

        # Connection parameters
        if Parameters['Mode3'] == 'Legacy':
            self.httpConnAuth = Domoticz.Connection(Name="BmwAuth", Transport="TCP/IP", Protocol="HTTPS", Address='b2vapi.bmwgroup.com', Port='443')
        else:
            self.httpConnAuth = Domoticz.Connection(Name="BmwAuth", Transport="TCP/IP", Protocol="HTTPS", Address='customer.bmwgroup.com', Port='443')
        self.httpConnAuth.Connect()

        # Global settings
        DumpConfigToLog()

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called ("+Connection.Name+") with status="+str(Status))
        if Status == 0:
            if Connection.Name == 'BmwAuth':
                self.Get_oauth_token()
            if Connection.Name == 'BmwApi':
                self.Ask_vehicle_status()
        else:
            self.errorLevel += 1

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called ("+Connection.Name+")")
        if int(Data['Status']) == 200:
            result_json = json.loads(Data['Data'])
            if Connection.Name == 'BmwAuth':
                self.oauth_token = result_json['access_token']
                expiration_time = int(result_json['expires_in'])
                self.token_expiration = datetime.datetime.now() + datetime.timedelta(seconds=expiration_time)
                Domoticz.Debug(self.oauth_token)
                self.httpConnAuth.Disconnect()
                self.httpConnApi = Domoticz.Connection(Name="BmwApi", Transport="TCP/IP", Protocol="HTTPS", Address='b2vapi.bmwgroup.com', Port='443')
                self.httpConnApi.Connect()
            if Connection.Name == 'BmwApi':
                # Doors
                Status = 0
                for door in LIDS:
                    if door in result_json['vehicleStatus']:
                        if result_json['vehicleStatus'][door] not in ['CLOSED', 'INVALID']:
                            Status = 1
                UpdateDevice(_UNIT_DOORS, Status, 0, Images[_IMAGE].ID)
                # Windows
                Status = 0
                for window in WINDOWS:
                    if window in result_json['vehicleStatus']:
                        if result_json['vehicleStatus'][window] not in ['CLOSED', 'INVALID']:
                            Status = 1
                UpdateDevice(_UNIT_WINDOWS, Status, 0, Images[_IMAGE].ID)
                # Mileage
                UpdateDevice(_UNIT_MILEAGE, result_json['vehicleStatus']['mileage'], result_json['vehicleStatus']['mileage'], Images[_IMAGE].ID)
                # Remaining mileage (remainingRangeFuel is the total remaining mileage, including the remainingRangeElectric)
                if 'remainingRangeElectric' in result_json['vehicleStatus']:
                    remainingRangeElectric = result_json['vehicleStatus']['remainingRangeElectric']
                    UpdateDevice(_UNIT_REMAIN_RANGE_ELEC, remainingRangeElectric, remainingRangeElectric, Images[_IMAGE].ID)
                else:
                    remainingRangeElectric = 0
                if 'remainingRangeFuel' in result_json['vehicleStatus']:
                    remainingRangeFuel = result_json['vehicleStatus']['remainingRangeFuel'] - remainingRangeElectric
                    UpdateDevice(_UNIT_REMAIN_RANGE_FUEL, remainingRangeFuel, remainingRangeFuel, Images[_IMAGE].ID)
                # Electric charging
                if 'chargingStatus' in result_json['vehicleStatus']:
                    if result_json['vehicleStatus']['chargingStatus'] == 'CHARGING':
                        UpdateDevice(_UNIT_CHARGING, 1, 1, Images[_IMAGE].ID)
                    else:
                        UpdateDevice(_UNIT_CHARGING, 0, 0, Images[_IMAGE].ID)
                if 'chargingTimeRemaining' in result_json['vehicleStatus']:
                    UpdateDevice(_UNIT_CHARGING_REMAINING, result_json['vehicleStatus']['chargingTimeRemaining'], result_json['vehicleStatus']['chargingTimeRemaining'], Images[_IMAGE].ID)
                if 'chargingLevelHv' in result_json['vehicleStatus']:
                    UpdateDevice(_UNIT_BAT_LEVEL, result_json['vehicleStatus']['chargingLevelHv'], result_json['vehicleStatus']['chargingLevelHv'], Images[_IMAGE].ID)
                # All went well...
                self.errorLevel = 0
        else:
            self.errorLevel += 1

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called ("+Connection.Name+")")

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")
        self.runAgain -= 1
        if self.runAgain <= 0:

            # Get a new auth token from the server.
            if self.token_expiration is None or datetime.datetime.now() > self.token_expiration:
                if self.httpConnAuth.Connected():
                    self.Get_oauth_token()
                else:
                    self.httpConnAuth = Domoticz.Connection(Name="BmwAuth", Transport="TCP/IP", Protocol="HTTPS", Address='customer.bmwgroup.com', Port='443')
                    self.httpConnAuth.Connect()
            else:
                if self.httpConnApi.Connected():
                    self.Ask_vehicle_status()
                else:
                    self.httpConnApi = Domoticz.Connection(Name="BmwApi", Transport="TCP/IP", Protocol="HTTPS", Address='b2vapi.bmwgroup.com', Port='443')
                    self.httpConnApi.Connect()

            # Run again following the period in the settings
            self.runAgain = _MINUTE*int(Parameters['Mode5'])
            
            # If no correct communication in some trials...
            if self.errorLevel == 5:
                Domoticz.Error("Too many errors received: devices are timedout!")
                TimeoutDevice(True)
            
        else:
            Domoticz.Debug("onHeartbeat called, run again in "+str(self.runAgain)+" heartbeats.")

    def Get_oauth_token(self):
        Domoticz.Debug("API Mode used: "+Parameters['Mode3'])
        values = {
            'scope': 'authenticate_user vehicle_data remote_services', \
            'username': Parameters['Mode1'], \
            'password': Parameters['Mode2'], \
            'grant_type': 'password'
        }
        data = urllib.parse.urlencode(values)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded', \
            'Content-Length': "%d" % (len(data)), \
            'Connection': 'Keep-Alive', \
            'Host': 'customer.bmwgroup.com', \
            'Accept-Encoding': 'json', \
            'Authorization': 'Basic ZDc2NmI1MzctYTY1NC00Y2JkLWEzZGMtMGNhNTY3MmQ3ZjhkOjE1ZjY5N2Y2LWE1ZDUtNGNhZC05OWQ5LTNhMTViYzdmMzk3Mw==', \
            'Credentials': 'nQv6CqtxJuXWP74xf3CJwUEP:1zDHx6un4cDjybLENN3kyfumX2kEYigWPcQpdvDRpIBk7rOJ', \
            'User-Agent': 'okhttp/3.12.2'
        }
        url = '/gcdm/oauth/token'
        self.httpConnAuth.Send({'Verb': 'POST', 'URL': url, 'Headers': headers, 'Data': data})

    def Ask_vehicle_status(self):
        headers = {
            'accept': 'application/json', \
            'Authorization': 'Bearer {}'.format(self.oauth_token), \
            'Host': 'b2vapi.bmwgroup.com', \
            'referer': 'https://www.bmw-connecteddrive.de/app/index.html'
        }
        url = '/webapi/v1/user/vehicles/'+ Parameters['Mode4'] +'/status'
        self.httpConnApi.Send({'Verb': 'GET', 'URL': url, 'Headers': headers})


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

################################################################################
# Generic helper functions
################################################################################

#DUMP THE PARAMETER
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))

#UPDATE THE DEVICE
def UpdateDevice(Unit, nValue, sValue, Image, TimedOut=0, AlwaysUpdate=False):
    if Unit in Devices:
        if Devices[Unit].nValue != int(nValue) or Devices[Unit].sValue != str(sValue) or Devices[Unit].TimedOut != TimedOut or Devices[Unit].Image != Image or AlwaysUpdate:
            Devices[Unit].Update(nValue=int(nValue), sValue=str(sValue), Image=Image, TimedOut=TimedOut)
            Domoticz.Debug("Update " + Devices[Unit].Name + ": " + str(nValue) + " - '" + str(sValue) + "'")
        else:
            Devices[Unit].Touch()

#SET DEVICE ON TIMED-OUT (OR ALL DEVICES)
def TimeoutDevice(All, Unit=0):
    if All:
        for x in Devices:
            UpdateDevice(x, Devices[x].nValue, Devices[x].sValue, Devices[x].Image, TimedOut=_TIMEDOUT)
    else:
        UpdateDevice(Unit, Devices[Unit].nValue, Devices[Unit].sValue, Devices[Unit].Image, TimedOut=_TIMEDOUT)

#CREATE ALL THE DEVICES (USED)
def CreateDevicesUsed():
    if (_UNIT_MILEAGE not in Devices):
        Domoticz.Device(Unit=_UNIT_MILEAGE, Name="Mileage", TypeName="Custom", Options={"Custom": "0;km"}, Image=Images[_IMAGE].ID, Used=1).Create()

#CREATE ALL THE DEVICES (NOT USED)
def CreateDevicesNotUsed():
    if (_UNIT_DOORS not in Devices):
        
        Domoticz.Device(Unit=_UNIT_DOORS, Name="Doors", Type=244, Subtype=73, Switchtype=11, Image=Images[_IMAGE].ID, Used=0).Create()
    if (_UNIT_WINDOWS not in Devices):
        Domoticz.Device(Unit=_UNIT_WINDOWS, Name="Windows", Type=244, Subtype=73, Switchtype=11, Image=Images[_IMAGE].ID, Used=0).Create()
    if (_UNIT_REMAIN_RANGE_FUEL not in Devices):
        Domoticz.Device(Unit=_UNIT_REMAIN_RANGE_FUEL, Name="Remain mileage (fuel)", TypeName="Custom", Options={"Custom": "0;km"}, Image=Images[_IMAGE].ID, Used=0).Create()
    if (_UNIT_REMAIN_RANGE_ELEC not in Devices):
        Domoticz.Device(Unit=_UNIT_REMAIN_RANGE_ELEC, Name="Remain mileage (elec)", TypeName="Custom", Options={"Custom": "0;km"}, Image=Images[_IMAGE].ID, Used=0).Create()
    if (_UNIT_CHARGING not in Devices):
        Domoticz.Device(Unit=_UNIT_CHARGING, Name="Charging", Type=244, Subtype=73, Switchtype=0, Image=Images[_IMAGE].ID, Used=0).Create()
    if (_UNIT_CHARGING_REMAINING not in Devices):
        Domoticz.Device(Unit=_UNIT_CHARGING_REMAINING, Name="Charging time", TypeName="Custom", Options={"Custom": "0;min"}, Image=Images[_IMAGE].ID, Used=0).Create()
    if (_UNIT_BAT_LEVEL not in Devices):
        Domoticz.Device(Unit=_UNIT_BAT_LEVEL, Name="Battery Level", TypeName="Custom", Options={"Custom": "0;%"}, Image=Images[_IMAGE].ID, Used=0).Create()

#GET CPU TEMPERATURE
def getCPUtemperature():
    try:
        res = os.popen("cat /sys/class/thermal/thermal_zone0/temp").readline()
    except:
        res = "0"
    return round(float(res)/1000,1)
