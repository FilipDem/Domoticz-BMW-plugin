#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# BMW Python Plugin
#
# Author: Filip Demaertelaere
#
# Plugin to get data of the BMW.
# Using directly the bimmerconnected from https://github.com/bimmerconnected/bimmer_connected
# Including the threading...
#
"""
<plugin key="Bmw" name="Bmw" author="Filip Demaertelaere" version="3.1.0">
    <params>
        <param field="Mode2" label="Username" width="200px" required="true" default=""/>
        <param field="Mode3" label="Password" width="200px" required="true" default="" password="true"/>
        <param field="Mode4" label="VIN" width="200px" required="true" default=""/>
        <param field="Mode1" label="Region" width="120px" required="true">
            <options>
                <option label="Rest Of World" value="rest_of_world"/>
                <option label="North America" value="north_america"/>
                <option label="China" value="china" default="Rest Of World"/>
            </options>
        </param>
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
sys.path.append('..')
sys.path.append('/usr/lib/python3/dist-packages')
sys.path.append('/usr/local/lib/python{}.{}/dist-packages'.format(major, minor))
import Domoticz
import datetime
import threading
import queue
import json
from bimmer_connected.account import ConnectedDriveAccount
from bimmer_connected.country_selector import get_region_from_name
from bimmer_connected.remote_services import ExecutionState

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

#BMW Information
REGIONS = ['Rest_of_World', 'China', 'North_America']
REMOTE_LIGHT_FLASH = 'light-flash'
REMOTE_VEHICLE_FINDER = 'vehicle-finder'
REMOTE_DOOR_LOCK = 'door-lock'
REMOTE_DOOR_UNLOCK = 'door-unlock'
REMOTE_HORN = 'horn-blow'
REMOTE_AIR_CONDITIONING = 'climate-now'

################################################################################
# Start Plugin
################################################################################

class BasePlugin:

    def __init__(self):
        self.debug = _DEBUG_OFF
        self.runAgain = _MINUTE
        self.errorLevel = 0
        self.myBMW = None
        self.region = REGIONS[0]
        self.myVehicle = None
        self.last_car_opened_time = datetime.datetime.now()
        self.car_opened_status_given = False
        self.tasksQueue = queue.Queue()
        self.tasksThread = threading.Thread(name='QueueThread', target=BasePlugin.handleTasks, args=(self,))

    def onStart(self):
        Domoticz.Debug("onStart called")

        # Debugging On/Off
        if Parameters["Mode6"] == "Debug":
            self.debug = _DEBUG_ON
        else:
            self.debug = _DEBUG_OFF
        Domoticz.Debugging(self.debug)
        
        # Check region (especially because of updating from previous version
        if Parameters['Mode1'] in REGIONS:
            self.region = Parameters['Mode1']

        # Check if images are in database
        if _IMAGE not in Images:
            Domoticz.Image("Bmw.zip").Create()

        # Create devices (USED BY DEFAULT)
        CreateDevicesUsed()

        # Create devices (NOT USED BY DEFAULT)
        CreateDevicesNotUsed()

        # Set all devices as timed out
        TimeoutDevice(All=True)

        # Create BMW instance
        self.tasksThread.start()
        self.tasksQueue.put({'Action': 'Login'})
        self.tasksQueue.put({'Action': 'StatusUpdate'})

        # Global settings
        DumpConfigToLog()

    def onStop(self):
        Domoticz.Debug("onStop called")
        
        # Signal queue thread to exit
        self.tasksQueue.put(None)
        self.tasksQueue.join()

        # Wait until queue thread has exited
        Domoticz.Debug('Threads still active: {} (should be 1)'.format(threading.active_count()))
        while threading.active_count() > 1:
            for thread in threading.enumerate():
                if thread.name != threading.current_thread().name:
                    Domoticz.Debug('Thread {} is still running, waiting otherwise Domoticz will abort on plugin exit.'.format(thread.name))
            time.sleep(1.0)

        Domoticz.Debug('Plugin stopped')

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called ({}) with status={}".format(Connection.Name, Status))

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called ({})".format(Connection.Name))

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit: {} - Parameter: {} - Level: {}".format(Unit, Command, Level))
        if Unit == _UNIT_REMOTE_SERVICES and Command == 'Set Level':
            if Level:
                if Level == 10:
                    self.tasksQueue.put({'Action': REMOTE_LIGHT_FLASH})
                elif Level == 20:
                    self.tasksQueue.put({'Action': REMOTE_HORN})
                elif Level == 30:
                    self.tasksQueue.put({'Action': REMOTE_AIR_CONDITIONING})
                elif Level == 40:
                    self.tasksQueue.put({'Action': REMOTE_DOOR_LOCK})
                    self.tasksQueue.put({'Action': 'StatusUpdate'})
                elif Level == 50:
                    self.tasksQueue.put({'Action': REMOTE_DOOR_UNLOCK})
                    self.tasksQueue.put({'Action': 'StatusUpdate'})

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification")

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called ({})".format(Connection.Name))

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")
        
        self.runAgain -= 1
        if self.runAgain <= 0:

            # Check if car is locked
            if int(Devices[_UNIT_CAR].nValue) and not self.car_opened_status_given and datetime.datetime.now()-self.last_car_opened_time>datetime.timedelta(seconds=60):
                Domoticz.Status('ATTTENTION: Car is not closed!!')
                self.car_opened_status_given = True

            if self.myBMW == None:
                self.tasksQueue.put({'Action': 'Login'})
            self.tasksQueue.put({'Action': 'StatusUpdate'})

            # Run again following the period in the settings
            self.runAgain = _MINUTE*int(Parameters['Mode5'])
            
            # If no correct communication in some trials...
            if self.errorLevel == 5:
                Domoticz.Error("Too many errors received: devices are timedout!")
                TimeoutDevice(True)
        else:
            Domoticz.Debug("onHeartbeat called, run again in {} heartbeats...".format(self.runAgain))

    def handleTasks(self):
        try:
            Domoticz.Debug('Entering tasks handler')
            while True:
                task = self.tasksQueue.get(block=True)
                if task is None:
                    Domoticz.Debug('Exiting task handler')
                    self.MyBMW = None
                    self.tasksQueue.task_done()
                    break

                Domoticz.Debug('Handling task: {}.'.format(task['Action']))
                if task['Action'] == 'Login':
                    try:
                        self.myBMW = ConnectedDriveAccount(Parameters['Mode2'], Parameters['Mode3'], get_region_from_name(self.region))
                    except:
                        Domoticz.Error('Error login in ConnectedDrive for user {} and region {}.'.format(Parameters['Mode2'], self.region))
                        self.myBMW = None
                        self.errorLevel += 1
                    else:
                        self.myVehicle = self.myBMW.get_vehicle(Parameters['Mode4'])
                        if self.myVehicle:
                            Domoticz.Debug('Car {} found!'.format(self.myVehicle.name))
                            self.updateVehicleStatus()
                        else:
                            Domoticz.Error('vin {} not found for user {}.'.format(Parameters['Mode4'], Parameters['Mode2']))
                            TimeoutDevice(True)

                elif task['Action'] == 'StatusUpdate':
                    if self.myBMW and self.myVehicle:
                        try:
                            self.myBMW.update_vehicle_states()
                        except:
                            if not self.errorLevel:
                                Domoticz.Status('Error occured in getting the status update of the BMW.')
                            self.errorLevel += 1
                        else:
                            self.myVehicle = self.myBMW.get_vehicle(Parameters['Mode4'])
                            if self.myVehicle:
                                Domoticz.Debug('Car {} found after update!'.format(self.myVehicle.name))
                                self.updateVehicleStatus()
                            else:
                                if not self.errorLevel:
                                    Domoticz.Status('BMW with VIN {} not found for user {}.'.format(Parameters['Mode4'], Parameters['Mode2']))
                                self.errorLevel += 1
                            
                elif task['Action'] in [REMOTE_LIGHT_FLASH, REMOTE_DOOR_LOCK, REMOTE_DOOR_UNLOCK, REMOTE_HORN, REMOTE_AIR_CONDITIONING]:
                    if self.myVehicle:
                        try:
                            if task['Action'] == REMOTE_LIGHT_FLASH:
                                Status = self.myVehicle.remote_services.trigger_remote_light_flash()
                            elif task['Action'] == REMOTE_HORN:
                                Status = self.myVehicle.remote_services.trigger_remote_horn()
                            elif task['Action'] == REMOTE_AIR_CONDITIONING:
                                Status = self.myVehicle.remote_services.trigger_remote_air_conditioning()
                            elif task['Action'] == REMOTE_DOOR_LOCK:
                                Status = self.myVehicle.remote_services.trigger_remote_door_lock()
                            elif task['Action'] == REMOTE_DOOR_UNLOCK:
                                Status = self.myVehicle.remote_services.trigger_remote_door_unlock()
                            if Status.state != ExecutionState.EXECUTED:
                                 Domoticz.Error('Error executing remote service {} for {} (not executed).'.format(task['Action'], Parameters['Mode4']))
                        except:
                            Domoticz.Error('Error executing remote service {} for {} (unknown error).'.format(task['Action'], Parameters['Mode4']))
                    else:
                        Domoticz.Error('BMW with VIN {} not found for user {}.'.format(Parameters['Mode4'], Parameters['Mode2']))
                    UpdateDevice(_UNIT_REMOTE_SERVICES, 2, 0)
    
                else:
                     Domoticz.Error('Invalid task/action name: {}.'.format(task['Action']))

                self.tasksQueue.task_done()
                Domoticz.Debug('Finished handling task: {}.'.format(task['Action']))

        except Exception as err:
            self.tasksQueue.task_done()
            Domoticz.Error('General error TaskHandler: {}'.format(err))

    def updateVehicleStatus(self):

        # Update status Doors
        if self.myVehicle.status.all_lids_closed:
            UpdateDevice(_UNIT_DOORS, 0, 0)
        else:
            UpdateDevice(_UNIT_DOORS, 1, 0)
    
        # Update status Windows
        if self.myVehicle.status.all_windows_closed:
            UpdateDevice(_UNIT_WINDOWS, 0, 0)
        else:
            UpdateDevice(_UNIT_WINDOWS, 1, 0)

        # Update status Locked
        if self.myVehicle.status.door_lock_state == 'LOCKED':
            UpdateDevice(_UNIT_CAR, 0, 0)
        else:
            if UpdateDevice(_UNIT_CAR, 1, 0):
                Domoticz.Debug("Car is opened now!")
                self.last_car_opened_time = datetime.datetime.now()
                self.car_opened_status_given = False

        # Update Mileage
        Domoticz.Debug('Units ({}) are not yet updated on device but hardcoded.'.format(self.myVehicle.status.mileage[1]))
        UpdateDevice(_UNIT_MILEAGE, self.myVehicle.status.mileage[0], self.myVehicle.status.mileage[0])
        UpdateDevice(_UNIT_MILEAGE_COUNTER, 0, self.myVehicle.status.mileage[0])

        # Update Remaining mileage
        if self.myVehicle.status.remaining_range_electric != None:
            UpdateDevice(_UNIT_REMAIN_RANGE_ELEC, self.myVehicle.status.remaining_range_electric[0], self.myVehicle.status.remaining_range_electric[0])
        if self.myVehicle.status.remaining_range_fuel[0] != None:
            UpdateDevice(_UNIT_REMAIN_RANGE_FUEL, self.myVehicle.status.remaining_range_fuel[0], self.myVehicle.status.remaining_range_fuel[0])

        # Update Electric charging
        if self.myVehicle.status.charging_status != None:
            if self.myVehicle.status.charging_status == 'CHARGING':
                UpdateDevice(_UNIT_CHARGING, 1, 1)
            else:
                UpdateDevice(_UNIT_CHARGING, 0, 0)

        # Update Charging Percentage
        if self.myVehicle.status.charging_level_hv != None:
            UpdateDevice(_UNIT_BAT_LEVEL, self.myVehicle.status.charging_level_hv, self.myVehicle.status.charging_level_hv)

        # Update Charging Time (minutes)
        if self.myVehicle.status.charging_time_remaining != None:
            UpdateDevice(_UNIT_CHARGING_REMAINING, self.myVehicle.status.charging_time_remaining, self.myVehicle.status.charging_time_remaining)

        # Switch for remote services
        if Devices[_UNIT_REMOTE_SERVICES].TimedOut == _TIMEDOUT:
            UpdateDevice(_UNIT_REMOTE_SERVICES, Devices[_UNIT_REMOTE_SERVICES].nValue, Devices[_UNIT_REMOTE_SERVICES].sValue, TimedOut=0)

        # All went well...
        self.errorLevel = 0
                

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
def UpdateDevice(Unit, nValue, sValue, Image=None, TimedOut=0, AlwaysUpdate=False):
    if Unit in Devices:
        if not Image:
            Image = Devices[Unit].Image
        if Devices[Unit].nValue != int(nValue) or Devices[Unit].sValue != str(sValue) or Devices[Unit].TimedOut != TimedOut or Devices[Unit].Image != Image or AlwaysUpdate:
            Devices[Unit].Update(nValue=int(nValue), sValue=str(sValue), Image=Image, TimedOut=TimedOut)
            Domoticz.Debug('Update unit {}: {} - {} - {}'.format(Unit, Devices[Unit].Name, nValue, sValue))
            Updated = True
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
