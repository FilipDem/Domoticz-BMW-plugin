#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BMW Python Plugin for Domoticz

This plugin integrates BMW vehicles with Domoticz home automation system.
It uses the offical BMW's API (CarData) and creates
corresponding devices in Domoticz.

Author: Filip Demaertelaere
Version: 5.0.0
License: MIT
"""
"""
<plugin key="Bmw" name="BMW CarData" author="Filip Demaertelaere" version="5.0.0">
    <description>
        <h2>Introduction</h2>
        <p>The BMW CarData plugin provides a robust and seamless integration of your BMW vehicle with the Domoticz home automation system, essentially transforming Domoticz into a comprehensive command center for your car.</p>
        <p>Upon successful configuration, the plugin automatically creates a suite of virtual devices within Domoticz. These devices represent key aspects of your BMW's status, including mileage, door and window lock states, fuel and electric range, charging status, and the vehicle's real-time location and movement.</p>
        <p>To ensure optimal performance and security, this plugin requires a valid MyBMW account with corresponding credentials.</p>
        <p>It is important to note that this plugin is entirely dependent on the data made available by the BMW Open Data Platform. The BMW CarData plugin utilizes the Streaming API (MQTT-based) to retrieve vehicle information, meaning there is no periodic polling by the Domoticz API towards the BMW Open Data Platform. For detailed information, please refer to the official resource: <a href="https://bmw-cardata.bmwgroup.com/thirdparty/public/car-data/overview">https://bmw-cardata.bmwgroup.com/thirdparty/public/car-data/overview</a>.</p>
        <br/>
        <h2>Activation of BMW CarData</h2>
        <p>The steps below summarize how to activate the BMW CarData service within the MyBMW portal. For a detailed, comprehensive guide, please visit the official documentation: <a href="https://bmw-cardata.bmwgroup.com/customer/public/api-documentation/Id-Introduction">https://bmw-cardata.bmwgroup.com/customer/public/api-documentation/Id-Introduction</a>.</p>
        <ul>
            <li>Navigate to the MyBMW Portal, log in with your credentials, and go to the "Vehicle Overview" section.</li>
            <li>Proceed to the "BMW CarData" section.</li>
            <li>Scroll down to the "TECHNICAL ACCESS TO BMW CARDATA" section.</li>
            <li>Click on "Create CarData-client" and ensure both "Request Access to CarData API" and "CarData Stream" options are activated.</li>
            <li>Scroll to the "STREAM CARDATA" section and click "Change data selection."</li>
            <li>Select all data keys you wish to include in the stream. Refer to the **Streaming Configuration** section below for required keys.</li>
        </ul>
        <br/>
        <h2>Configuration Parameters</h2>
        <p>The following parameters are required for initial plugin setup:</p>
        <ul>
            <li><b>BMW CarData Client_id</b>: The unique value obtained from the MyBMW portal after creating the CarData Client.</li>
            <li><b>Vehicle Identification Number (VIN)</b>: The full, 17-character VIN of your BMW vehicle, used to identify the specific car to monitor.</li>
            <li><b>Update Interval (Minutes)</b>: Defines the maximum frequency (in minutes) at which the plugin will check for new data, provided information is made available by the BMW CarData service.</li>
            <li><b>Debug Level</b>: Sets the logging verbosity. Higher levels provide more diagnostic information for troubleshooting purposes.</li>
        </ul>
        <br/>
        <h2>OAuth2 Authentication</h2>
        <p>When the plugin is started for the first time, an authentication status message will appear in the Domoticz log. Copy the complete verification URI, open it in your browser, and complete the process before the displayed expiry time (you may be prompted to re-enter your MyBMW username and password).</p>
        <pre><code>
        ============================================================<br/>
        BMW CarData Authentication Required<br/>
        ============================================================<br/>
        User Code: [client_id]<br/>
        Please visit: [verification_uri_complete]<br/>
        Complete the authentication in your browser before 15:30:00...<br/>
        ============================================================<br/>
        </code></pre>
        <p>Upon successful authentication, you will see the confirmation message: "BMW CarData Authentication successful! Starting BMW CarData MQTT connection..." in the Domoticz log.</p>
        <br/>
        <h2>Streaming configuration (Bmw_keys_streaming.json)</h2>
        <p>The configuration file, "Bmw_keys_streaming.json," maps BMW CarData streaming keys to the corresponding implemented Domoticz devices. This JSON file supports multiple cars. The default settings should typically be correct and require no changes. The example shows configurations for a fuel car and a hybrid fuel/electric car.</p>
        <p>Ensure you update the configuration file with your specific VIN(s). You may add or remove VIN sections to monitor multiple or fewer vehicles.</p>
        <p>Configuration Rules:</p>
        <ul>
            <li>If a device status depends on **one single** BMW CarData key, list only that key (e.g., mileage information).</li>
            <li>If a device status depends on data from **several** BMW CarData keys, use a JSON array. A wildcard (`*`) can be used to capture related keys (e.g., status of all windows).</li>
            <li>If an option is removed or not required, deleting its entry from the JSON file will automatically set the corresponding Domoticz device to **UNUSED** (e.g., removing 'Charging' status for a gasoline-only vehicle).</li>
        </ul>
        <p>Note that information will only be available if the respective BMW CarData keys are actively included in the data stream (as configured in the "Activation of BMW CarData" chapter above).</p>
        <p>Example of the configuration file:</p>
        <pre><code>
        {<br/>
        "WBAJF11YYYYYYYYYY": {<br/>
        &#9;"Mileage": "vehicle.vehicle.travelledDistance",<br/>
        &#9;"Doors": ["vehicle.cabin.door*isOpen", "vehicle.body.trunk*door.isOpen"],<br/>
        &#9;"Windows": ["vehicle.cabin.window*status", "vehicle.cabin.sunroof.overallStatus"],<br/>
        &#9;"Locked": "vehicle.cabin.door.status",<br/>
        &#9;"Location": ["vehicle.cabin.infotainment.navigation.currentLocation.latitude", "vehicle.cabin.infotainment.navigation.currentLocation.longitude"],<br/>
        &#9;"Driving": "vehicle.isMoving",<br/>
        &#9;"RemainingRangeTotal": "vehicle.drivetrain.totalRemainingRange"<br/>
        &#9;},<br/>
        "WBA21EFXXXXXXXXXX": {<br/>
        &#9;"Mileage": "vehicle.vehicle.travelledDistance",<br/>
        &#9;"Doors": ["vehicle.cabin.door*isOpen", "vehicle.body.trunk*door.isOpen"],<br/>
        &#9;"Windows": ["vehicle.cabin.window*status", "vehicle.cabin.sunroof.overallStatus"],<br/>
        &#9;"Locked": "vehicle.cabin.door.status",<br/>
        &#9;"Location": ["vehicle.cabin.infotainment.navigation.currentLocation.latitude", "vehicle.cabin.infotainment.navigation.currentLocation.longitude"],<br/>
        &#9;"Driving": "vehicle.isMoving",<br/>
        &#9;"RemainingRangeTotal": "vehicle.drivetrain.totalRemainingRange",<br/>
        &#9;"RemainingRangeElec": "vehicle.drivetrain.electricEngine.kombiRemainingElectricRange",<br/>
        &#9;"Charging": "vehicle.drivetrain.electricEngine.charging.hvStatus",<br/>
        &#9;"BatteryLevel": "vehicle.drivetrain.batteryManagement.header",<br/>
        &#9;"ChargingTime": "vehicle.drivetrain.electricEngine.charging.timeRemaining"<br/>
        &#9;}<br/>
        }<br/>
        </code></pre>
    </description>
    <params>
        <param field="Mode1" label="BMW CarData Client_id" width="200px" required="true" default=""/>
        <param field="Mode2" label="Vehicle Identification Number (VIN)" width="200px" required="true" default=""/>
        <param field="Mode5" label="Update Interval (Minutes)" width="120px" required="true" default="5"/>
        <param field="Mode6" label="Debug Level" width="120px">
            <options>
                <option label="None" value="0" default="true"/>
                <option label="Python Only" value="2"/>
                <option label="Basic Debugging" value="62"/>
                <option label="Basic+Messages" value="126"/>
                <option label="Queue" value="128"/>
                <option label="Connections Only" value="16"/>
                <option label="Connections+Queue" value="144"/>
                <option label="All" value="-1"/>
            </options>
        </param>
    </params>
</plugin>"""

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from enum import IntEnum, Enum, auto
import base64
import hashlib
import secrets
import urllib.parse
import json
from typing import Any, Dict, List, Type, Union
from datetime import datetime, timedelta
import paho.mqtt.client as mqtt

import DomoticzEx as Domoticz
from domoticzEx_tools import (
    DomoticzConstants, dump_config_to_log, update_device, get_unit,
    get_config_item_db, set_config_item_db, get_distance,
    get_device_n_value
)

class UnitIdentifiers(IntEnum):
    """Enum defining unit identifiers for various BMW data points in Domoticz"""
    MILEAGE = auto()
    DOORS = auto()
    WINDOWS = auto()
    REMAIN_RANGE_TOTAL = auto()
    REMAIN_RANGE_ELEC = auto()
    CHARGING = auto()
    CHARGING_REMAINING = auto()
    BAT_LEVEL = auto()
    REMOTE_SERVICES = auto()
    CAR = auto()
    MILEAGE_COUNTER = auto()
    DRIVING = auto()
    HOME = auto()
    AC_LIMITS = auto()
    CHARGING_MODE = auto()

class CarDataURLs(str, Enum):
    """Enum defining various BMW url points"""
    MQTT_HOST = 'customer.streaming-cardata.bmwgroup.com'
    MQTT_PORT = '9000'
    MQTT_KEEP_ALIVE = '15'
    BMW_HOST = 'customer.bmwgroup.com'
    BMW_PORT = '443'
    API_HOST = 'api-cardata.bmwgroup.com'
    API_PORT = '443'
    API_VERSION = 'v1'
    DEVICE_CODE_URI = '/gcdm/oauth/device/code'
    TOKEN_URI = '/gcdm/oauth/token'
    CREATE_CONTAINER_URI = '/customers/containers'

class Authenticate(IntEnum):
    """State machine during authentication"""
    INIT = auto()
    OAUTH2 = auto()
    USER_INTERACTION = auto()
    DONE = auto()
    ERROR = auto()
    REFRESH_TOKEN = auto()

class AuthenticationData:
    """Store Authentication data"""
    state_machine: int = Authenticate.INIT
    client_id: str = None
    vin: str = None
    code_verifier: str = None
    device_code: str = None
    expires_in: int = None
    interval: int = None

class APIData:
    """Store API data"""
    container_id = None

# Default image for devices
_IMAGE = 'Bmw'

# Streaming key filename
_STREAMING_KEY_FILE = 'Bmw_keys_streaming.json'

# Constants for workaround isMoving
VELOCITY_THRESHOLD_MPS = 2
STOP_TIME_THRESHOLD_SEC = 360  

class CarMovementDetector:
    def __init__(self):
        # State variables to store the last known coordinates and time
        self.last_coord = None
        self.last_timestamp = datetime.now()
        
        # State variables for the "Time-in-Stop" filter
        self.stop_start_time = None
        self.is_currently_moving = False # True/False state for final output
        self.velocity = 0

    def process_new_data(self, location, current_timestamp_sec):
        """
        Main function to process a new set of coordinates.
        current_timestamp_sec: time in seconds (e.g., from time.time())
        """
        
        # Calculate Delta Distance and Delta Time
        delta_t = (current_timestamp_sec - self.last_timestamp).total_seconds()
        
        # Skip if no new coordinates
        if not location:
            if delta_t >= STOP_TIME_THRESHOLD_SEC:
                self.is_currently_moving = False
            return f"NO UPDATE (since {delta_t}s)"

        # Initialize the first point if it doesn't exist
        if self.last_coord is None:
            self.last_coord = location
            self.last_timestamp = current_timestamp_sec
            return "INITIALIZING" # Assume moving or unknown initially

        # Prevent division by zero if timestamps are identical (or too close)
        if delta_t < 2: 
            return "MOVEMENT_STATUS_SAME" # Not enough time passed to measure movement
        delta_d = get_distance(self.last_coord, location, unit='m')

        # Calculate Velocity
        self.velocity = delta_d / delta_t # Meters per second (MPS)
        Domoticz.Debug(f'delta_t={delta_t}; delta_d={delta_d}; self.velocity={self.velocity}')

        # Update state for the next cycle
        self.last_coord = location
        self.last_timestamp = current_timestamp_sec

        # Apply the Movement Logic and Time-in-Stop Filter
        if self.velocity > VELOCITY_THRESHOLD_MPS:
            # Car is actively moving (e.g., driving on a road)
            self.stop_start_time = None  # Reset the stop timer
            self.is_currently_moving = True
            return "MOVING (Active Driving)"
        else:
            # Car is not moving fast enough (stopped at light, traffic, or parked)
            if self.stop_start_time is None:
                # First time detecting a stop - start the timer
                self.stop_start_time = current_timestamp_sec
                self.is_currently_moving = True # Still considered 'moving' in the sense of being in traffic/a temporary stop
                return "MOVING (Traffic/Red Light - Timer Started)"
            else:
                # Check how long the car has been "stopped" (below threshold)
                time_in_stop = (current_timestamp_sec - self.stop_start_time).total_seconds()
                if time_in_stop >= STOP_TIME_THRESHOLD_SEC:
                    # Car has been stationary long enough to be considered NOT MOVING/PARKED
                    self.is_currently_moving = False
                    return "STOPPED (Final Destination/Parked)"
                else:
                    # Still within the temporary stop window (Red light/Traffic Jam)
                    # For the user, this should still be considered "Moving" or "In Transit"
                    self.is_currently_moving = True
                    return "MOVING (Traffic Jam/Long Red Light)"

################################################################################
# Start Plugin
################################################################################
class BasePlugin:
    """
    Main plugin class for the BMW Domoticz integration.
    Handles communication with the BMW CarData API and manages device updates.
    """

    def __init__(self):
        self.runAgain = 0
        self.runUpdate = DomoticzConstants.MINUTE
        self.runAPI = 0
        self.Stop = False
        self.tokens = {}
        self.mqtt_client = None
        self.bmwData = {}
        self.streamingKeys = {}
        self.isMoving = CarMovementDetector()

    def onStart(self):
        Domoticz.Debug('onStart called')

        # Debugging
        if Parameters["Mode6"] != '0':
            try:
                Domoticz.Debugging(int(Parameters["Mode6"]))
                DumpConfigToLog(Parameters, Devices)
            except:
                pass

        # Create the BMW image if not present
        if _IMAGE not in Images:
            Domoticz.Image(f'{_IMAGE}.zip').Create()

        # Add other images
        for image in os.listdir(Parameters['HomeFolder']):
            if image.endswith('.zip') and image.startswith('_IMAGE') and image != f'{_IMAGE}.zip':
                Domoticz.Image(image).Create()

        # Create devices
        self.create_devices()

        # Get CarData client_id and vin
        AuthenticationData.client_id = Parameters["Mode1"]
        AuthenticationData.vin = Parameters["Mode2"]

        # Set up connections
        self.oauth2 = Domoticz.Connection(
                Name='OAuth2', 
                Transport='TCP/IP',
                Protocol='HTTPS', 
                Address=CarDataURLs.BMW_HOST, 
                Port=CarDataURLs.BMW_PORT
            )
        self.api = Domoticz.Connection(
                Name='API', 
                Transport='TCP/IP',
                Protocol='HTTPS', 
                Address=CarDataURLs.API_HOST, 
                Port=CarDataURLs.API_PORT
            )

        # Authenticate
        AuthenticationData.state_machine = Authenticate.INIT
        self.authenticate()

        # Read key streaming file
        self._read_streaming_keys_file()

        # Update interval of devices
        self.runUpdate = DomoticzConstants.MINUTE * int(Parameters['Mode5'])

    def onStop(self):
        Domoticz.Debug('onStop called')
        self.Stop = True
        if self.oauth2 and self.oauth2.Connected():
            self.oauth2.Disconnect()
        self.disconnect_mqtt(reconnect=False)

    def onConnect(self, Connection, Status, Description):
        if self.Stop: return
        Domoticz.Debug(f'onConnect called with status {Status} - {Connection.Name}')

        if Connection == self.oauth2:
            if Status == 0:
                Domoticz.Debug('OAuth2 connection successful.')
                self.authenticate()
            else:
                Domoticz.Debug(f'OAuth2 connection error ({Description}). Trying again in 1 minute...')
                AuthenticationData.state_machine = Authenticate.ERROR
                self.runAgain = DomoticzConstants.MINUTE

    def onCommand(self, DeviceID, Unit, Command, Level, Color):
        if self.Stop: return
        Domoticz.Debug('onCommand called for DeviceID/Unit: {}/{} - Parameter: {} - Level: {}'.format(DeviceID, Unit, Command, Level))

    def onDisconnect(self, Connection):
        Domoticz.Debug(f'onDisconnect called {Connection.Name}')

    def onMessage(self, Connection, Data):
        if self.Stop: return
        #Domoticz.Debug(f'onMessage called from {Connection.Name}')
        Domoticz.Debug(f'onMessage called from {Connection.Name}: {Data}')

        if Connection == self.oauth2:
            if AuthenticationData.state_machine == Authenticate.OAUTH2:
                if Data.get('Status', None) == '200':
                    AuthenticationData.state_machine = Authenticate.USER_INTERACTION
                    self.authenticate(json.loads(Data['Data']))
                else:
                    Domoticz.Error(f"Error during authentication ({Data.get('Status', None)}): {json.loads(Data['Data'])}.")
                
            elif AuthenticationData.state_machine == Authenticate.USER_INTERACTION:
                status = Data.get('Status', None) 
                data = json.loads(Data['Data'])
                if status == '200':
                    self.oauth2.Disconnect()
                    self._store_tokens(data)
                    AuthenticationData.state_machine = Authenticate.DONE
                    Domoticz.Status('BMW CarData Authentication successful! Starting BMW CarData MQTT connection...')
                    # Reconnection with new tokens required
                    self.disconnect_mqtt(reconnect=True)
                    self.runAgain = DomoticzConstants.MINUTE
                elif status in ['400', '401', '403']:
                    error = data.get('error', '')
                    if error == 'authorization_pending':
                        self.runAgain = AuthenticationData.interval // Domoticz.Heartbeat()
                    elif error == 'slow_down':
                        AuthenticationData.interval += Domoticz.Heartbeat()
                        Domoticz.Debug('Request to slow down polling!')
                        self.runAgain = AuthenticationData.interval // Domoticz.Heartbeat()
                    elif error == 'expired_token':
                        Domoticz.Error('BMW CarData Authentication was not completed in the browser in due time.')
                        AuthenticationData.state_machine = Authenticate.ERROR
                    elif error == 'access_denied':
                        Domoticz.Error('BMW CarData Authentication was denied.')
                        AuthenticationData.state_machine = Authenticate.ERROR
                    else:
                        Domoticz.Error(f'BMW CarData Authentication error ({status}): {error}')
                        AuthenticationData.state_machine = Authenticate.ERROR
                else:
                    Domoticz.Error(f'BMW CarData Authentication Unexpected response ({status}): {data}')
                    AuthenticationData.state_machine = Authenticate.ERROR

            elif AuthenticationData.state_machine == Authenticate.REFRESH_TOKEN:
                if Data.get('Status', None) == '200':
                    self.oauth2.Disconnect()
                    AuthenticationData.state_machine = Authenticate.DONE
                    self._store_tokens(json.loads(Data['Data']))
                    Domoticz.Debug('Tokens refreshed successfully; reconnect MQTT...')
                    # Reconnection with new tokens required
                    self.disconnect_mqtt(reconnect=True)
                    self.runAgain = DomoticzConstants.MINUTE
                    AuthenticationData.state_machine = Authenticate.DONE
                else:
                    Domoticz.Debug(f"Error refreshing tokens ({Data.get('Status', None)}): {json.loads(Data['Data'])}. Restarting authentication...")
                    AuthenticationData.state_machine = Authenticate.OAUTH2
                    self.authenticate()

        elif Connection == self.api:
            if not APIData.container_id and Data.get('Status', None) == '201':
                container = json.loads(Data['Data'])
                container.pop('technicalDescriptors')
                set_config_item_db(key='container', value=container)
                Domoticz.Debug(f'Container created: {container}')
            elif APIData.container_id and Data.get('Status', None) == '200':
                # Correct answer on TelematicData
                pass
            else:
                Domoticz.Debug(f"Error creating container ({Data.get('Status', None)}): {json.loads(Data['Data'])}.")

    def onHeartbeat(self):
        if self.Stop: return

        self.runAgain -= 1
        if self.runAgain <= 0:
            #Domoticz.Debug(f'Hearbeat status Authentication: {AuthenticationData.state_machine}')
            if AuthenticationData.state_machine == Authenticate.USER_INTERACTION:
                # Polling waiting for user interaction
                self.authenticate()
            elif AuthenticationData.state_machine == Authenticate.ERROR:
                # Restart authentication in cause of error
                AuthenticationData.state_machine = Authenticate.INIT
                self.authenticate()
            elif AuthenticationData.state_machine == Authenticate.DONE:
                # Monitor and refresh tokens as needed.
                self._ensure_valid_id_token()
                # Ensure MQTT connection
                self.connect_mqtt()
                # Workaround to deduct if vehicle is driving or not
                self.workaround_driving()
                self.runAgain = DomoticzConstants.MINUTE
            else:
                self.runAgain = DomoticzConstants.MINUTE

        self.runUpdate -= 1
        if self.runUpdate <= 0:
            Domoticz.Debug(f'Status BMW(s): {self.bmwData}')
            # Read bmw keys streaming file if change was detected
            try:
                if self.streamingKeysDatim != os.path.getmtime(f"{Parameters['HomeFolder']}{_STREAMING_KEY_FILE}"):
                    Domoticz.Debug(f'Reading updated file {_STREAMING_KEY_FILE}.')
                    self._read_streaming_keys_file()
            except:
                pass
            self.update_devices()
            self.runUpdate = DomoticzConstants.MINUTE * int(Parameters['Mode5'])

        """
        if AuthenticationData.state_machine == Authenticate.DONE:
            self.runAPI -= 1
            if self.runAPI <= 0:
                if not (self.api.Connected() or self.api.Connecting() ):
                    self.api.Connect()
                else:
                    if APIData.container_id:
                        pass #get status
                    else:
                        APIData.container_id = get_config_item_db(key='container', default={})
                        if not APIData.container_id:
                            self._create_container()
                    self.runAPI = 100
        """

    def workaround_driving(self):
        """Workaround when the vehicle.isMoving keys is not in the stream."""
        if ( streaming_keys := self.streamingKeys.get('Location', None) ):
            current_location = self._get_status_from_streaming_keys('Location', streaming_keys, float, delete_key=False)
            # Workaround if key "vehicle.isMoving" is not supplied... calculate if vehicle is moving
            result = self.isMoving.process_new_data(current_location, datetime.now())
            Domoticz.Debug(f'Workaround for vehicle isMoving... isMoving={self.isMoving.is_currently_moving}; last_location={self.isMoving.last_coord}; current_location={current_location}; result={result}')
            # Use workaround if no vehicle.isMoving data coming true
            update_device(False, Devices, Parameters['Name'], UnitIdentifiers.DRIVING,
                          1 if self.isMoving.is_currently_moving else 0, 
                          min(max((self.isMoving.velocity/33.33)*100, 0.0), 100.0) if self.isMoving.is_currently_moving else 0)

    def update_devices(self):
        """Update the devices Domoticz"""
        if self.Stop:
            return
        
        if not self.bmwData.get(AuthenticationData.vin, None):
            return

        # Update Mileage
        if not ( streaming_keys := self.streamingKeys.get('Mileage', None) ):
            update_device( False, Devices, Parameters['Name'], UnitIdentifiers.MILEAGE, Used=0 )
            update_device( False, Devices, Parameters['Name'], UnitIdentifiers.MILEAGE_COUNTER, Used=0 )
        else:
            if status := self._get_status_from_streaming_keys('Mileage', [streaming_keys], int):
                unit = self.bmwData[AuthenticationData.vin].get(streaming_keys, {}).get('unit', 'km')
                update_device( False, Devices, Parameters['Name'], UnitIdentifiers.MILEAGE,
                               status[0], status[0], 
                               Options={'Custom': f"0;{unit}"}
                             )
                update_device( False, Devices, Parameters['Name'], UnitIdentifiers.MILEAGE_COUNTER,
                               0, status[0],
                               Options={'ValueUnits': unit, 'ValueQuantity': unit}
                             )

        # Update status of Doors
        if not ( streaming_keys := self.streamingKeys.get('Doors', None) ):
            update_device( False, Devices, Parameters['Name'], UnitIdentifiers.DOORS, Used=0 )
        else:
            if status := self._get_status_from_streaming_keys('Doors', streaming_keys, bool):
                update_device( False, Devices, Parameters['Name'], UnitIdentifiers.DOORS,
                               1 if any(status) else 0, 0 )

        # Update status of Windows
        if not ( streaming_keys := self.streamingKeys.get('Windows', None) ):
            update_device( False, Devices, Parameters['Name'], UnitIdentifiers.WINDOWS, Used=0 )
        else:
            if status := self._get_status_from_streaming_keys('Windows', streaming_keys, ['OPEN', 'INTERMEDIATE', 'CLOSED']):
                update_device( False, Devices, Parameters['Name'], UnitIdentifiers.WINDOWS,
                               0 if all(x == 'CLOSED' for x in status) else 1, 0 )

        # Update door lock status
        if not ( streaming_keys := self.streamingKeys.get('Locked', None) ):
            update_device( False, Devices, Parameters['Name'], UnitIdentifiers.CAR, Used=0 )
        else:
            if status := self._get_status_from_streaming_keys('Locked', [streaming_keys], ['SECURED', 'LOCKED', 'UNLOCKED']):
                update_device( False, Devices, Parameters['Name'], UnitIdentifiers.CAR,
                               0 if status[0] in ['SECURED', 'LOCKED'] else 1, 0 )

        # Location data is available 
        if not ( streaming_keys := self.streamingKeys.get('Location', None) ):
            update_device( False, Devices, Parameters['Name'], UnitIdentifiers.HOME, Used=0 )
        else:
            if status := self._get_status_from_streaming_keys('Location', streaming_keys, float):
                #Domoticz.Debug(f'Current location is: {status}')
                # Parse home location from settings
                home_loc = Settings['Location'].split(';')
                home_point = (float(home_loc[0]), float(home_loc[1]))
                # Calculate distance from home using the tracker
                if distance := get_distance(list(status), home_point, 'm'):
                    #Domoticz.Debug(f'Distance car-home: {distance} m')
                    update_device(False, Devices, Parameters['Name'], UnitIdentifiers.HOME,
                                  1 if distance <= 100 else 0, 100-distance if distance <= 100 else 0)

        # Driving status
        if not ( streaming_keys := self.streamingKeys.get('Driving', None) ):
            update_device( False, Devices, Parameters['Name'], UnitIdentifiers.DRIVING, Used=0 )
        else:
            if status := self._get_status_from_streaming_keys('Driving', [streaming_keys], bool):
                update_device(False, Devices, Parameters['Name'], UnitIdentifiers.DRIVING,
                              1 if status[0] else 0, 100 if status[0] else 0)

        # Update Remaining fuel range
        if not ( streaming_keys := self.streamingKeys.get('RemainingRangeTotal', None) ):
            update_device( False, Devices, Parameters['Name'], UnitIdentifiers.REMAIN_RANGE_TOTAL, Used=0 )
        else:
            if status := self._get_status_from_streaming_keys('RemainingRangeTotal', [streaming_keys], int):
                unit = self.bmwData[AuthenticationData.vin].get(streaming_keys, {}).get('unit', 'km')
                update_device( False, Devices, Parameters['Name'], UnitIdentifiers.REMAIN_RANGE_TOTAL,
                               status[0], status[0], 
                               Options={'Custom': f"0;{unit}"}
                             )

        # Update Remaining electric range
        if not ( streaming_keys := self.streamingKeys.get('RemainingRangeElec', None) ):
            update_device( False, Devices, Parameters['Name'], UnitIdentifiers.REMAIN_RANGE_ELEC, Used=0 )
        else:
            if status := self._get_status_from_streaming_keys('RemainingRangeElec', [streaming_keys], int):
                unit = self.bmwData[AuthenticationData.vin].get(streaming_keys, {}).get('unit', 'km')
                update_device( False, Devices, Parameters['Name'], UnitIdentifiers.REMAIN_RANGE_ELEC,
                               status[0], status[0], 
                               Options={'Custom': f"0;{unit}"}
                             )

        # Update Battery Percentage
        if not ( streaming_keys := self.streamingKeys.get('BatteryLevel', None) ):
            update_device( False, Devices, Parameters['Name'], UnitIdentifiers.BAT_LEVEL, Used=0 )
        else:
            if status := self._get_status_from_streaming_keys('BatteryLevel', [streaming_keys], int):
                update_device(False, Devices, Parameters['Name'], UnitIdentifiers.BAT_LEVEL,
                              status[0], status[0])

        # Update Electric charging status
        if not ( streaming_keys := self.streamingKeys.get('Charging', None) ):
            update_device( False, Devices, Parameters['Name'], UnitIdentifiers.CHARGING, Used=0 )
        else:
            if status := self._get_status_from_streaming_keys('Charging', [streaming_keys], 
                                                               ['NOCHARGING', 'INITIALIZATION', 
                                                                'CHARGINGACTIVE', 'CHARGINGPAUSED', 
                                                                'CHARGINGENDED', 'CHARGINGERROR']
                                                             ):
                charging = status[0]=='CHARGINGACTIVE'
                battery = get_device_n_value(Devices, Parameters['Name'], UnitIdentifiers.BAT_LEVEL) or 0
                update_device(False, Devices, Parameters['Name'], UnitIdentifiers.CHARGING,
                              1 if charging else 0, battery if charging else 0)

        # Update Charging Time (minutes)
        if get_device_n_value(Devices, Parameters['Name'], UnitIdentifiers.CHARGING):
            if not ( streaming_keys := self.streamingKeys.get('ChargingTime', None) ):
                update_device( False, Devices, Parameters['Name'], UnitIdentifiers.CHARGING_REMAINING, Used=0 )
            else:
                if status := self._get_status_from_streaming_keys('ChargingTime', [streaming_keys], int):
                    update_device(False, Devices, Parameters['Name'], UnitIdentifiers.CHARGING_REMAINING,
                                  status[0], status[0])
        else:
            update_device(False, Devices, Parameters['Name'], UnitIdentifiers.CHARGING_REMAINING, 0, 0)

        """
        # Update the AC Limits
        ac_limits_options = None
        if (ac_available_limits := self.my_vehicle.charging_profile.ac_available_limits) is not None:
            Domoticz.Debug(f'Available AC limitations: {ac_available_limits}')
            if ac_available_limits: #should be none-empty list
                level_names = '|' + '|'.join(f'{A} A' for A in ac_available_limits)
                ac_limits_options = {
                    'LevelActions': '|'*len(ac_available_limits),
                    'LevelNames': level_names,
                    'LevelOffHidden': 'true',
                    'SelectorStyle': '1'
                }
        if (ac_current_limit := self.my_vehicle.charging_profile.ac_current_limit) is not None:
            Domoticz.Debug(f'Current AC limitations: {ac_current_limit}')
            try:
                index = ac_available_limits.index(ac_current_limit)+1
            except ValueError:
                index = None
            else:
                if ac_limits_options:
                    update_device(False, Devices, Parameters['Name'], UnitIdentifiers.AC_LIMITS,
                                  2 if index else 0, 10*index if index else 0, Options=ac_limits_options)
                else:
                    update_device(False, Devices, Parameters['Name'], UnitIdentifiers.AC_LIMITS,
                                  2 if index else 0, 10*index if index else 0)

        # Update Charging Mode
        if (charging_mode := self.my_vehicle.charging_profile.charging_mode) is not None:
            Domoticz.Debug(f'Charging mode: {charging_mode}')
            available_charging_modes = get_unit(Devices, Parameters['Name'], UnitIdentifiers.CHARGING_MODE).Options['LevelNames'].split('|')
            try:
                index = available_charging_modes.index(charging_mode)
            except ValueError:
                index = None
            else:
                update_device(False, Devices, Parameters['Name'], UnitIdentifiers.CHARGING_MODE, 2, 10*index)
        """

    def _get_status_from_streaming_keys(self, key_name: str, streaming_keys: List, expected_value: Union[List, Type], delete_key: bool = True) -> List:
        """Parse all the list of streaming keys to get and return their values if matching the correct type"""
        # Parse to get explicit list of streaming keys
        keys = [ key for streaming_key in streaming_keys
                   for key in self.bmwData.get(AuthenticationData.vin, {}).keys() 
                     if '*' in streaming_key and key.startswith(streaming_key.split('*', 1)[0]) and key.endswith(streaming_key.split('*', 1)[1])
                     or '*' not in streaming_key and key == streaming_key
               ]
        # Get status back of all streaming keys
        status = [ self.bmwData[AuthenticationData.vin][key].get('value', 'ERR') for key in keys ]
        # Erase streaming keys from BMWStatus
        if delete_key:
            for key in keys:
                self.bmwData[AuthenticationData.vin].pop(key, None)
        # Check if all return values match expected types
        check = all(x in expected_value for x in status) if isinstance(expected_value, List) else all(isinstance(x, expected_value) for x in status)
        if not check:
            Domoticz.Error(f'{AuthenticationData.vin}: Streaming keys are defined in {_STREAMING_KEY_FILE} for {key_name} that do not return {expected_value}. Key {streaming_keys} gives {status}.')
            return None
        # Return status
        #Domoticz.Debug(f'{key_name}: {status}')
        return status

    def _get_all_streaming_keys(self) -> List:
        """Reads all data elements from a JSON object and compiles them into a single list."""
        
        # The final list to hold all the processed data elements
        container_keys = []

        # Iterate over the values in the dictionary
        for value in self.streamingKeys.values():
            if isinstance(value, str):
                container_keys.append(value)
            elif isinstance(value, list):
                # Use extend() to add individual items from the sub-list to the main list
                container_keys.extend(value)
        Domoticz.Debug(f'Elements for the container are: {container_keys}')
        return container_keys

    def _create_container(self) -> None:
        container_data = {
            'name': AuthenticationData.vin,
            'purpose': 'Telemetry',
            'technicalDescriptors': list(self._get_all_streaming_keys())
        }

        headers = {
            'Host': CarDataURLs.API_HOST,
            'Authorization': f"Bearer {self.tokens['access_token']['token']}",
            'x-version': CarDataURLs.API_VERSION,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        Domoticz.Debug('Create container with all known streaming keys.')
        self.api.Send( {'Verb':'POST', 'URL':CarDataURLs.CREATE_CONTAINER_URI, 'Data':urllib.parse.urlencode(container_data), 'Headers':headers} )

    def authenticate(self, data: Dict[str, Any]=None):
        """Perform OAuth2 Device Code Flow authentication."""

        #import random
        #ran = random.randint(0, 999999)
        #Domoticz.Debug(f"*START {ran:06d}: Calling authenticate function with state_machine={AuthenticationData.state_machine}")
        
        if not self.oauth2.Connected():
            Domoticz.Debug('Not connected to OAUTH2 authentication server: reconnecting...')
            self.oauth2.Connect()
            #Domoticz.Debug(f"*STOP {ran:06d}: Calling authenticate function with state_machine={AuthenticationData.state_machine}")
            return

        if AuthenticationData.state_machine == Authenticate.INIT:
            # Always refresh tokens on startup for fresh hour-long session
            #Domoticz.Debug('Refreshing tokens for fresh session if token is not yet expired...')
            if self._load_tokens():
                Domoticz.Debug('Using refreshed tokens; no need for new authentication')
                self._ensure_valid_id_token(force_update=True)
                # Avoid that tokens are again refreshed, because the state machine switched to Authenticate.REFRESH_TOKEN
                return 
            else:
                Domoticz.Debug('Token refresh failed, proceeding with new authentication...')
                AuthenticationData.state_machine = Authenticate.OAUTH2

        if AuthenticationData.state_machine == Authenticate.OAUTH2:
            Domoticz.Debug('Starting OAuth2 Device Code Flow authentication...')

            # Step 1: Generate PKCE pair
            AuthenticationData.code_verifier, code_challenge = self._generate_pkce_pair()

            # Step 2: Request device and user codes
            device_code_data = {
                'client_id': AuthenticationData.client_id,
                'response_type': 'device_code',
                'scope': 'authenticate_user openid cardata:streaming:read cardata:api:read',
                'code_challenge': code_challenge,
                'code_challenge_method': 'S256'
            }

            headers = {
                'Host': CarDataURLs.BMW_HOST,
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            #Domoticz.Debug(f'Request device and user tokens - Sending HTTP POST to {CarDataURLs.DEVICE_CODE_URI}: headers={headers} - data={urllib.parse.urlencode(device_code_data)}')
            self.oauth2.Send( {'Verb':'POST', 'URL':CarDataURLs.DEVICE_CODE_URI, 'Data':urllib.parse.urlencode(device_code_data), 'Headers':headers} )

        if AuthenticationData.state_machine == Authenticate.USER_INTERACTION:
            if data:
                # Extract response data
                user_code = data['user_code']
                AuthenticationData.device_code = data['device_code']
                verification_uri_complete = data['verification_uri_complete']
                AuthenticationData.expires_in = data['expires_in']
                AuthenticationData.interval = data.get('interval', Domoticz.Heartbeat())

                # Step 3: Display user instructions
                text = '\n' + '=' * 60
                text = text + '\nBMW CarData Authentication Required'
                text = text + '\n' + '=' * 60
                text = text + f'\nUser Code: {user_code}'
                text = text + f'\nPlease visit: {verification_uri_complete}'
                text = text + f"\nComplete the authentication in your browser before {(datetime.now() + timedelta(seconds=AuthenticationData.expires_in)).strftime('%H:%M:%S')}..."
                text = text + '\n' + '=' * 60

                Domoticz.Status(text)
                self.runAgain = AuthenticationData.interval // Domoticz.Heartbeat()
                #Domoticz.Debug(f'Next polling in {self.runAgain} heartbeats (interval = {AuthenticationData.interval}s)')

            else:
                # Step 4: Poll for tokens
                Domoticz.Debug('Polling for the user action to get the tokens.')
                token_data = {
                    'client_id': AuthenticationData.client_id,
                    'device_code': AuthenticationData.device_code,
                    'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
                    'code_verifier': AuthenticationData.code_verifier
                }
                headers = {
                    'Host': CarDataURLs.BMW_HOST,
                    'Accept': 'application/json',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
                #Domoticz.Debug(f'Poll for tokens - Sending HTTP POST to {CarDataURLs.TOKEN_URI}: headers={headers} - data={urllib.parse.urlencode(token_data)}')
                self.oauth2.Send( {'Verb':'POST', 'URL':CarDataURLs.TOKEN_URI, 'Data':urllib.parse.urlencode(token_data), 'Headers':headers} )
                self.runAgain = AuthenticationData.interval // Domoticz.Heartbeat()

        if AuthenticationData.state_machine == Authenticate.REFRESH_TOKEN:
            refresh_data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.tokens['refresh_token']['token'],
                'client_id': AuthenticationData.client_id
            }
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Host': CarDataURLs.BMW_HOST
            }
            #Domoticz.Debug(f'Refresh tokens - Sending HTTP POST to {CarDataURLs.TOKEN_URI}: headers={headers} - data={urllib.parse.urlencode(refresh_data)}')
            self.oauth2.Send( {'Verb':'POST', 'URL':CarDataURLs.TOKEN_URI, 'Data':urllib.parse.urlencode(refresh_data), 'Headers':headers} )

        #Domoticz.Debug(f"*STOP {ran:06d}: Calling authenticate function with state_machine={AuthenticationData.state_machine}")
        return True

    def connect_mqtt(self):
        """
        Connect to MQTT broker for streaming.
        Using paho mqtt client because the Domoticz build-in MQTT does not support TLS.
        """

        if AuthenticationData.state_machine != Authenticate.DONE:
            Domoticz.Debug('MQTT cannot start because of none-complete authentication.')
            return

        if self.mqtt_client and self.mqtt_client.is_connected():
            #Domoticz.Debug('MQTT already running.')
            return

        Domoticz.Debug('Starting MQTT...')
        self.mqtt_client = mqtt.Client(
            protocol=mqtt.MQTTv5,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        )
        self.mqtt_client.on_connect = self.onMqttConnect
        self.mqtt_client.on_message = self.onMqttMessage
        self.mqtt_client.on_subscribe = self.onMqttSubscribe
        self.mqtt_client.on_disconnect = self.onMqttDisconnect

        self.mqtt_client.tls_set()

        id_token = self.tokens['id_token']['token']
        self.mqtt_client.username_pw_set(self.mqtt_username, id_token)

        try:
            connect_properties = mqtt.Properties(mqtt.PacketTypes.CONNECT)
            connect_properties.SessionExpiryInterval = 0  # Clean start
            Domoticz.Debug('Set up connection to MQTT broker...')
            self.mqtt_client.connect(CarDataURLs.MQTT_HOST, int(CarDataURLs.MQTT_PORT), keepalive=int(CarDataURLs.MQTT_KEEP_ALIVE), properties=connect_properties)
            Domoticz.Debug('Start mqtt client loop...')
            self.mqtt_client.loop_start()
            return True
        except Exception as e:
            Domoticz.Error(f"Error connecting to BMW CarData MQTT broker: {e}")
            return False

    def disconnect_mqtt(self, reconnect: bool=False):
        """Disconnect from MQTT broker."""

        if self.mqtt_client:
            self.mqtt_client.user_data_set({'reconnect': reconnect})
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        elif reconnect:
            self.connect_mqtt()

    def onMqttConnect(self, client, userdata, flags, rc, properties):
        """MQTT connection callback."""

        if rc.value == 0:
            Domoticz.Debug('Connected to MQTT broker successfully')

            topic = f'{self.mqtt_username}/{AuthenticationData.vin}'
            self.mqtt_client.subscribe(topic, qos=1)
            Domoticz.Debug(f'Request to subscribe to topic: {topic} with QoS 1')

            wildcard_topic = f'{self.mqtt_username}/+'
            self.mqtt_client.subscribe(wildcard_topic, qos=1)
            Domoticz.Debug(f'Request to subscribe to wildcard topic: {wildcard_topic} with QoS 1')

            expires_at = datetime.fromisoformat(self.tokens['id_token']['expires_at'])
            time_until_expiry = expires_at - datetime.now()
            Domoticz.Debug(f'ID token expires in: {time_until_expiry}')

            #if hasattr(flags, "session_present"):
            #    Domoticz.Debug(f'Session present: {flags.session_present}')

        else:
            Domoticz.Error(f'Failed to connect to BMW CarData MQTT broker: {rc}.')

    def onMqttMessage(self, client, userdata, msg):
        """MQTT message callback."""

        try:
            data = json.loads(msg.payload.decode())
            Domoticz.Debug(f'Received message on {msg.topic}: {data}')
            #Populate BMW Data structure with received information
            if data['vin'] not in self.bmwData:
                self.bmwData[data['vin']] = {}
            for key, value in data['data'].items(): 
                self.bmwData[data['vin']][key] = value 

        except json.JSONDecodeError:
            Domoticz.Debug(f'Received non-JSON message: {msg.payload.decode()}')
        except Exception as e:
            Domoticz.Debug(f'Error processing message: {e}')

    def onMqttSubscribe(self, client, userdata, mid, reason_codes, properties):
        """MQTT subscription callback."""

        #Domoticz.Debug(f'Subscription confirmed - Message ID: {mid}')
        for i, rc in enumerate(reason_codes):
            Domoticz.Debug(f'Subscription confirmed - Topic {i}: {rc}')

    def onMqttDisconnect(self, client, userdata, flags, rc, properties):
        """MQTT disconnect callback."""

        if rc.value == 0:
            Domoticz.Debug(f"Disconnect after disconnect() successful; reconnect again: {False if not userdata else userdata.get('reconnect', False)}")
            if userdata and userdata.get('reconnect', False):
                self.connect_mqtt()
        else:
            Domoticz.Debug(f'Unexpected disconnection from MQTT broker: {rc}')

            if rc.value in (4, 5):
                Domoticz.Debug('Possible token expiration - checking token validity...')
                if self._is_token_expired('id_token'):
                    Domoticz.Debug('ID token has expired, will refresh on next connection attempt')
            else:
                Domoticz.Debug('Attempting to reconnect through heartbeat loop...')

    def _generate_pkce_pair(self) -> tuple[str, str]:
        """Generate PKCE code verifier and code challenge."""

        code_verifier = (
            base64.urlsafe_b64encode(secrets.token_bytes(32))
            .decode("utf-8")
            .rstrip("=")
        )

        code_challenge = (
            base64.urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode("utf-8")).digest()
            )
            .decode("utf-8")
            .rstrip("=")
        )

        return code_verifier, code_challenge

    def _store_tokens(self, tokens: Dict[str, Any]):
        """Store tokens with expiration timestamps."""

        now = datetime.now()

        # Store access token (in memory only, not persisted)
        if 'access_token' in tokens:
            expires_in = tokens.get('expires_in', 3600)
            self.tokens['access_token'] = {
                'token': tokens['access_token'],
                'expires_at': (now + timedelta(seconds=expires_in)).isoformat(),
                'type': tokens.get('token_type', 'Bearer')
            }

        # Store refresh token (persisted for future use)
        if 'refresh_token' in tokens:
            self.tokens['refresh_token'] = {
                'token': tokens['refresh_token'],
                'expires_at': (now + timedelta(seconds=1209600)).isoformat()  # 2 weeks
            }

        # Store ID token (in memory only, not persisted)
        if 'id_token' in tokens:
            expires_in = tokens.get('expires_in', 3600)
            self.tokens['id_token'] = {
                'token': tokens['id_token'],
                'expires_at': (now + timedelta(seconds=expires_in)).isoformat()
            }

        # Store other data
        if 'gcid' in tokens:
            self.tokens['gcid'] = tokens['gcid']
        if "scope" in tokens:
            self.tokens['scope'] = tokens['scope']

        self._save_tokens_selective()

    def _refresh_id_token(self) -> bool:
        """Refresh access and ID tokens using refresh token."""

        if 'refresh_token' not in self.tokens:
            Domoticz.Debug('No refresh token available')
            return False
        else:
            if self._is_token_expired('refresh_token'):
                Domoticz.Debug('Refresh token available but expired')
                return False

        Domoticz.Debug('Start refresh id token operation...')
        AuthenticationData.state_machine = Authenticate.REFRESH_TOKEN
        self.authenticate()
        return True

    def _ensure_valid_id_token(self, force_update: bool=False) -> None:
        """Ensure we have valid tokens, refreshing if necessary."""

        if self._is_token_expired('id_token') or force_update:
            if self._refresh_id_token():
                Domoticz.Debug(f'Forced update ({force_update}) and/or ID token expired, refreshing using refresh token...')
            else:
                Domoticz.Debug('ID token expired and cannot refresh, need new authentication')
                AuthenticationData.state_machine = Authenticate.OAUTH2
                self.authenticate()
        else:
            Domoticz.Debug(f"ID token still valid until {self.tokens['id_token']['expires_at']}...")

    def _save_tokens_selective(self):
        """Save only refresh token and metadata to db for persistence."""

        persistent_tokens = {}
        persistent_tokens['client_id'] = AuthenticationData.client_id
        if 'refresh_token' in self.tokens:
            persistent_tokens['refresh_token'] = self.tokens['refresh_token']
        if 'gcid' in self.tokens:
            persistent_tokens['gcid'] = self.tokens['gcid']
        if 'scope' in self.tokens:
            persistent_tokens['scope'] = self.tokens['scope']

        Domoticz.Debug(f'Tokens stored to database: {persistent_tokens}')
        set_config_item_db(key='tokens', value=persistent_tokens)

    def _load_tokens(self) -> bool:
        """Load tokens from db if available."""

        self.tokens = get_config_item_db(key='tokens', default={})
        if self.tokens:
            Domoticz.Debug(f'Tokens loaded from database: {self.tokens}')
            if self.tokens.get('client_id', '') != AuthenticationData.client_id:
                Domoticz.Debug(f'Client_id changed: tokens from database do not correspond and will be erased!')
                return False
            return True

        Domoticz.Debug(f'Tokens not loaded from database.')
        return False

    def _is_token_expired(self, token_key: str) -> bool:
        """Check if a token is expired or will expire soon."""

        if token_key not in self.tokens or 'expires_at' not in self.tokens[token_key]:
            return True

        expires_at = datetime.fromisoformat(self.tokens[token_key]['expires_at'])
        return datetime.now() + timedelta(minutes=5) >= expires_at

    @property
    def mqtt_username(self) -> str:
        """Get MQTT username (GCID) from stored tokens."""

        if 'gcid' in self.tokens:
            return self.tokens['gcid']
        raise ValueError('GCID not available - authentication required')

    def _read_streaming_keys_file(self):
        """Read configuration file with the streaming keys"""
        Domoticz.Debug(f"Looking for configuration file {Parameters['HomeFolder']}{_STREAMING_KEY_FILE}...")
        try:
            # Read parameters
            with open(f"{Parameters['HomeFolder']}{_STREAMING_KEY_FILE}") as json_file:
                self.streamingKeys = json.load(json_file).get(AuthenticationData.vin, {})
            self.streamingKeysDatim = os.path.getmtime(f"{Parameters['HomeFolder']}{_STREAMING_KEY_FILE}")
            Domoticz.Debug(f'{_STREAMING_KEY_FILE} read: {self.streamingKeys}.')
            return True
        except Exception as e:
            self.streamingKeys = {}
            Domoticz.Error(f"Problem BMW streaming keys file {Parameters['HomeFolder']}{_STREAMING_KEY_FILE} ({e})!")
            return False

    def create_devices(self) -> None:
        """Create all required devices if they don't exist yet."""
        # Create Mileage device
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.MILEAGE):
            Domoticz.Unit(
                DeviceID=Parameters['Name'],
                Unit=UnitIdentifiers.MILEAGE,
                Name=f"{Parameters['Name']} - Mileage",
                TypeName='Custom',
                Options={'Custom': '0;km'},
                Image=Images[_IMAGE].ID,
                Used=1
            ).Create()

        # Create Mileage Counter device
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.MILEAGE_COUNTER):
            Domoticz.Unit(
                DeviceID=Parameters['Name'],
                Unit=UnitIdentifiers.MILEAGE_COUNTER,
                Name=f"{Parameters['Name']} - Mileage (Day)",
                Type=113,
                Subtype=0,
                Switchtype=3,
                Options={'ValueUnits': 'km'},
                Image=Images[_IMAGE].ID,
                Used=1
            ).Create()

        """
        # Create device for Remote Services
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.REMOTE_SERVICES):
            level_names = '|(select)|' + '|'.join(service.value for service in SupportedBmwRemoteService)
            remote_services_options = {
                'LevelActions': '|'*(len(SupportedBmwRemoteService)+1),
                'LevelNames': level_names,
                'LevelOffHidden': 'true',
                'SelectorStyle': '1'
            }

            Domoticz.Unit(
                DeviceID=Parameters['Name'],
                Unit=UnitIdentifiers.REMOTE_SERVICES,
                Name=f"{Parameters['Name']} - Remote Services",
                TypeName='Selector Switch',
                Options=remote_services_options,
                Image=Images[_IMAGE].ID,
                Used=0
            ).Create()
        """
        if get_unit(Devices, Parameters['Name'], UnitIdentifiers.REMOTE_SERVICES):
            update_device( False, Devices, Parameters['Name'], UnitIdentifiers.REMOTE_SERVICES, Used=0 )

        # Create doors status device
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.DOORS):
            Domoticz.Unit(
                DeviceID=Parameters['Name'],
                Unit=UnitIdentifiers.DOORS,
                Name=f"{Parameters['Name']} - Doors",
                Type=244,
                Subtype=73,
                Switchtype=11,
                Image=Images[_IMAGE].ID,
                Used=1
            ).Create()

        # Create windows status device
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.WINDOWS):
            Domoticz.Unit(
                DeviceID=Parameters['Name'],
                Unit=UnitIdentifiers.WINDOWS,
                Name=f"{Parameters['Name']} - Windows",
                Type=244,
                Subtype=73,
                Switchtype=11,
                Image=Images[_IMAGE].ID,
                Used=1
            ).Create()

        # Create remaining total (fuel+elec) range device
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.REMAIN_RANGE_TOTAL):
            Domoticz.Unit(
                DeviceID=Parameters['Name'],
                Unit=UnitIdentifiers.REMAIN_RANGE_TOTAL,
                Name=f"{Parameters['Name']} - Remaining range (total)",
                TypeName='Custom',
                Options={'Custom': '0;km'},
                Image=Images[_IMAGE].ID,
                Used=1
            ).Create()

        # Create remaining electric range device
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.REMAIN_RANGE_ELEC):
            Domoticz.Unit(
                DeviceID=Parameters['Name'],
                Unit=UnitIdentifiers.REMAIN_RANGE_ELEC,
                Name=f"{Parameters['Name']} - Remaining range (elec)",
                TypeName='Custom',
                Options={'Custom': '0;km'},
                Image=Images[_IMAGE].ID,
                Used=1
            ).Create()

        # Create charging status device
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.CHARGING):
            Domoticz.Unit(
                DeviceID=Parameters['Name'],
                Unit=UnitIdentifiers.CHARGING,
                Name=f"{Parameters['Name']} - Charging",
                Type=244,
                Subtype=73,
                Switchtype=0,
                Image=Images[_IMAGE].ID,
                Used=1
            ).Create()

        # Create charging remaining time device
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.CHARGING_REMAINING):
            Domoticz.Unit(
                DeviceID=Parameters['Name'],
                Unit=UnitIdentifiers.CHARGING_REMAINING,
                Name=f"{Parameters['Name']} - Charging time",
                TypeName='Custom',
                Options={'Custom': '0;min'},
                Image=Images[_IMAGE].ID,
                Used=1
            ).Create()

        # Create battery level device
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.BAT_LEVEL):
            Domoticz.Unit(
                DeviceID=Parameters['Name'],
                Unit=UnitIdentifiers.BAT_LEVEL,
                Name=f"{Parameters['Name']} - Battery Level",
                TypeName='Custom',
                Options={'Custom': '0;%'},
                Image=Images[_IMAGE].ID,
                Used=1
            ).Create()

        # Create car status device (locked/unlocked)
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.CAR):
            Domoticz.Unit(
                DeviceID=Parameters['Name'],
                Unit=UnitIdentifiers.CAR,
                Name=f"{Parameters['Name']} - Car",
                Type=244,
                Subtype=73,
                Switchtype=11,
                Image=Images[_IMAGE].ID,
                Used=1
            ).Create()

        # Create driving status device
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.DRIVING):
            Domoticz.Unit(
                DeviceID=Parameters['Name'],
                Unit=UnitIdentifiers.DRIVING,
                Name=f"{Parameters['Name']} - Driving",
                Type=244,
                Subtype=73,
                Switchtype=0,
                Image=Images[_IMAGE].ID,
                Used=1
            ).Create()

        # Create home status device
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.HOME):
            Domoticz.Unit(
                DeviceID=Parameters['Name'],
                Unit=UnitIdentifiers.HOME,
                Name=f"{Parameters['Name']} - Home",
                Type=244,
                Subtype=73,
                Switchtype=0,
                Image=Images[_IMAGE].ID,
                Used=1
            ).Create()

        # Create device for AC limitation limits
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.AC_LIMITS):
            Domoticz.Unit(
                DeviceID=Parameters['Name'],
                Unit=UnitIdentifiers.AC_LIMITS,
                Name=f"{Parameters['Name']} - AC Limits",
                TypeName='Selector Switch',
                Options={'LevelActions': '|', 'LevelNames': '|(update pending)', 'LevelOffHidden': 'true', 'SelectorStyle': '1'},
                Image=Images[_IMAGE].ID,
                Used=1
            ).Create()
        else:
            update_device( False, Devices, Parameters['Name'], UnitIdentifiers.AC_LIMITS, Used=0 )

        """
        # Create device for Charging Mode
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.CHARGING_MODE):
            charging_mode_options = {
                'LevelActions': '|'*len(ChargingMode),
                'LevelNames': '|' + '|'.join(ChargingMode),
                'LevelOffHidden': 'true',
                'SelectorStyle': '1'
            }
            Domoticz.Unit(
                DeviceID=Parameters['Name'],
                Unit=UnitIdentifiers.CHARGING_MODE,
                Name=f"{Parameters['Name']} - Charging Mode",
                TypeName='Selector Switch',
                Options=charging_mode_options,
                Image=Images[_IMAGE].ID,
                Used=0
            ).Create()
        """
        if get_unit(Devices, Parameters['Name'], UnitIdentifiers.CHARGING_MODE):
            update_device( False, Devices, Parameters['Name'], UnitIdentifiers.CHARGING_MODE, Used=0 )

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

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(DeviceID, Unit, Command, Level, Color):
    global _plugin
    _plugin.onCommand(DeviceID, Unit, Command, Level, Color)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()
    
################################################################################
# Specific helper functions
################################################################################
