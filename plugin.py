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
<plugin key="Bmw" name="Bmw" author="Filip Demaertelaere" version="3.2.0">
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
import sys, os
major,minor,x,y,z = sys.version_info
sys.path.append('/usr/lib/python3/dist-packages')
sys.path.append('/usr/local/lib/python{}.{}/dist-packages'.format(major, minor))
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from domoticz_tools import *
import Domoticz
import datetime
import threading
import queue
import json
import time
import asyncio #inspired on https://www.domoticz.com/forum/viewtopic.php?f=65&p=283902
from bimmer_connected.account import MyBMWAccount
from bimmer_connected.api.regions import get_region_from_name
from bimmer_connected.vehicle.remote_services import ExecutionState

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
_UNIT_DRIVING = 12
_UNIT_HOME = 13

#DEFAULT IMAGE
_IMAGE = 'Bmw'

#BMW Information
REGIONS = ['rest_of_world', 'china', 'north_america']
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
        self.debug = DEBUG_OFF
        self.runAgain = MINUTE
        self.errorLevel = 0
        self.myBMW = None
        self.region = REGIONS[0]
        self.myVehicle = None
        self.last_car_opened_time = datetime.datetime.now()
        self.car_opened_status_given = False
        self.car_location = (None, None)
        self.last_car_location = (None, None)
        self.entering_home_distance = 1000
        self.tasksQueue = queue.Queue()
        self.tasksThread = threading.Thread(name='QueueThread', target=BasePlugin.handleTasks, args=(self,))

    def onStart(self):
        Domoticz.Debug('onStart called')

        # Debugging On/Off
        self.debug = DEBUG_ON if Parameters['Mode6'] == 'Debug' else DEBUG_OFF
        Domoticz.Debugging(self.debug)
        if self.debug == DEBUG_ON:
            DumpConfigToLog(Parameters, Devices)
        
        # Read technical parameters
        Domoticz.Debug('Looking for configuration file {}Bmw.json'.format(Parameters['HomeFolder']))
        try:
            config = None
            with open('{}Bmw.json'.format(Parameters['HomeFolder'])) as json_file:
                config = json.load(json_file)
            self.entering_home_distance = config['EnteringHomeDistance (m)']
        except:
            pass

        # Check region (especially because of updating from previous version
        if Parameters['Mode1'] in REGIONS:
            self.region = Parameters['Mode1']

        # Check if images are in database
        if _IMAGE not in Images:
            Domoticz.Image('Bmw.zip').Create()

        # Create devices
        if (_UNIT_MILEAGE not in Devices):
            Domoticz.Device(Unit=_UNIT_MILEAGE, Name='Mileage', TypeName='Custom', Options={'Custom': '0;km'}, Image=Images[_IMAGE].ID, Used=1).Create()
        if (_UNIT_MILEAGE_COUNTER not in Devices):
            Domoticz.Device(Unit=_UNIT_MILEAGE_COUNTER, Name='Mileage (Day)', Type=113, Subtype=0, Switchtype=3, Options={'ValueUnits': 'km'}, Image=Images[_IMAGE].ID, Used=1).Create()
        if (_UNIT_REMOTE_SERVICES not in Devices):
            Domoticz.Device(Unit=_UNIT_REMOTE_SERVICES, Name='Remote Services', TypeName='Selector Switch', Options={'LevelActions': '|||||', 'LevelNames': '|{}|{}|{}|{}|{}'.format(REMOTE_LIGHT_FLASH, REMOTE_HORN, REMOTE_AIR_CONDITIONING, REMOTE_DOOR_LOCK, REMOTE_DOOR_UNLOCK), 'LevelOffHidden': 'false', 'SelectorStyle': '1'}, Image=Images[_IMAGE].ID, Used=1).Create()
        if (_UNIT_DOORS not in Devices):
            Domoticz.Device(Unit=_UNIT_DOORS, Name='Doors', Type=244, Subtype=73, Switchtype=11, Image=Images[_IMAGE].ID, Used=0).Create()
        if (_UNIT_WINDOWS not in Devices):
            Domoticz.Device(Unit=_UNIT_WINDOWS, Name='Windows', Type=244, Subtype=73, Switchtype=11, Image=Images[_IMAGE].ID, Used=0).Create()
        if (_UNIT_REMAIN_RANGE_FUEL not in Devices):
            Domoticz.Device(Unit=_UNIT_REMAIN_RANGE_FUEL, Name='Remain mileage (fuel)', TypeName='Custom', Options={'Custom': '0;km'}, Image=Images[_IMAGE].ID, Used=0).Create()
        if (_UNIT_REMAIN_RANGE_ELEC not in Devices):
            Domoticz.Device(Unit=_UNIT_REMAIN_RANGE_ELEC, Name='Remain mileage (elec)', TypeName='Custom', Options={'Custom': '0;km'}, Image=Images[_IMAGE].ID, Used=0).Create()
        if (_UNIT_CHARGING not in Devices):
            Domoticz.Device(Unit=_UNIT_CHARGING, Name='Charging', Type=244, Subtype=73, Switchtype=0, Image=Images[_IMAGE].ID, Used=0).Create()
        if (_UNIT_CHARGING_REMAINING not in Devices):
            Domoticz.Device(Unit=_UNIT_CHARGING_REMAINING, Name='Charging time', TypeName='Custom', Options={'Custom': '0;min'}, Image=Images[_IMAGE].ID, Used=0).Create()
        if (_UNIT_BAT_LEVEL not in Devices):
            Domoticz.Device(Unit=_UNIT_BAT_LEVEL, Name='Battery Level', TypeName='Custom', Options={'Custom': '0;%'}, Image=Images[_IMAGE].ID, Used=0).Create()
        if (_UNIT_CAR not in Devices):
            Domoticz.Device(Unit=_UNIT_CAR, Name='Car', Type=244, Subtype=73, Switchtype=11, Image=Images[_IMAGE].ID, Used=0).Create()
        if (_UNIT_DRIVING not in Devices):
            Domoticz.Device(Unit=_UNIT_DRIVING, Name='Driving', Type=244, Subtype=73, Switchtype=0, Image=Images[_IMAGE].ID, Used=0).Create()
        if (_UNIT_HOME not in Devices):
            Domoticz.Device(Unit=_UNIT_HOME, Name='Home', Type=244, Subtype=73, Switchtype=0, Image=Images[_IMAGE].ID, Used=1).Create()
        TimeoutDevice(Devices, All=True)

        # Create BMW instance
        self.tasksThread.start()
        self.tasksQueue.put({'Action': 'Login'})
        self.tasksQueue.put({'Action': 'StatusUpdate'})

    def onStop(self):
        Domoticz.Debug('onStop called - Threads still active: {} (should be 1 = {})'.format(threading.active_count(), threading.current_thread().name))
        
        # Signal queue thread to exit
        self.tasksQueue.put(None)
        self.tasksThread.join()

        # Wait until queue thread has exited
        Domoticz.Debug('Threads still active: {} (should be 1)'.format(threading.active_count()))
        endTime = time.time() + 70
        while (threading.active_count() > 1) and (time.time() < endTime):
            for thread in threading.enumerate():
                if thread.name != threading.current_thread().name:
                    Domoticz.Debug('Thread {} is still running, waiting otherwise Domoticz will abort on plugin exit.'.format(thread.name))
            time.sleep(1.0)

        Domoticz.Debug('Plugin stopped - Threads still active: {} (should be 1)'.format(threading.active_count()))

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug('onConnect called ({}) with status={}'.format(Connection.Name, Status))

    def onMessage(self, Connection, Data):
        Domoticz.Debug('onMessage called ({})'.format(Connection.Name))

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug('onCommand called for Unit: {} - Parameter: {} - Level: {}'.format(Unit, Command, Level))
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
        Domoticz.Debug('Notification: {}, {}, {}, {}, {}, {}, {}'.format(
            Name, Subject, Text, Status, Priority, Sound, ImageFile
        ))

    def onDisconnect(self, Connection):
        Domoticz.Debug('onDisconnect called ({})'.format(Connection.Name))

    def onHeartbeat(self):
        
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
            self.runAgain = MINUTE*int(Parameters['Mode5'])
            
            # If no correct communication in some trials...
            if self.errorLevel == 5:
                Domoticz.Error('Too many errors received: devices are timedout!')
                TimeoutDevice(Devices, All=True)

    def handleTasks(self):
        try:
            Domoticz.Debug('Entering tasks handler')
            while True:
                task = self.tasksQueue.get(block=True)
                if task is None:
                    Domoticz.Debug('Exiting task handler')
                    try:
                        loop = asyncio.get_running_loop()
                        loop.stop()
                        loop.close()
                    except:
                        pass
                    self.MyBMW = None
                    self.myVehicle = None
                    self.tasksQueue.task_done()
                    break

                Domoticz.Debug('Handling task: {}.'.format(task['Action']))
                if task['Action'] == 'Login':
                    try:
                        self.myBMW = MyBMWAccount(Parameters['Mode2'], Parameters['Mode3'], get_region_from_name(self.region))
                        Domoticz.Debug('Login done! MyBMW object: {}'.format(self.myBMW))
                        if self.myBMW:
                            asyncio.run(self.myBMW.get_vehicles())
                    except Exception as err:
                        Domoticz.Error('Error login in MyBMW for user {} and region {}.'.format(Parameters['Mode2'], self.region))
                        Domoticz.Debug('Login error: {}'.format(err))
                        #import traceback
                        #Domoticz.Debug('Login error TRACEBACK: {}'.format(traceback.format_exc()))
                        self.myBMW = None
                        self.errorLevel += 1
                    else:
                        self.myVehicle = self.myBMW.get_vehicle(Parameters['Mode4'])
                        if self.myVehicle:
                            Domoticz.Status('Login successful! Car {} (VIN:{}) found!'.format(self.myVehicle.name, Parameters['Mode4']))
                            self.updateVehicleStatus()
                        else:
                            Domoticz.Error('vin {} not found for user {}.'.format(Parameters['Mode4'], Parameters['Mode2']))
                            TimeoutDevice(Devices, All=True)

                elif task['Action'] == 'StatusUpdate':
                    if self.myBMW:
                        try:
                            asyncio.run(self.myBMW.get_vehicles())
                        except:
                            if not self.errorLevel:
                                Domoticz.Log('Error occured in getting the status update of the BMW.')
                            self.errorLevel += 1
                        else:
                            self.myVehicle = self.myBMW.get_vehicle(Parameters['Mode4'])
                            if self.myVehicle:
                                Domoticz.Debug('Car {} found after update!'.format(self.myVehicle.name))
                                self.updateVehicleStatus()
                                self.errorLevel = 0
                            else:
                                if not self.errorLevel:
                                    Domoticz.Log('BMW with VIN {} not found for user {}.'.format(Parameters['Mode4'], Parameters['Mode2']))
                                self.errorLevel += 1
                            
                elif task['Action'] in [REMOTE_LIGHT_FLASH, REMOTE_DOOR_LOCK, REMOTE_DOOR_UNLOCK, REMOTE_HORN, REMOTE_AIR_CONDITIONING]:
                    if self.myVehicle:
                        try:
                            if task['Action'] == REMOTE_LIGHT_FLASH:
                                Status = asyncio.run(self.myVehicle.remote_services.trigger_remote_light_flash())
                            elif task['Action'] == REMOTE_HORN:
                                Status = asyncio.run(self.myVehicle.remote_services.trigger_remote_horn())
                            elif task['Action'] == REMOTE_AIR_CONDITIONING:
                                Status = asyncio.run(self.myVehicle.remote_services.trigger_remote_air_conditioning())
                            elif task['Action'] == REMOTE_DOOR_LOCK:
                                Status = asyncio.run(self.myVehicle.remote_services.trigger_remote_door_lock())
                            elif task['Action'] == REMOTE_DOOR_UNLOCK:
                                Status = asyncio.run(self.myVehicle.remote_services.trigger_remote_door_unlock())
                            if Status.state != ExecutionState.EXECUTED:
                                 Domoticz.Error('Error executing remote service {} for {} (not executed).'.format(task['Action'], Parameters['Mode4']))
                        except Exception as err:
                            Domoticz.Error('Error executing remote service {} for {} (unknown error).'.format(task['Action'], Parameters['Mode4']))
                            Domoticz.Debug('Remote service error: {}'.format(err))
                    else:
                        Domoticz.Error('BMW with VIN {} not found for user {}.'.format(Parameters['Mode4'], Parameters['Mode2']))
                    UpdateDevice(False, Devices, _UNIT_REMOTE_SERVICES, 2, 0)
    
                else:
                     Domoticz.Error('Invalid task/action name: {}.'.format(task['Action']))

                self.tasksQueue.task_done()
                Domoticz.Debug('Finished handling task: {}.'.format(task['Action']))

        except Exception as err:
            self.tasksQueue.task_done()
            Domoticz.Error('General error TaskHandler: {}'.format(err))

    def updateVehicleStatus(self):

        # Update status Doors
        if self.myVehicle.doors_and_windows.all_lids_closed:
            UpdateDevice(False, Devices, _UNIT_DOORS, 0, 0)
        else:
            UpdateDevice(False, Devices, _UNIT_DOORS, 1, 0)
    
        # Update status Windows
        if self.myVehicle.doors_and_windows.all_windows_closed:
            UpdateDevice(False, Devices, _UNIT_WINDOWS, 0, 0)
        else:
            UpdateDevice(False, Devices, _UNIT_WINDOWS, 1, 0)

        # Update status Locked
        if self.myVehicle.doors_and_windows.door_lock_state == 'LOCKED':
            UpdateDevice(False, Devices, _UNIT_CAR, 0, 0)
        else:
            if UpdateDevice(False, Devices, _UNIT_CAR, 1, 0):
                Domoticz.Debug('Car is opened now!')
                self.last_car_opened_time = datetime.datetime.now()
                self.car_opened_status_given = False

        # Update Mileage
        UpdateDevice(False, Devices, _UNIT_MILEAGE, self.myVehicle.mileage[0], self.myVehicle.mileage[0])
        UpdateDevice(False, Devices, _UNIT_MILEAGE_COUNTER, 0, self.myVehicle.mileage[0])
        if self.myVehicle.mileage[1] not in Devices[_UNIT_MILEAGE].Options['Custom']:
            UpdateDeviceOptions(Devices, _UNIT_MILEAGE, Options={'Custom': '0;{}'.format(self.myVehicle.mileage[1])})
        if self.myVehicle.mileage[1] not in Devices[_UNIT_MILEAGE_COUNTER].Options['ValueUnits']:
            UpdateDeviceOptions(Devices, _UNIT_MILEAGE_COUNTER, Options={'ValueUnits': self.myVehicle.mileage[1], 'ValueQuantity': self.myVehicle.mileage[1]})
            
        # Update Remaining mileage
        if self.myVehicle.fuel_and_battery.remaining_range_electric != (None, None):
            UpdateDevice(False, Devices, _UNIT_REMAIN_RANGE_ELEC, self.myVehicle.fuel_and_battery.remaining_range_electric[0], self.myVehicle.fuel_and_battery.remaining_range_electric[0])
            if self.myVehicle.fuel_and_battery.remaining_range_electric[1] not in Devices[_UNIT_REMAIN_RANGE_ELEC].Options['Custom']:
                UpdateDeviceOptions(Devices, _UNIT_REMAIN_RANGE_ELEC, Options={'Custom': '0;{}'.format(self.myVehicle.fuel_and_battery.remaining_range_electric[1])})
        if self.myVehicle.fuel_and_battery.remaining_range_fuel != (None, None):
            UpdateDevice(False, Devices, _UNIT_REMAIN_RANGE_FUEL, self.myVehicle.fuel_and_battery.remaining_range_fuel[0], self.myVehicle.fuel_and_battery.remaining_range_fuel[0])
            if self.myVehicle.fuel_and_battery.remaining_range_fuel[1] not in Devices[_UNIT_REMAIN_RANGE_FUEL].Options['Custom']:
                UpdateDeviceOptions(Devices, _UNIT_REMAIN_RANGE_FUEL, Options={'Custom': '0;{}'.format(self.myVehicle.fuel_and_battery.remaining_range_fuel[1])})

        # Update Electric charging
        if self.myVehicle.fuel_and_battery.charging_status != None:
            if self.myVehicle.fuel_and_battery.charging_status == 'CHARGING':
                UpdateDevice(False, Devices, _UNIT_CHARGING, 1, 1)
            else:
                UpdateDevice(False, Devices, _UNIT_CHARGING, 0, 0)

        # Update Charging Percentage
        if self.myVehicle.fuel_and_battery.remaining_battery_percent != None:
            UpdateDevice(False, Devices, _UNIT_BAT_LEVEL, self.myVehicle.fuel_and_battery.remaining_battery_percent, self.myVehicle.fuel_and_battery.remaining_battery_percent)

        # Update Charging Time (minutes)
        if self.myVehicle.fuel_and_battery.charging_end_time:
            charging_time_remaining = round((self.myVehicle.timestamp-self.myVehicle.fuel_and_battery.charging_end_time)/3600, 2)
            UpdateDevice(False, Devices, _UNIT_CHARGING_REMAINING, charging_time_remaining, charging_time_remaining)

        # Location of vehicle
        home_location = Settings['Location'].split(';')
        self.car_location = (self.myVehicle.vehicle_location.location.latitude, self.myVehicle.vehicle_location.location.longitude)
        distance = getDistance(self.car_location, (float(home_location[0]), float(home_location[1])))
        Domoticz.Debug('Distance car-home: {} km'.format(distance))
        if distance*1000 < self.entering_home_distance:
            UpdateDevice(False, Devices, _UNIT_HOME, 1, 1)
        else:
            UpdateDevice(False, Devices, _UNIT_HOME, 0, 0)
        
        # Update driving status
        #if self.myVehicle.is_vehicle_active:
        if self.last_car_location != (None, None):
            if self.last_car_location == self.car_location:
                UpdateDevice(False, Devices, _UNIT_DRIVING, 0, 0)
            else:
                UpdateDevice(False, Devices, _UNIT_DRIVING, 1, 1)
        self.last_car_location = self.car_location

        # Switch for remote services
        if Devices[_UNIT_REMOTE_SERVICES].TimedOut == TIMEDOUT:
            UpdateDevice(False, Devices, _UNIT_REMOTE_SERVICES, Devices[_UNIT_REMOTE_SERVICES].nValue, Devices[_UNIT_REMOTE_SERVICES].sValue, TimedOut=0)


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
# Specific helper functions
################################################################################
