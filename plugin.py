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
        <p>Keep in mind that no data is sent by the BMW Open Data Platform in streaming mode when not any event happens at car level.</p>
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
            <li>If a device status depends on data from **several** BMW CarData keys, use a JSON array.</li>
            <li>If an option is removed or not required, deleting its entry from the JSON file will automatically set the corresponding Domoticz device to **UNUSED** (e.g., removing 'Charging' status for a gasoline-only vehicle).</li>
        </ul>
        <p>Note that information will only be available if the respective BMW CarData keys are actively included in the data stream (as configured in the "Activation of BMW CarData" chapter above).</p>
        <p>Example of the configuration file:</p>
        <pre><code>
        {<br/>
        "WBAJF11YYYYYYYYYY": {<br/>
        &#9;"Mileage": "vehicle.vehicle.travelledDistance",<br/>
        &#9;"Doors": ["vehicle.cabin.door.row1.driver.isOpen", "vehicle.cabin.door.row1.passenger.isOpen", "vehicle.cabin.door.row2.driver.isOpen", "vehicle.cabin.door.row2.passenger.isOpen", "vehicle.body.trunk.door.isOpen"],<br/>
        &#9;"Windows": ["vehicle.cabin.window.row1.driver.status", "vehicle.cabin.window.row1.passenger.status", "vehicle.cabin.window.row2.driver.status", "vehicle.cabin.window.row2.passenger.status", "vehicle.cabin.sunroof.overallStatus"],<br/>
        &#9;"Locked": "vehicle.cabin.door.status",<br/>
        &#9;"Location": ["vehicle.cabin.infotainment.navigation.currentLocation.latitude", "vehicle.cabin.infotainment.navigation.currentLocation.longitude"],<br/>
        &#9;"Driving": "vehicle.isMoving",<br/>
        &#9;"RemainingRangeTotal": "vehicle.drivetrain.totalRemainingRange"<br/>
        &#9;},<br/>
        "WBA21EFXXXXXXXXXX": {<br/>
        &#9;"Mileage": "vehicle.vehicle.travelledDistance",<br/>
        &#9;"Doors": ["vehicle.cabin.door.row1.driver.isOpen", "vehicle.cabin.door.row1.passenger.isOpen", "vehicle.cabin.door.row2.driver.isOpen", "vehicle.cabin.door.row2.passenger.isOpen", "vehicle.body.trunk.door.isOpen"],,<br/>
        &#9;"Windows": ["vehicle.cabin.window.row1.driver.status", "vehicle.cabin.window.row1.passenger.status", "vehicle.cabin.window.row2.driver.status", "vehicle.cabin.window.row2.passenger.status", "vehicle.cabin.sunroof.overallStatus"],<br/>
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
        <param field="Mode5" label="Min. Update Interval (Minutes)" width="120px" required="true" default="30">
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
from typing import Any, Dict, List, Type, Union, Tuple
from datetime import datetime, timedelta
import paho.mqtt.client as mqtt

import DomoticzEx as Domoticz
from domoticzEx_tools import (
    DomoticzConstants, dump_config_to_log, update_device, get_unit,
    get_config_item_db, set_config_item_db, get_distance,
    get_device_n_value, smart_convert_string, timeout_device
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

class Authenticate(IntEnum):
    """State machine during authentication"""
    INIT = auto()
    OAUTH2 = auto()
    USER_INTERACTION = auto()
    DONE = auto()
    ERROR = auto()
    REFRESH_TOKEN = auto()

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
    GET_TELEMATICDATA_URI = '/customers/vehicles/{vin}/telematicData'

class AuthenticationData:
    """Store Authentication data (shared state)"""
    state_machine: int = Authenticate.INIT
    client_id: str = None
    vin: str = None
    code_verifier: str = None
    device_code: str = None
    expires_in: int = None
    interval: int = None

class APIData:
    """Store API data (shared state)"""
    container_id: Dict[str, Any] = None

# Default image for devices
_IMAGE = 'Bmw'

# Streaming key filename
_STREAMING_KEY_FILE = 'Bmw_keys_streaming.json'

# Constants for workaround isMoving
VELOCITY_THRESHOLD_MPS = 2
STOP_TIME_THRESHOLD_SEC = 360  

class CarMovementHandler:
    """Detects if the car is currently moving based on location and time stamps."""
    def __init__(self) -> None:
        # State variables to store the last known coordinates and time
        self.last_coord: Union[List[float], None] = None
        self.last_timestamp: datetime = datetime.now()
        
        # State variables for the "Time-in-Stop" filter
        self.stop_start_time: Union[datetime, None] = None
        self.is_currently_moving: bool = False # True/False state for final output
        self.velocity: float = 0.0

    def process_new_data(self, location: List[float], current_timestamp_sec: datetime) -> str:
        """
        Main function to process a new set of coordinates.
        Determines movement status using a velocity and stop-time threshold.
        """
        
        # Calculate Delta Distance and Delta Time
        delta_t: float = (current_timestamp_sec - self.last_timestamp).total_seconds()
        
        # Skip if no new coordinates
        if len(location) != 2:
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
        Domoticz.Debug(f'Calculate distance with last location {self.last_coord} and current location {location}')
        delta_d: float = get_distance(self.last_coord, location, unit='m')

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
                time_in_stop: float = (current_timestamp_sec - self.stop_start_time).total_seconds()
                if time_in_stop >= STOP_TIME_THRESHOLD_SEC:
                    # Car has been stationary long enough to be considered NOT MOVING/PARKED
                    self.is_currently_moving = False
                    return "STOPPED (Final Destination/Parked)"
                else:
                    # Still within the temporary stop window (Red light/Traffic Jam)
                    # For the user, this should still be considered "Moving" or "In Transit"
                    self.is_currently_moving = True
                    return "MOVING (Traffic Jam/Long Red Light)"

class PollingHandler:
    """Manages the daily API polling quota and calculates the next polling interval."""
    DAILY_QUOTA = 50
    # Reserve 5 calls for the last few hours of the day or if MQTT fails
    RESERVED_CALLS = 5 
    
    def __init__(self, parent_plugin: Any) -> None:
        """Initializes the Polling Manager and loads its persistent state."""
        self.parent = parent_plugin
        self.calls_made_today: int = 0
        self.last_reset_day: Union[datetime, None] = None
        self.last_mqtt_update: Union[datetime, None] = None
        # next_api_call_time is the target time for the next call
        self.next_api_call_time: datetime = datetime.now()
        
        self._load_state()

    def _load_state(self) -> None:
        """Loads persistent state for polling from the Domoticz database."""
        state = get_config_item_db(key='polling_handler', default={})
        
        self.calls_made_today = state.get('calls_made_today', 0)
        last_reset_day_str = state.get('last_reset_day')
        
        if last_reset_day_str:
            self.last_reset_day = datetime.fromisoformat(last_reset_day_str)
        else:
            # Initialize to today's midnight if no state is found
            self.last_reset_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    def _save_state(self) -> None:
        """Internal method to save persistent state for polling to the Domoticz database."""
        state = {
            'calls_made_today': self.calls_made_today,
            'last_reset_day': self.last_reset_day.isoformat() if self.last_reset_day else None,
        }
        set_config_item_db(key='polling_handler', value=state)

    def save_state(self) -> None:
        """Public method to save persistent state for polling to the Domoticz database. Called on plugin stop."""
        self._save_state()

    def _reset_quota(self) -> None:
        """Resets the daily quota if a new day has started (at midnight)."""
        now: datetime = datetime.now()
        current_day: datetime = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        if self.last_reset_day is None or current_day > self.last_reset_day:
            Domoticz.Debug(f'API Polling Quota reset for new day. Calls made yesterday: {self.calls_made_today}.')
            self.calls_made_today = 0
            self.last_reset_day = current_day
        
    def register_api_call(self) -> None:
        """Registers a successful API call, updates state, and schedules the next call."""
        self._reset_quota()
        self.calls_made_today += 1
        Domoticz.Debug(f'API call registered. Total calls today: {self.calls_made_today}/{self.DAILY_QUOTA}.')
        
        # Schedule the next call immediately after registering a successful one
        # Use force_seconds=True to get the raw interval for calculation
        interval_sec = self.get_next_interval(force_seconds=True) 
        self.next_api_call_time = datetime.now() + timedelta(seconds=interval_sec)

    def register_mqtt_update(self) -> None:
        """Registers an MQTT update, potentially pushing back the next scheduled API call time."""
        self.last_mqtt_update = datetime.now()
        self.parent.runAgainAPI = int(Parameters.get('Mode5', 60)) * 60 // Domoticz.Heartbeat()
        Domoticz.Debug('MQTT update received. Next API poll in {self.parent.runAgainAPI} heartbeats.')

    def get_next_interval(self, force_seconds: bool = False) -> int:
        """
        Calculates the optimal time (in seconds or Heartbeat ticks) for the next API call.
        The algorithm spreads the remaining quota calls evenly over the remaining day.
        """
        self._reset_quota()

        now: datetime = datetime.now()
        
        # 1. Check if the next call is scheduled for the future
        if not force_seconds and now < self.next_api_call_time:
            time_left: timedelta = self.next_api_call_time - now
            interval_sec: int = max(1, int(time_left.total_seconds()))
            Domoticz.Debug(f'Next API call is scheduled in the future. Remaining interval: {interval_sec}s.')
            return interval_sec // Domoticz.Heartbeat()

        # 2. Quota Check and Spreading Calculation
        calls_available: int = self.DAILY_QUOTA - self.calls_made_today
        calls_to_spread: int = max(0, calls_available - self.RESERVED_CALLS)
        
        # Time remaining until midnight
        midnight: datetime = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        time_until_midnight_sec: int = max(1, int((midnight - now).total_seconds()))

        if calls_to_spread <= 0:
            # Quota exhausted or only reserve remains.
            # Use reserve calls only if no MQTT update in the last 6 hours
            reserve_time_threshold_sec = 6 * 3600
            
            if self.calls_made_today < self.DAILY_QUOTA and \
               (self.last_mqtt_update is None or \
               (now - self.last_mqtt_update).total_seconds() > reserve_time_threshold_sec):
                
                Domoticz.Debug(f'Quota near limit. Using reserve call (1 hour interval).')
                interval_sec = 3600 # 1 hour
            else:
                Domoticz.Debug('Quota fully exhausted or recent MQTT update received. Waiting until midnight.')
                interval_sec = time_until_midnight_sec # Wait until midnight
        else:
            # Spread the available calls evenly
            interval_sec: int = time_until_midnight_sec // calls_to_spread
            
            # Enforce a minimum interval using Parameter['Mode5'] (Max. Update Interval)
            min_interval_sec: int = int(Parameters.get('Mode5', 60)) * 60 
            interval_sec = max(min_interval_sec, interval_sec)
            
            Domoticz.Debug(f'Spreading {calls_to_spread} calls over {time_until_midnight_sec}s. Next interval: {interval_sec}s.')

        if force_seconds:
            return interval_sec
        
        # Calculate next call time and return interval in heartbeat ticks
        self.next_api_call_time = now + timedelta(seconds=interval_sec)
        
        # Return in Heartbeat ticks (minimum 1)
        return max(1, interval_sec // Domoticz.Heartbeat())

class MqttClientHandler:
    """
    Handles all MQTT logic for connecting to the BMW CarData streaming service.
    Requires access to parent's state variables for tokens, data storage, and control flow.
    """
    def __init__(
        self, 
        parent_plugin: Any
        ) -> None:
        """Initializes the MQTT handler with a reference to the main plugin."""
        self.parent = parent_plugin
        self.mqtt_client: Union[mqtt.Client, None] = None

    def connect_mqtt(
        self
        ) -> bool:
        """
        Connect to MQTT broker for streaming using the Paho client.
        Requires authenticated tokens from the parent plugin.
        """

        if AuthenticationData.state_machine != Authenticate.DONE:
            Domoticz.Debug('MQTT cannot start because of none-complete authentication.')
            return False

        if self.mqtt_client and self.mqtt_client.is_connected():
            return True

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

        try:
            # Access credentials via the OAuth2Handler (parent.auth_handler)
            id_token: str = self.parent.tokens['id_token']['token']
            username: str = self.parent.auth_handler.mqtt_username
            self.mqtt_client.username_pw_set(username, id_token)
        except (ValueError, KeyError) as e:
            Domoticz.Error(f"Error getting MQTT credentials: {e}")
            return False

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

    def disconnect_mqtt(
        self, 
        reconnect: bool=False
        ) -> None:
        """Disconnects from the MQTT broker and optionally attempts an immediate reconnect."""

        if self.mqtt_client:
            self.mqtt_client.user_data_set({'reconnect': reconnect})
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        elif reconnect:
            self.connect_mqtt()

    def onMqttConnect(
        self, 
        client: mqtt.Client, 
        userdata: Dict[str, Any], 
        flags: Dict[str, int], 
        rc: int, 
        properties: mqtt.Properties
        ) -> None:
        """MQTT connection callback. Subscribes to necessary topics upon successful connection."""

        if rc == 0:
            Domoticz.Debug('Connected to MQTT broker successfully')

            topic: str = f'{self.parent.auth_handler.mqtt_username}/{AuthenticationData.vin}'
            self.mqtt_client.subscribe(topic, qos=1)
            Domoticz.Debug(f'Request to subscribe to topic: {topic} with QoS 1')

            wildcard_topic: str = f'{self.parent.auth_handler.mqtt_username}/+'
            self.mqtt_client.subscribe(wildcard_topic, qos=1)
            Domoticz.Debug(f'Request to subscribe to wildcard topic: {wildcard_topic} with QoS 1')

            expires_at: datetime = datetime.fromisoformat(self.parent.tokens['id_token']['expires_at'])
            time_until_expiry: timedelta = expires_at - datetime.now()
            Domoticz.Debug(f'ID token expires in: {time_until_expiry}')

        else:
            Domoticz.Error(f'Failed to connect to BMW CarData MQTT broker: {rc}.')

    def onMqttMessage(self, 
        client: mqtt.Client,
        userdata: Dict[str, Any], 
        msg: mqtt.MQTTMessage
        ) -> None:
        """MQTT message callback. Parses and stores received data into the plugin's state."""

        try:
            data: Dict[str, Any] = json.loads(msg.payload.decode())
            Domoticz.Debug(f'Received message on {msg.topic}: {data}')
            
            # Populate BMW Data structure with received information
            vin: str = data.get('vin')
            if vin:
                if vin not in self.parent.bmwData:
                    self.parent.bmwData[vin] = {}
                for key, value in data.get('data', {}).items(): 
                    self.parent.bmwData[vin][key] = value 

            # Register MQTT update with PollingManager
            self.parent.polling_handler.register_mqtt_update()

        except json.JSONDecodeError:
            Domoticz.Debug(f'Received non-JSON message: {msg.payload.decode()}')
        except Exception as e:
            Domoticz.Debug(f'Error processing message: {e}')

    def onMqttSubscribe(
        self, 
        client: mqtt.Client, 
        userdata: Dict[str, Any], 
        mid: int, 
        reason_codes: List[int], 
        properties: mqtt.Properties
        ) -> None:
        """MQTT subscription callback. Logs the broker's acknowledgment of subscription request."""

        for i, rc in enumerate(reason_codes):
            Domoticz.Debug(f'Subscription confirmed - Topic {i}: {rc}')

    def onMqttDisconnect(
        self, 
        client: mqtt.Client, 
        userdata: Dict[str, Any], 
        flags: Dict[str, int], 
        rc: int, 
        properties: mqtt.Properties
        ) -> None:
        """MQTT disconnect callback. Handles clean disconnects and token expiration detection."""

        reconnect: bool = False if not userdata else userdata.get('reconnect', False)
        
        # Check for clean disconnect (rc=0) based on V1 Paho documentation
        if rc == 0:
            Domoticz.Debug(f"Disconnect after disconnect() successful; reconnect again: {reconnect}")
            if reconnect:
                self.connect_mqtt()
        else:
            Domoticz.Debug(f'Unexpected disconnection from MQTT broker: {rc}')

            if rc in (4, 5): # Paho v1 codes for "Bad Username/Password" or "Not Authorized"
                Domoticz.Debug('Possible token expiration - checking token validity...')
                if self.parent.auth_handler._is_token_expired('id_token'):
                    Domoticz.Debug('ID token has expired, will refresh on next connection attempt')
            else:
                Domoticz.Debug('Attempting to reconnect through heartbeat loop...')

class OAuth2Handler:
    """Handles the entire OAuth2 Device Code Flow, token management, and authentication state."""

    def __init__(self, parent_plugin: Any) -> None:
        """Initializes the OAuth2 handler with a reference to the main plugin."""
        self.parent = parent_plugin
    
    def on_connect(self) -> None:
        """Callback from BasePlugin when the OAuth2 connection is established."""
        Domoticz.Debug('OAuth2 connection successful.')
        self.authenticate()

    def handle_message(self, data: Dict[str, Any]) -> None:
        """Routes message responses from the OAuth2 connection based on the current state machine."""
        
        status: Union[str, None] = data.get('Status', None)
        try:
            response_data: Dict[str, Any] = json.loads(data['Data'])
        except (KeyError, json.JSONDecodeError):
            Domoticz.Error(f"OAuth2 response data invalid: {data}")
            AuthenticationData.state_machine = Authenticate.ERROR
            return

        if AuthenticationData.state_machine == Authenticate.OAUTH2:
            if status == '200':
                AuthenticationData.state_machine = Authenticate.USER_INTERACTION
                self.authenticate(response_data)
            else:
                Domoticz.Error(f"Error during authentication ({status}): {response_data}.")
                AuthenticationData.state_machine = Authenticate.ERROR
                
        elif AuthenticationData.state_machine == Authenticate.USER_INTERACTION:
            if status == '200':
                self.parent.oauth2.Disconnect()
                self._store_tokens(response_data)
                AuthenticationData.state_machine = Authenticate.DONE
                Domoticz.Status('BMW CarData Authentication successful! Starting BMW CarData MQTT connection...')
                self.parent.mqtt_handler.disconnect_mqtt(reconnect=True)
                self.parent.runAgainOAuth = DomoticzConstants.MINUTE
            elif status in ['400', '401', '403']:
                error: str = response_data.get('error', '')
                if error == 'authorization_pending':
                    self.parent.runAgainOAuth = AuthenticationData.interval // Domoticz.Heartbeat()
                elif error == 'slow_down':
                    AuthenticationData.interval += Domoticz.Heartbeat()
                    Domoticz.Debug('Request to slow down polling!')
                    self.parent.runAgainOAuth = AuthenticationData.interval // Domoticz.Heartbeat()
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
                Domoticz.Error(f'BMW CarData Authentication Unexpected response ({status}): {response_data}')
                AuthenticationData.state_machine = Authenticate.ERROR

        elif AuthenticationData.state_machine == Authenticate.REFRESH_TOKEN:
            if status == '200':
                self.parent.oauth2.Disconnect()
                AuthenticationData.state_machine = Authenticate.DONE
                self._store_tokens(response_data)
                Domoticz.Debug('Tokens refreshed successfully; reconnect MQTT...')
                self.parent.mqtt_handler.disconnect_mqtt(reconnect=True)
                self.parent.runAgainOAuth = DomoticzConstants.MINUTE
            else:
                Domoticz.Debug(f"Error refreshing tokens ({status}): {response_data}. Restarting authentication...")
                AuthenticationData.state_machine = Authenticate.OAUTH2
                self.authenticate()

    def authenticate(self, data: Dict[str, Any]=None) -> bool:
        """Perform OAuth2 Device Code Flow authentication based on current state."""

        if not self.parent.oauth2.Connected():
            Domoticz.Debug('Not connected to OAUTH2 authentication server: reconnecting...')
            self.parent.oauth2.Connect()
            return False

        if AuthenticationData.state_machine == Authenticate.INIT:
            # Check for existing refresh tokens on startup
            if self._load_tokens():
                Domoticz.Debug('Tokens found, checking validity and refreshing if needed.')
                self._ensure_valid_id_token(force_update=True)
                return True
            else:
                Domoticz.Debug('Token refresh failed, proceeding with new authentication...')
                AuthenticationData.state_machine = Authenticate.OAUTH2

        if AuthenticationData.state_machine == Authenticate.OAUTH2:
            Domoticz.Debug('Starting OAuth2 Device Code Flow authentication...')

            # Step 1: Generate PKCE pair
            AuthenticationData.code_verifier, code_challenge = self._generate_pkce_pair()

            # Step 2: Request device and user codes
            device_code_data: Dict[str, str] = {
                'client_id': AuthenticationData.client_id,
                'response_type': 'device_code',
                'scope': 'authenticate_user openid cardata:streaming:read cardata:api:read',
                'code_challenge': code_challenge,
                'code_challenge_method': 'S256'
            }
            headers: Dict[str, str] = {
                'Host': CarDataURLs.BMW_HOST,
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            self.parent.oauth2.Send( {'Verb':'POST', 'URL':CarDataURLs.DEVICE_CODE_URI, 'Data':urllib.parse.urlencode(device_code_data), 'Headers':headers} )

        if AuthenticationData.state_machine == Authenticate.USER_INTERACTION:
            if data:
                # Display user instructions (first time in this state)
                user_code: str = data['user_code']
                AuthenticationData.device_code = data['device_code']
                verification_uri_complete: str = data['verification_uri_complete']
                AuthenticationData.expires_in = data['expires_in']
                AuthenticationData.interval = data.get('interval', Domoticz.Heartbeat())

                text: str = '\n' + '=' * 60
                text += '\nBMW CarData Authentication Required'
                text += '\n' + '=' * 60
                text += f'\nUser Code: {user_code}'
                text += f'\nPlease visit: {verification_uri_complete}'
                text += f"\nComplete the authentication in your browser before {(datetime.now() + timedelta(seconds=AuthenticationData.expires_in)).strftime('%H:%M:%S')}..."
                text += '\n' + '=' * 60

                Domoticz.Status(text)
                self.parent.runAgainOAuth = AuthenticationData.interval // Domoticz.Heartbeat()
            else:
                # Poll for tokens
                Domoticz.Debug('Polling for the user action to get the tokens.')
                token_data: Dict[str, str] = {
                    'client_id': AuthenticationData.client_id,
                    'device_code': AuthenticationData.device_code,
                    'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
                    'code_verifier': AuthenticationData.code_verifier
                }
                headers: Dict[str, str] = {
                    'Host': CarDataURLs.BMW_HOST,
                    'Accept': 'application/json',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
                self.parent.oauth2.Send( {'Verb':'POST', 'URL':CarDataURLs.TOKEN_URI, 'Data':urllib.parse.urlencode(token_data), 'Headers':headers} )
                self.parent.runAgainOAuth = AuthenticationData.interval // Domoticz.Heartbeat()

        if AuthenticationData.state_machine == Authenticate.REFRESH_TOKEN:
            # Request token refresh
            refresh_data: Dict[str, str] = {
                'grant_type': 'refresh_token',
                'refresh_token': self.parent.tokens['refresh_token']['token'],
                'client_id': AuthenticationData.client_id
            }
            headers: Dict[str, str] = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Host': CarDataURLs.BMW_HOST
            }
            self.parent.oauth2.Send( {'Verb':'POST', 'URL':CarDataURLs.TOKEN_URI, 'Data':urllib.parse.urlencode(refresh_data), 'Headers':headers} )

        return True

    def _generate_pkce_pair(self) -> Tuple[str, str]:
        """Generate PKCE code verifier and code challenge."""

        code_verifier: str = (
            base64.urlsafe_b64encode(secrets.token_bytes(32))
            .decode("utf-8")
            .rstrip("=")
        )

        code_challenge: str = (
            base64.urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode("utf-8")).digest()
            )
            .decode("utf-8")
            .rstrip("=")
        )

        return code_verifier, code_challenge

    def _store_tokens(self, tokens: Dict[str, Any]) -> None:
        """Store tokens and calculate their expiration timestamps."""

        now: datetime = datetime.now()

        # Store access token (in memory only, not persisted)
        if 'access_token' in tokens:
            expires_in: int = tokens.get('expires_in', 3600)
            self.parent.tokens['access_token'] = {
                'token': tokens['access_token'],
                'expires_at': (now + timedelta(seconds=expires_in)).isoformat(),
                'type': tokens.get('token_type', 'Bearer')
            }

        # Store refresh token (persisted for future use)
        if 'refresh_token' in tokens:
            self.parent.tokens['refresh_token'] = {
                'token': tokens['refresh_token'],
                'expires_at': (now + timedelta(seconds=1209600)).isoformat()  # 2 weeks
            }

        # Store ID token (in memory only, not persisted)
        if 'id_token' in tokens:
            expires_in: int = tokens.get('expires_in', 3600)
            self.parent.tokens['id_token'] = {
                'token': tokens['id_token'],
                'expires_at': (now + timedelta(seconds=expires_in)).isoformat()
            }

        # Store other data
        if 'gcid' in tokens:
            self.parent.tokens['gcid'] = tokens['gcid']
        if "scope" in tokens:
            self.parent.tokens['scope'] = tokens['scope']

        self._save_tokens_selective()

    def _refresh_id_token(self) -> bool:
        """Initiates the token refresh operation using the refresh token."""

        if 'refresh_token' not in self.parent.tokens:
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
        """Checks ID token validity and triggers refresh or re-authentication if necessary."""

        if self._is_token_expired('id_token') or force_update:
            if self._refresh_id_token():
                Domoticz.Debug(f'Forced update ({force_update}) and/or ID token expired, refreshing using refresh token...')
            else:
                Domoticz.Debug('ID token expired and cannot refresh, need new authentication')
                AuthenticationData.state_machine = Authenticate.OAUTH2
                self.authenticate()
        else:
            Domoticz.Debug(f"ID token still valid until {self.parent.tokens['id_token']['expires_at']}...")

    def _save_tokens_selective(self) -> None:
        """Saves only persistent tokens (refresh token, gcid) to the Domoticz database."""

        persistent_tokens: Dict[str, Any] = {}
        persistent_tokens['client_id'] = AuthenticationData.client_id
        if 'refresh_token' in self.parent.tokens:
            persistent_tokens['refresh_token'] = self.parent.tokens['refresh_token']
        if 'gcid' in self.parent.tokens:
            persistent_tokens['gcid'] = self.parent.tokens['gcid']
        if 'scope' in self.parent.tokens:
            persistent_tokens['scope'] = self.parent.tokens['scope']

        Domoticz.Debug(f'Tokens stored to database: {persistent_tokens}')
        set_config_item_db(key='tokens', value=persistent_tokens)

    def _load_tokens(self) -> bool:
        """Loads persistent tokens from the Domoticz database."""

        self.parent.tokens = get_config_item_db(key='tokens', default={})
        if self.parent.tokens:
            Domoticz.Debug(f'Tokens loaded from database: {self.parent.tokens}')
            if self.parent.tokens.get('client_id', '') != AuthenticationData.client_id:
                Domoticz.Debug(f'Client_id changed: tokens from database do not correspond and will be erased!')
                return False
            return True

        Domoticz.Debug(f'Tokens not loaded from database.')
        return False

    def _is_token_expired(self, token_key: str) -> bool:
        """Checks if a given token is expired or within the 5-minute pre-expiration window."""

        if token_key not in self.parent.tokens or 'expires_at' not in self.parent.tokens[token_key]:
            return True

        expires_at: datetime = datetime.fromisoformat(self.parent.tokens[token_key]['expires_at'])
        return datetime.now() + timedelta(minutes=5) >= expires_at

    @property
    def mqtt_username(self) -> str:
        """Get MQTT username (GCID) from stored tokens. Raises ValueError if not available."""

        if 'gcid' in self.parent.tokens:
            return self.parent.tokens['gcid']
        raise ValueError('GCID not available - authentication required')

class CarDataAPIHandler:
    """Handles communication for the BMW CarData API (container creation and telematic polling)."""

    def __init__(self, parent_plugin: Any) -> None:
        """Initializes the API handler with a reference to the main plugin."""
        self.parent = parent_plugin

    def handle_message(self, data: Dict[str, Any]) -> None:
        """Routes message responses from the API connection based on the response status."""
        
        status: Union[str, None] = data.get('Status', None)
        try:
            response_data: Dict[str, Any] = json.loads(data['Data'])
        except (KeyError, json.JSONDecodeError):
            Domoticz.Debug(f"API response data invalid: {data}")
            return

        if not APIData.container_id and status == '201':
            # Successful container creation
            container: Dict[str, Any] = response_data
            container.pop('technicalDescriptors')
            set_config_item_db(key='container', value=container)
            APIData.container_id = container
            Domoticz.Debug(f'Container created: {container}')
            # Register this as a successful API call
            self.parent.polling_handler.register_api_call() 
        elif APIData.container_id and status == '200':
            # Correct answer on TelematicData
            Domoticz.Debug(f"Telematic data received: {response_data}")
            telematicData: Dict[str, Any] = response_data.get('telematicData', {})
            
            # Merge received data into the plugin's main data structure
            vin: str = AuthenticationData.vin
            if vin in self.parent.bmwData:
                self.parent.bmwData[vin].update(telematicData)
            else:
                self.parent.bmwData[vin] = telematicData
            
            self.parent.api.Disconnect()
            # Register this as a successful API call
            self.parent.polling_handler.register_api_call() 
        else:
            Domoticz.Debug(f"API Error ({status}): {response_data}.")

    def poll_telematic_data(self) -> None:
        """Checks for the container ID and either creates it or requests telematic data."""
        
        # Load container ID if not in memory
        if not APIData.container_id:
            APIData.container_id = get_config_item_db(key='container', default={})
            if not APIData.container_id:
                # If still no ID, create the container
                self._create_container()
                return

        # Request telematic data if container ID is available
        self._get_telematic_data()

    def _get_all_streaming_keys(self) -> List[str]:
        """Reads all unique streaming keys from the configuration file for the API container."""
        
        container_keys: List[str] = []

        # Iterate over the values in the dictionary (parent.streamingKeys)
        for value in self.parent.streamingKeys.values():
            if isinstance(value, str):
                container_keys.append(value)
            elif isinstance(value, list):
                container_keys.extend(value)
        Domoticz.Debug(f'Elements for the container are: {container_keys}')
        return container_keys

    def _create_container(self) -> None:
        """Sends an HTTP POST request to the BMW API to create a CarData container."""

        container_data: Dict[str, Any] = {
            'name': AuthenticationData.vin,
            'purpose': 'Telemetry',
            'technicalDescriptors': self._get_all_streaming_keys()
        }

        headers: Dict[str, str] = {
            'Host': CarDataURLs.API_HOST,
            'Authorization': f"Bearer {self.parent.tokens['access_token']['token']}",
            'x-version': CarDataURLs.API_VERSION,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        Domoticz.Debug('Create container with all known streaming keys.')
        self.parent.api.Send( {'Verb':'POST', 'URL':CarDataURLs.CREATE_CONTAINER_URI, 'Data':json.dumps(container_data), 'Headers':headers} )

    def _get_telematic_data(self) -> None:
        """Sends an HTTP GET request to retrieve the latest telematic data for the vehicle."""

        headers: Dict[str, str] = {
            'Host': CarDataURLs.API_HOST,
            'Authorization': f"Bearer {self.parent.tokens['access_token']['token']}",
            'x-version': CarDataURLs.API_VERSION,
            'Accept': 'application/json'
        }

        Domoticz.Debug('Send request for telematic data.')
        self.parent.api.Send( {'Verb':'GET', 'URL':f"{CarDataURLs.GET_TELEMATICDATA_URI.format(vin=AuthenticationData.vin)}?containerId={APIData.container_id['containerId']}", 'Headers':headers} )


################################################################################
# Start Plugin
################################################################################
class BasePlugin:
    """
    Main plugin class and orchestrator for the BMW Domoticz integration.
    Handles Domoticz callbacks and delegates tasks to handler classes.
    """

    def __init__(self):
        """Initializes plugin state and handler classes."""
        self.runAgainOAuth: int = 0
        self.runAgainAPI: int = 0
        self.runAgainDeviceUpdate: int = 0
        self.Stop: bool = False
        self.tokens: Dict[str, Any] = {}
        self.bmwData: Dict[str, Any] = {}
        self.streamingKeys: Dict[str, Any] = {}
        
        # Initialize Handlers
        self.mov_handler: CarMovementHandler = CarMovementHandler()
        self.mqtt_handler: MqttClientHandler = MqttClientHandler(self) 
        self.auth_handler: OAuth2Handler = OAuth2Handler(self)
        self.api_handler: CarDataAPIHandler = CarDataAPIHandler(self)
        self.polling_handler: PollingHandler = PollingHandler(self)

        # Connection objects (initialized in onStart)
        self.oauth2: Union[Domoticz.Connection, None] = None
        self.api: Union[Domoticz.Connection, None] = None

    def onStart(self) -> None:
        """Called by Domoticz when the plugin starts. Initializes configuration and connections."""
        Domoticz.Debug('onStart called')

        # Debugging
        if Parameters["Mode6"] != '0':
            try:
                Domoticz.Debugging(int(Parameters["Mode6"]))
                dump_config_to_log(Parameters, Devices)
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

        # Initial Authentication attempt
        AuthenticationData.state_machine = Authenticate.INIT
        self.auth_handler.authenticate()

        # Read key streaming file
        self._read_streaming_keys_file()

        # Update interval of devices
        self.runAgainDeviceUpdate = DomoticzConstants.MINUTE

        # Timeout devices
        timeout_device(Devices)

    def onStop(self) -> None:
        """Called by Domoticz when the plugin stops. Cleans up connections."""
        Domoticz.Debug('onStop called')
        self.Stop = True

        # Save the PollingHandler state only upon plugin stop
        self.polling_handler.save_state() 

        # Disconnections
        if self.oauth2 and self.oauth2.Connected():
            self.oauth2.Disconnect()
        self.mqtt_handler.disconnect_mqtt(reconnect=False)

    def onConnect(self, Connection: Domoticz.Connection, Status: int, Description: str) -> None:
        """Called when a connection attempt completes. Routes success to the relevant handler."""
        if self.Stop: return
        Domoticz.Debug(f'onConnect called with status {Status} - {Connection.Name}')

        if Connection == self.oauth2:
            if Status == 0:
                self.auth_handler.on_connect()
            else:
                Domoticz.Debug(f'OAuth2 connection error ({Description}). Trying again in 1 minute...')
                AuthenticationData.state_machine = Authenticate.ERROR
                self.runAgainOAuth = DomoticzConstants.MINUTE
        
        # API Connection is established, but no action needed until onMessage receives the response.

    def onCommand(self, DeviceID: int, Unit: int, Command: str, Level: int, Color: str) -> None:
        """Called when a Domoticz device associated with the plugin is controlled."""
        if self.Stop: return
        Domoticz.Debug('onCommand called for DeviceID/Unit: {}/{} - Parameter: {} - Level: {}'.format(DeviceID, Unit, Command, Level))

    def onDisconnect(self, Connection: Domoticz.Connection) -> None:
        """Called when a connection is disconnected."""
        Domoticz.Debug(f'onDisconnect called {Connection.Name}')

    def onMessage(self, Connection: Domoticz.Connection, Data: Dict[str, Any]) -> None:
        """Called when data is received on a Domoticz connection. Routes messages to the correct handler."""
        if self.Stop: return

        if Connection == self.oauth2:
            self.auth_handler.handle_message(Data)
        elif Connection == self.api:
            self.api_handler.handle_message(Data)

    def onHeartbeat(self) -> None:
        """Called periodically by Domoticz. Handles scheduling and state machine progression."""
        if self.Stop: return

        self.runAgainOAuth -= 1
        if self.runAgainOAuth <= 0:
            if AuthenticationData.state_machine == Authenticate.USER_INTERACTION:
                # Polling waiting for user interaction
                self.auth_handler.authenticate()
            elif AuthenticationData.state_machine == Authenticate.ERROR:
                # Restart authentication in cause of error
                AuthenticationData.state_machine = Authenticate.INIT
                self.auth_handler.authenticate()
            elif AuthenticationData.state_machine == Authenticate.DONE:
                # Monitor and refresh tokens as needed.
                self.auth_handler._ensure_valid_id_token()
                # Ensure MQTT connection
                self.mqtt_handler.connect_mqtt()
                self.runAgainOAuth = DomoticzConstants.MINUTE
            else:
                self.runAgainOAuth = DomoticzConstants.MINUTE

        self.runAgainDeviceUpdate -= 1
        if self.runAgainDeviceUpdate <= 0:
            Domoticz.Debug(f'Status BMW(s): {self.bmwData}')
            # Read bmw keys streaming file if change was detected
            try:
                if self.streamingKeysDatim != os.path.getmtime(f"{Parameters['HomeFolder']}{_STREAMING_KEY_FILE}"):
                    Domoticz.Debug(f'Reading updated file {_STREAMING_KEY_FILE}.')
                    self._read_streaming_keys_file()
            except:
                pass
            self.workaround_driving() # Workaround to deduct if vehicle is driving or not
            self.update_devices()
            self.runAgainDeviceUpdate = DomoticzConstants.MINUTE

        if AuthenticationData.state_machine == Authenticate.DONE:
            self.runAgainAPI -= 1
            if self.runAgainAPI <= 0:
                if not (self.api.Connected() or self.api.Connecting() ):
                    self.api.Connect()
                else:
                    self.api_handler.poll_telematic_data()
                    # Only reset the API timer if a request was successfully sent/attempted
                    self.runAgainAPI = self.polling_handler.get_next_interval()

    def workaround_driving(self) -> None:
        """Applies a calculated driving status if the 'vehicle.isMoving' key is missing from the stream."""
        if ( streaming_keys := self.streamingKeys.get('Location', None) ):
            current_location = self._get_status_from_streaming_keys('Location', streaming_keys, float, delete_key=False)
            # Workaround if key "vehicle.isMoving" is not supplied... calculate if vehicle is moving
            current_time: datetime = datetime.now()
            result: str = self.mov_handler.process_new_data(list(current_location), current_time)
            Domoticz.Debug(f'Workaround for vehicle isMoving... isMoving={self.mov_handler.is_currently_moving}; last_location={self.mov_handler.last_coord}; current_location={current_location}; result={result}')
            # Use workaround if no vehicle.isMoving data coming true
            update_device(False, Devices, Parameters['Name'], UnitIdentifiers.DRIVING,
                          1 if self.mov_handler.is_currently_moving else 0, 
                          100 if self.mov_handler.is_currently_moving else 0)

    def update_devices(self) -> None:
        """Updates all virtual devices in Domoticz based on the latest BMW data."""
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
                unit: str = self.bmwData[AuthenticationData.vin].get(streaming_keys, {}).get('unit', 'km')
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
            if status := self._get_status_from_streaming_keys('Doors', streaming_keys, ['OPEN', 'CLOSED', True, False]):
                update_device( False, Devices, Parameters['Name'], UnitIdentifiers.DOORS,
                               0 if all(x in ['CLOSED', False] for x in status) else 1, 0 )

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
            if (status := self._get_status_from_streaming_keys('Location', streaming_keys, float)) and len(status)==2:
                # Parse home location from settings
                home_loc: List[str] = Settings['Location'].split(';')
                home_point: Tuple[float, float] = (float(home_loc[0]), float(home_loc[1]))
                # Calculate distance from home using the tracker
                if distance := get_distance(list(status), home_point, 'm'):
                    update_device(False, Devices, Parameters['Name'], UnitIdentifiers.HOME,
                                  1 if distance <= 100 else 0, 100-distance if distance <= 100 else 0)

        # Driving status
        if not ( streaming_keys := self.streamingKeys.get('Driving', None) ):
            # Driving status is calculated via the workaround if not explicitly streamed
            if not self.mov_handler.is_currently_moving:
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
                unit: str = self.bmwData[AuthenticationData.vin].get(streaming_keys, {}).get('unit', 'km')
                update_device( False, Devices, Parameters['Name'], UnitIdentifiers.REMAIN_RANGE_TOTAL,
                               status[0], status[0], 
                               Options={'Custom': f"0;{unit}"}
                             )

        # Update Remaining electric range
        if not ( streaming_keys := self.streamingKeys.get('RemainingRangeElec', None) ):
            update_device( False, Devices, Parameters['Name'], UnitIdentifiers.REMAIN_RANGE_ELEC, Used=0 )
        else:
            if status := self._get_status_from_streaming_keys('RemainingRangeElec', [streaming_keys], int):
                unit: str = self.bmwData[AuthenticationData.vin].get(streaming_keys, {}).get('unit', 'km')
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
                charging: bool = status[0]=='CHARGINGACTIVE'
                battery: int = get_device_n_value(Devices, Parameters['Name'], UnitIdentifiers.BAT_LEVEL) or 0
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

        # Clean up unused/legacy devices
        if get_unit(Devices, Parameters['Name'], UnitIdentifiers.REMOTE_SERVICES):
            update_device( False, Devices, Parameters['Name'], UnitIdentifiers.REMOTE_SERVICES, Used=0 )
        if get_unit(Devices, Parameters['Name'], UnitIdentifiers.AC_LIMITS):
            update_device( False, Devices, Parameters['Name'], UnitIdentifiers.AC_LIMITS, Used=0 )
        if get_unit(Devices, Parameters['Name'], UnitIdentifiers.CHARGING_MODE):
            update_device( False, Devices, Parameters['Name'], UnitIdentifiers.CHARGING_MODE, Used=0 )


    def _get_status_from_streaming_keys(
        self, 
        key_name: str, 
        streaming_keys: Union[str, List[str]], 
        expected_value: Union[List[Union[str, bool]], Type], 
        delete_key: bool = True
        ) -> Union[List[Any], None]:
        """
        Parses all requested streaming keys for the current VIN, validates their type/value, 
        and optionally removes them from the main data structure.
        """
        
        # Ensure streaming_keys is a list for uniform processing
        if isinstance(streaming_keys, str):
            streaming_keys = [streaming_keys]
            
        # Parse to get explicit list of streaming keys
        keys: List[str] = [ 
            key for streaming_key in streaming_keys
            for key in self.bmwData.get(AuthenticationData.vin, {}).keys() 
                if '*' in streaming_key and key.startswith(streaming_key.split('*', 1)[0]) and key.endswith(streaming_key.split('*', 1)[1])
                or '*' not in streaming_key and key == streaming_key
        ]
        
        # Get status back of all streaming keys
        status: List[Any] = [ 
            smart_convert_string(self.bmwData[AuthenticationData.vin][key].get('value', None)) 
            for key in keys 
            if self.bmwData[AuthenticationData.vin][key].get('value', None) is not None
        ]
        
        # Erase streaming keys from BMWStatus
        if delete_key:
            for key in keys:
                self.bmwData[AuthenticationData.vin].pop(key, None)
        
        # Check if all return values match expected types/values
        check: bool
        if isinstance(expected_value, List):
            check = all(x in expected_value for x in status)
        else:
            check = all(isinstance(x, expected_value) for x in status)
            
        if not check:
            Domoticz.Error(f'{AuthenticationData.vin}: Streaming keys are defined in {_STREAMING_KEY_FILE} for {key_name} that do not return {expected_value}. Key {streaming_keys} gives {status}.')
            return None
            
        #Domoticz.Debug(f'{key_name}: {status}')
        return status

    def _read_streaming_keys_file(self) -> bool:
        """Reads and loads the Bmw_keys_streaming.json configuration file."""
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
        """Creates all required Domoticz devices if they don't exist yet."""
        # Create Mileage device
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.MILEAGE):
            Domoticz.Unit(
                DeviceID=Parameters['Name'], Unit=UnitIdentifiers.MILEAGE, Name=f"{Parameters['Name']} - Mileage",
                TypeName='Custom', Options={'Custom': '0;km'}, Image=Images[_IMAGE].ID, Used=1
            ).Create()

        # Create Mileage Counter device
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.MILEAGE_COUNTER):
            Domoticz.Unit(
                DeviceID=Parameters['Name'], Unit=UnitIdentifiers.MILEAGE_COUNTER, Name=f"{Parameters['Name']} - Mileage (Day)",
                Type=113, Subtype=0, Switchtype=3, Options={'ValueUnits': 'km'}, Image=Images[_IMAGE].ID, Used=1
            ).Create()

        # NOT USED: Create device for remote services
        if get_unit(Devices, Parameters['Name'], UnitIdentifiers.REMOTE_SERVICES):
            update_device( False, Devices, Parameters['Name'], UnitIdentifiers.REMOTE_SERVICES, Used=0 )

        # Create doors status device
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.DOORS):
            Domoticz.Unit(
                DeviceID=Parameters['Name'], Unit=UnitIdentifiers.DOORS, Name=f"{Parameters['Name']} - Doors",
                Type=244, Subtype=73, Switchtype=11, Image=Images[_IMAGE].ID, Used=1
            ).Create()

        # Create windows status device
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.WINDOWS):
            Domoticz.Unit(
                DeviceID=Parameters['Name'], Unit=UnitIdentifiers.WINDOWS, Name=f"{Parameters['Name']} - Windows",
                Type=244, Subtype=73, Switchtype=11, Image=Images[_IMAGE].ID, Used=1
            ).Create()

        # Create remaining total (fuel+elec) range device
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.REMAIN_RANGE_TOTAL):
            Domoticz.Unit(
                DeviceID=Parameters['Name'], Unit=UnitIdentifiers.REMAIN_RANGE_TOTAL, Name=f"{Parameters['Name']} - Remaining range (total)",
                TypeName='Custom', Options={'Custom': '0;km'}, Image=Images[_IMAGE].ID, Used=1
            ).Create()

        # Create remaining electric range device
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.REMAIN_RANGE_ELEC):
            Domoticz.Unit(
                DeviceID=Parameters['Name'], Unit=UnitIdentifiers.REMAIN_RANGE_ELEC, Name=f"{Parameters['Name']} - Remaining range (elec)",
                TypeName='Custom', Options={'Custom': '0;km'}, Image=Images[_IMAGE].ID, Used=1
            ).Create()

        # Create charging status device
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.CHARGING):
            Domoticz.Unit(
                DeviceID=Parameters['Name'], Unit=UnitIdentifiers.CHARGING, Name=f"{Parameters['Name']} - Charging",
                Type=244, Subtype=73, Switchtype=0, Image=Images[_IMAGE].ID, Used=1
            ).Create()

        # Create charging remaining time device
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.CHARGING_REMAINING):
            Domoticz.Unit(
                DeviceID=Parameters['Name'], Unit=UnitIdentifiers.CHARGING_REMAINING, Name=f"{Parameters['Name']} - Charging time",
                TypeName='Custom', Options={'Custom': '0;min'}, Image=Images[_IMAGE].ID, Used=1
            ).Create()

        # Create battery level device
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.BAT_LEVEL):
            Domoticz.Unit(
                DeviceID=Parameters['Name'], Unit=UnitIdentifiers.BAT_LEVEL, Name=f"{Parameters['Name']} - Battery Level",
                TypeName='Custom', Options={'Custom': '0;%'}, Image=Images[_IMAGE].ID, Used=1
            ).Create()

        # Create car status device (locked/unlocked)
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.CAR):
            Domoticz.Unit(
                DeviceID=Parameters['Name'], Unit=UnitIdentifiers.CAR, Name=f"{Parameters['Name']} - Car",
                Type=244, Subtype=73, Switchtype=11, Image=Images[_IMAGE].ID, Used=1
            ).Create()

        # Create driving status device
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.DRIVING):
            Domoticz.Unit(
                DeviceID=Parameters['Name'], Unit=UnitIdentifiers.DRIVING, Name=f"{Parameters['Name']} - Driving",
                Type=244, Subtype=73, Switchtype=0, Image=Images[_IMAGE].ID, Used=1
            ).Create()

        # Create home status device
        if not get_unit(Devices, Parameters['Name'], UnitIdentifiers.HOME):
            Domoticz.Unit(
                DeviceID=Parameters['Name'], Unit=UnitIdentifiers.HOME, Name=f"{Parameters['Name']} - Home",
                Type=244, Subtype=73, Switchtype=0, Image=Images[_IMAGE].ID, Used=1
            ).Create()

        # NOT USED: Create device for AC limitation limits
        if get_unit(Devices, Parameters['Name'], UnitIdentifiers.AC_LIMITS):
            update_device( False, Devices, Parameters['Name'], UnitIdentifiers.AC_LIMITS, Used=0 )

        # NOT USED:  Create device for Charging Mode
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
