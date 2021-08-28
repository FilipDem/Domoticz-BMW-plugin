#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# BMW Python Plugin
#
# Author: Filip Demaertelaere
#
# Plugin to get data of the BMW.
# Implemenation based on https://github.com/bimmerconnected/bimmer_connected, https://github.com/edent/BMW-i-Remote
#
"""
<plugin key="Bmw" name="Bmw" author="Filip Demaertelaere" version="2.0.0">
    <params>
        <param field="Mode2" label="Username" width="200px" required="true" default=""/>
        <param field="Mode3" label="Password" width="200px" required="true" default="" password="true"/>
        <param field="Mode4" label="VIN" width="200px" required="true" default=""/>
        <param field="Mode1" label="Answer Security Question" width="120px" required="true" default=""/>
        <param field="Mode5" label="Minutes between update" width="120px" required="true" default="5"/>
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
_UNIT_REMOTE_SERVICES = 9
_UNIT_CAR = 10
_UNIT_MILEAGE_COUNTER = 11

#DEFAULT IMAGE
_IMAGE = "Bmw"

#THE HAERTBEAT IS EVERY 10s
_MINUTE = 6

#VALUE TO INDICATE THAT THE DEVICE TIMED-OUT
_TIMEDOUT = 1

#DEBUG
_DEBUG_OFF = 0
_DEBUG_ON = 2

#STATES
_GET_STATUS = 0
_REMOTE_SERVICE = 1
_REMOTE_SERVICE_STATUS = 2

#BMW Information
LIDS = ['doorDriverFront', 'doorPassengerFront', 'doorDriverRear', 'doorPassengerRear', 'hood', 'trunk']
WINDOWS = ['windowDriverFront', 'windowPassengerFront', 'windowDriverRear', 'windowPassengerRear', 'rearWindow', 'sunroof']
REMOTE_LIGHT_FLASH = 'light-flash'
REMOTE_VEHICLE_FINDER = 'vehicle-finder'
REMOTE_DOOR_LOCK = 'door-lock'
REMOTE_DOOR_UNLOCK = 'door-unlock'
REMOTE_HORN = 'horn-blow'
REMOTE_AIR_CONDITIONING = 'climate-now'

#BMW SERVER ADDRESSES REST_OF_WORLD
LEGACY_SERVER = 'b2vapi.bmwgroup.com'
OAUTH_ENDPOINT_SERVER = 'customer.bmwgroup.com'
REMOTE_SERVICES_SERVER = 'cocoapi.bmwgroup.com'

OAUTH_ENDPOINT_AUTH_URI = '/gcdm/oauth/authenticate'
OAUTH_ENDPOINT_TOKEN_URI = '/gcdm/oauth/token'
VEHICLE_STATUS_URI = '/webapi/v1/user/vehicles/{vin}/status'
REMOTE_SERVICES_URI = '/eadrax-vrccs/v2/presentation/remote-commands/{vin}/{service_type}'
REMOTE_SERVICES_STATUS_URI = '/eadrax-vrccs/v2/presentation/remote-commands/eventStatus'

#BMW INITIAL PARAMETERS REST_OF_WORLD
AUTH_CLIENT_ID = '31c357a0-7a1d-4590-aa99-33b97244d048'
AUTH_STATE = 'cEG9eLAIi6Nv-aaCAniziE_B6FPoobva3qr5gukilYw'
TOKEN_AUTHORIZATION = 'Basic MzFjMzU3YTAtN2ExZC00NTkwLWFhOTktMzNiOTcyNDRkMDQ4OmMwZTMzOTNkLTcwYTItNGY2Zi05ZDNjLTg1MzBhZjY0ZDU1Mg=='
TOKEN_VERIFIER = '7PsmfPS5MpaNt0jEcPpi-B7M7u0gs1Nzw6ex0Y9pa-0'


################################################################################
# Start Plugin
################################################################################

class BasePlugin:

    def __init__(self):
        self.debug = _DEBUG_OFF
        self.authorization_challenge = None
        self.login_code = None
        self.authorization_token = None
        self.authorization_token_expiration = None
        self.errorLevel = 0
        self.runAgain = _MINUTE
        self.state = _GET_STATUS
        self.remote_service = REMOTE_LIGHT_FLASH
        self.remote_service_eventid = None
        self.last_car_opened_time = datetime.datetime.now()
        self.car_opened_status_given = False
        self.remote_status_eventid = None
        self.httpConnAuth = None
        self.httpConnApi = None
        self.httpConnRemote = None
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
        try:
            UpdateDevice(_UNIT_REMOTE_SERVICES, Devices[_UNIT_REMOTE_SERVICES].nValue, Devices[_UNIT_REMOTE_SERVICES].sValue, Images[_IMAGE].ID, TimedOut=0)
        except:
            pass

        # Connection parameters
        self.httpConnAuth = Domoticz.Connection(Name="BmwAuth", Transport="TCP/IP", Protocol="HTTPS", Address=OAUTH_ENDPOINT_SERVER, Port='443')
        self.httpConnAuth.Connect()

        # Global settings
        DumpConfigToLog()

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called ({}) with status={}".format(Connection.Name, Status))
        if Status == 0:
            if Connection.Name == 'BmwAuth':
                self.Get_authorization_challenge()
            if Connection.Name == 'BmwApi':
                if self.state == _GET_STATUS:
                    self.Ask_vehicle_status()
            if Connection.Name == 'BmwRemoteServices':
                if self.state == _REMOTE_SERVICE:
                    self.Exec_remote_service(self.remote_service)
            if Connection.Name == 'BmwRemoteServices':
                if self.state == _REMOTE_SERVICE_STATUS:
                    self.Get_remote_service_status()
        else:
            self.errorLevel += 1

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called ({})".format(Connection.Name))
        Domoticz.Debug("HTTP Return Code: {}".format(Data['Status']))

        if int(Data['Status']) == 302:
            # 2 - Handle reply for login code
            if Connection.Name == 'BmwAuth' and self.authorization_challenge:
                if 'location' in Data['Headers']:
                    cookie_location = urllib.parse.urlparse(Data['Headers']['location'])
                    self.login_code = dict(urllib.parse.parse_qsl(cookie_location.query))['code']
                    Domoticz.Debug("Got login code: {}".format(self.login_code))
                    self.Get_authorization_token()

        if int(Data['Status']) == 200:
            Domoticz.Debug("HTTP Data: {}".format(json.dumps(json.loads(Data['Data']))))
            result_json = json.loads(Data['Data'])
            # 1 - Handle reply for authorization challenge
            if Connection.Name == 'BmwAuth' and not self.authorization_challenge:
                if 'redirect_to' in result_json:
                    cookie_redirect = urllib.parse.urlparse(result_json['redirect_to'])
                    self.authorization_challenge = dict(urllib.parse.parse_qsl(cookie_redirect.query))['authorization']
                    Domoticz.Debug("Got authorization challenge: {}".format(self.authorization_challenge))
                    self.Get_login_code()

            # 3 - Handle reply for authorization token
            if Connection.Name == 'BmwAuth' and self.authorization_challenge:
                if 'access_token' in result_json:
                    self.authorization_token = result_json['access_token']
                    expiration_time = int(result_json['expires_in'])
                    self.authorization_token_expiration = datetime.datetime.now() + datetime.timedelta(seconds=expiration_time)
                    Domoticz.Debug("Got authorization token: {}".format(self.authorization_token))
                    Domoticz.Debug("Authorization token expiry: {}".format(self.authorization_token_expiration))
                    self.httpConnAuth.Disconnect()

                    # We have an authorization token and we can start using APIs to get data
                    if self.state == _GET_STATUS:
                        self.Macro_Ask_vehicle_status()
                    if self.state == _REMOTE_SERVICE_STATUS:
                        self.Macro_Get_remote_service_status()
            
            # Handle the return of the status of the car        
            if Connection.Name == 'BmwApi' and self.state == _GET_STATUS:
                # Switch for remote services
                #UpdateDevice(_UNIT_REMOTE_SERVICES, Devices[_UNIT_REMOTE_SERVICES].nValue, Devices[_UNIT_REMOTE_SERVICES].sValue, Images[_IMAGE].ID, TimedOut=0)
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
                # Car
                if result_json['vehicleStatus']['doorLockState'] in ['LOCKED', 'SECURED']:
                    UpdateDevice(_UNIT_CAR, 0, 0, Images[_IMAGE].ID)
                else:
                    if UpdateDevice(_UNIT_CAR, 1, 0, Images[_IMAGE].ID):
                        Domoticz.Debug("Car is opened now!")
                        self.last_car_opened_time = datetime.datetime.now()
                        self.car_opened_status_given = False
                # Mileage
                UpdateDevice(_UNIT_MILEAGE, result_json['vehicleStatus']['mileage'], result_json['vehicleStatus']['mileage'], Images[_IMAGE].ID)
                UpdateDevice(_UNIT_MILEAGE_COUNTER, 0, result_json['vehicleStatus']['mileage'], Images[_IMAGE].ID)
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
            
            # Handle the return on an the status request of a pending remote services event
            # These lines must be before the code that handles the request itself.
            if Connection.Name == 'BmwRemoteServices' and self.state == _REMOTE_SERVICE_STATUS:
                if 'eventStatus' in result_json:
                    Domoticz.Debug("Remote Service ({}) status: {}".format(self.remote_service, result_json['eventStatus']))
                    if result_json['eventStatus'] == 'PENDING':
                        pass
                    else:
                        if result_json['eventStatus'] == 'ERROR':
                            Domoticz.Status("Initiating the remote service ({}) failed: {}".format(self.remote_service, result_json['errorDetails']['description']))
                        Domoticz.Debug("Current state of unit _UNIT_REMOTE_SERVICES: {}".format(Devices[_UNIT_REMOTE_SERVICES].nValue))
                        UpdateDevice(_UNIT_REMOTE_SERVICES, 2, 0, Images[_IMAGE].ID)
                        self.state = _GET_STATUS
                        self.remote_status_eventid = None
                        self.httpConnRemote.Disconnect()
                        if result_json['eventStatus'] == 'EXECUTED' and self.remote_service in [REMOTE_DOOR_LOCK, REMOTE_DOOR_UNLOCK]:
                            self.Macro_Ask_vehicle_status()
                
            # Handle the return on an request for remote services
            if Connection.Name == 'BmwRemoteServices' and self.state == _REMOTE_SERVICE:
                if 'eventId' in result_json:
                    self.remote_status_eventid = result_json['eventId']
                    Domoticz.Debug("Remote Service {} initiated!".format(self.remote_service))
                    self.state = _REMOTE_SERVICE_STATUS
            
        else:
            self.errorLevel += 1

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit: {} - Parameter: {} - Level: {}".format(Unit, Command, Level))
        if Unit == _UNIT_REMOTE_SERVICES and Command == 'Set Level':
            if Level:
                if Level == 10:
                    self.remote_service = REMOTE_LIGHT_FLASH
                elif Level == 20:
                    self.remote_service = REMOTE_HORN
                elif Level == 30:
                    self.remote_service = REMOTE_AIR_CONDITIONING
                elif Level == 40:
                    self.remote_service = REMOTE_DOOR_LOCK
                elif Level == 50:
                    self.remote_service = REMOTE_DOOR_UNLOCK
                self.state = _REMOTE_SERVICE
                self.Macro_Exec_remote_service()
                #UpdateDevice(_UNIT_REMOTE_SERVICES, 1, 1, Images[_IMAGE].ID)
                
    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification")

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called ({})".format(Connection.Name))

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")
        
        # Check remote service status when remote service is initiated
        if self.state == _REMOTE_SERVICE_STATUS:
            self.Macro_Get_remote_service_status()
        
        self.runAgain -= 1
        if self.runAgain <= 0:

            # Check if car is locked
            if int(Devices[_UNIT_CAR].nValue) and not self.car_opened_status_given and datetime.datetime.now()-self.last_car_opened_time>datetime.timedelta(seconds=60):
                Domoticz.Status("Car is not closed!!")
                self.car_opened_status_given = True

            # Get status of the car
            self.Macro_Ask_vehicle_status()

            # Run again following the period in the settings
            self.runAgain = _MINUTE*int(Parameters['Mode5'])
            
            # If no correct communication in some trials...
            if self.errorLevel == 5:
                Domoticz.Error("Too many errors received: devices are timedout!")
                TimeoutDevice(True)
            
        else:
            Domoticz.Debug("onHeartbeat called, run again in {} heartbeats...".format(self.runAgain))

    def Get_authorization_challenge(self):
        Domoticz.Debug("Sending request to get authorization challenge.")
        values = {
            'client_id': AUTH_CLIENT_ID, \
            'response_type': 'code', \
            'redirect_uri': 'com.bmw.connected://oauth', \
            'state': AUTH_STATE, \
            'nonce': 'login_nonce', \
            'scope': 'openid profile email offline_access smacc vehicle_data perseus dlm svds cesim vsapi remote_services fupo authenticate_user', \
            'grant_type': 'authorization_code', \
            'username': Parameters['Mode2'], \
            'password': Parameters['Mode3']
        }
        data = urllib.parse.urlencode(values)
        headers = {
            'User-Agent': 'okhttp/3.12.2', \
            'Host': OAUTH_ENDPOINT_SERVER, \
            'Accept-Encoding': 'gzip, deflate', \
            'Accept': '*/*', \
            'Connection': 'Keep-Alive', \
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        self.httpConnAuth.Send({'Verb': 'POST', 'URL': OAUTH_ENDPOINT_AUTH_URI, 'Headers': headers, 'Data': data})

    def Get_login_code(self):
        Domoticz.Debug("Sending request to get login code.")
        values = {
            'client_id': AUTH_CLIENT_ID, \
            'response_type': 'code', \
            'redirect_uri': 'com.bmw.connected://oauth', \
            'state': AUTH_STATE, \
            'nonce': 'login_nonce', \
            'scope': 'openid profile email offline_access smacc vehicle_data perseus dlm svds cesim vsapi remote_services fupo authenticate_user', \
            'authorization': self.authorization_challenge
        }
        data = urllib.parse.urlencode(values)
        headers = {
            'User-Agent': 'okhttp/3.12.2', \
            'Host': OAUTH_ENDPOINT_SERVER, \
            'Accept-Encoding': 'gzip, deflate', \
            'Accept': '*/*', \
            'Connection': 'Keep-Alive', \
            'Content-Type': 'application/x-www-form-urlencoded', \
            'Cookie': 'GCDMSSO={}'.format(self.authorization_challenge)
        }
        self.httpConnAuth.Send({'Verb': 'POST', 'URL': OAUTH_ENDPOINT_AUTH_URI, 'Headers': headers, 'Data': data})

    def Get_authorization_token(self):
        Domoticz.Debug("Sending request to get authorization token.")
        values = {
            'code': self.login_code, \
            'code_verifier': TOKEN_VERIFIER, \
            'redirect_uri': 'com.bmw.connected://oauth', \
            'grant_type': 'authorization_code'
        }
        data = urllib.parse.urlencode(values)
        headers = {
            'User-Agent': 'okhttp/3.12.2', \
            'Host': OAUTH_ENDPOINT_SERVER, \
            'Accept-Encoding': 'gzip, deflate', \
            'Accept': '*/*', \
            'Connection': 'Keep-Alive', \
            'Content-Type': 'application/x-www-form-urlencoded', \
            'Authorization': TOKEN_AUTHORIZATION
        }
        self.httpConnAuth.Send({'Verb': 'POST', 'URL': OAUTH_ENDPOINT_TOKEN_URI, 'Headers': headers, 'Data': data})

    def Ask_vehicle_status(self):
        headers = {
            'User-Agent': 'okhttp/3.12.2', \
            'Host': LEGACY_SERVER, \
            'Accept-Encoding': 'gzip, deflate', \
            'Accept': 'application/json', \
            'Connection': 'Keep-Alive', \
            'Authorization': 'Bearer {}'.format(self.authorization_token)
        }
        self.httpConnApi.Send({'Verb': 'GET', 'URL': VEHICLE_STATUS_URI.format(vin=Parameters['Mode4']), 'Headers': headers})

    def Exec_remote_service(self, service=REMOTE_HORN):
        data = ''
        headers = {
            'User-Agent': 'okhttp/3.12.2', \
            'Host': REMOTE_SERVICES_SERVER, \
            'Accept-Encoding': 'gzip, deflate', \
            'Accept': '*/*', \
            'Connection': 'Keep-Alive', \
            'nx-user-agent': 'android(v1.07_20200330);bmw;1.5.2(8932)', \
            'Authorization': 'Bearer {}'.format(self.authorization_token)
        }
        url = REMOTE_SERVICES_URI.format(vin=Parameters['Mode4'], service_type=service)
        Domoticz.Debug("HTTP Send Url: {}".format(url))
        self.httpConnRemote.Send({'Verb': 'POST', 'URL': url, 'Headers': headers, 'Data': data})

    def Get_remote_service_status(self):
        data = ''
        headers = {
            'User-Agent': 'okhttp/3.12.2', \
            'Host': REMOTE_SERVICES_SERVER, \
            'Accept-Encoding': 'gzip, deflate', \
            'Accept': '*/*', \
            'Connection': 'Keep-Alive', \
            'nx-user-agent': 'android(v1.07_20200330);bmw;1.5.2(8932)', \
            'Authorization': 'Bearer {}'.format(self.authorization_token)
        }
        url = "{}?eventId={}".format(REMOTE_SERVICES_STATUS_URI, self.remote_status_eventid)
        Domoticz.Debug("HTTP Send Url: {}".format(url))
        self.httpConnRemote.Send({'Verb': 'POST', 'URL': url, 'Headers': headers, 'Data': data})

    def Macro_Ask_vehicle_status(self):
        if self.authorization_token_expiration is None or datetime.datetime.now() > self.authorization_token_expiration:
            if self.httpConnAuth and self.httpConnAuth.Connected():
                self.Get_authorization_challenge()
            else:
                self.httpConnAuth = Domoticz.Connection(Name="BmwAuth", Transport="TCP/IP", Protocol="HTTPS", Address=OAUTH_ENDPOINT_SERVER, Port='443')
                self.httpConnAuth.Connect()
        else:
            if self.httpConnApi and self.httpConnApi.Connected():
                self.Ask_vehicle_status()
            else:
                self.httpConnApi = Domoticz.Connection(Name="BmwApi", Transport="TCP/IP", Protocol="HTTPS", Address=LEGACY_SERVER, Port='443')
                self.httpConnApi.Connect()

    def Macro_Exec_remote_service(self):
        if self.authorization_token_expiration is None or datetime.datetime.now() > self.authorization_token_expiration:
            if self.httpConnAuth and self.httpConnAuth.Connected():
                self.Get_authorization_challenge()
            else:
                self.httpConnAuth = Domoticz.Connection(Name="BmwAuth", Transport="TCP/IP", Protocol="HTTPS", Address=OAUTH_ENDPOINT_SERVER, Port='443')
                self.httpConnAuth.Connect()
        else:
           if self.httpConnRemote and self.httpConnRemote.Connected():
                self.Exec_remote_service(self.remote_service)
           else:
                self.httpConnRemote = Domoticz.Connection(Name="BmwRemoteServices", Transport="TCP/IP", Protocol="HTTPS", Address=REMOTE_SERVICES_SERVER, Port='443')
                self.httpConnRemote.Connect()
                
    def Macro_Get_remote_service_status(self):
        if self.authorization_token_expiration is None or datetime.datetime.now() > self.authorization_token_expiration:
            if self.httpConnAuth and self.httpConnAuth.Connected():
                self.Get_authorization_challenge()
            else:
                self.httpConnAuth = Domoticz.Connection(Name="BmwAuth", Transport="TCP/IP", Protocol="HTTPS", Address=OAUTH_ENDPOINT_SERVER, Port='443')
                self.httpConnAuth.Connect()
        else:
            if self.httpConnRemote and self.httpConnRemote.Connected():
                self.Get_remote_service_status()
            else:
                self.httpConnRemote = Domoticz.Connection(Name="BmwRemoteServices", Transport="TCP/IP", Protocol="HTTPS", Address=REMOTE_SERVICES_SERVER, Port='443')
                self.httpConnRemote.Connect()


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
            Updated = True
            Domoticz.Debug("Update {}: {} - {}".format(Devices[Unit].Name, nValue, sValue))
        else:
            Devices[Unit].Touch()
            Updated = False
        return Updated

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
    if (_UNIT_MILEAGE_COUNTER not in Devices):
        Domoticz.Device(Unit=_UNIT_MILEAGE_COUNTER, Name="Mileage (Day)", Type=113, Subtype=0, Switchtype=3, Options={"ValueUnits": "km", "ValueQuantity": "Kilometers"}, Image=Images[_IMAGE].ID, Used=1).Create()
    if (_UNIT_REMOTE_SERVICES not in Devices):
        Domoticz.Device(Unit=_UNIT_REMOTE_SERVICES, Name="Remote Services", TypeName="Selector Switch", Options={"LevelActions": "|||||", "LevelNames": "|" + REMOTE_LIGHT_FLASH + "|" + REMOTE_HORN + "|" + REMOTE_AIR_CONDITIONING + "|" + REMOTE_DOOR_LOCK + "|" + REMOTE_DOOR_UNLOCK, "LevelOffHidden": "false", "SelectorStyle": "1"}, Image=Images[_IMAGE].ID, Used=1).Create()

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
    if (_UNIT_CAR not in Devices):
        Domoticz.Device(Unit=_UNIT_CAR, Name="Car", Type=244, Subtype=73, Switchtype=11, Image=Images[_IMAGE].ID, Used=0).Create()

#GET CPU TEMPERATURE
def getCPUtemperature():
    try:
        res = os.popen("cat /sys/class/thermal/thermal_zone0/temp").readline()
    except:
        res = "0"
    return round(float(res)/1000,1)
