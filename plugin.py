#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BMW Python Plugin for Domoticz

This plugin integrates BMW vehicles with Domoticz home automation system.
It uses the bimmerconnected library to fetch data from BMW's API and creates
corresponding devices in Domoticz.

Author: Filip Demaertelaere
Version: 4.0.1
License: MIT
"""
"""
<plugin key="Bmw" name="BMW ConnectedDrive" author="Filip Demaertelaere" version="4.0.1">
    <description>
        <h2>Introduction</h2>
        <p>The BMW ConnectedDrive plugin for Domoticz offers a robust and seamless integration with your BMW vehicle, transforming your home automation system into a comprehensive command center for your car. This plugin leverages the capabilities of the open-source <a href="https://github.com/bimmerconnected/bimmer_connected">bimmer_connected Python API</a>, providing real-time data monitoring and remote control functionalities. By bridging the gap between your vehicle's advanced telematics and your smart home environment, it empowers users with unprecedented control and insight.</p>
        <p>Upon successful configuration, the plugin creates a suite of virtual devices within Domoticz, representing key aspects of your BMW's status, including mileage, door and window lock states, fuel and electric range, charging status, and even the vehicle's location and movement. Beyond passive monitoring, it enables active management through remote services such as locking/unlocking doors, flashing lights, sounding the horn, activating air conditioning, and initiating charging, all directly from the Domoticz interface.</p>
        <p>To ensure optimal performance and security, this plugin requires a valid MyBMW account with corresponding credentials (username and password). Furthermore, the BMW API often necessitates a CAPTCHA token for initial authentication or re-authentication. Users can generate this token by visiting the official `bimmer_connected` documentation at <a href="https://bimmer-connected.readthedocs.io/en/stable/captcha.html">https://bimmer-connected.readthedocs.io/en/stable/captcha.html</a>. It is crucial to note that these CAPTCHA tokens possess a limited validity period, necessitating regeneration and re-entry in the plugin's configuration should authentication failures occur or upon plugin restarts.</p>
        <p>The plugin is designed with flexibility in mind, offering configurable polling intervals to balance data freshness with API usage, along with comprehensive debug options to assist with troubleshooting and optimization. This makes the BMW ConnectedDrive plugin an invaluable tool for any BMW owner looking to enhance their smart home ecosystem.</p>
        <br/>
        <h2>Configuration Parameters</h2>
        <ul>
            <li><b>MyBMW Account Username</b>: Your username for the MyBMW ConnectedDrive account.</li>
            <li><b>MyBMW Account Password</b>: Your password for the MyBMW ConnectedDrive account. This field is masked for security.</li>
            <li><b>Vehicle Identification Number (VIN)</b>: The full 17-character Vehicle Identification Number (VIN) of your BMW car. This identifies the specific vehicle to monitor.</li>
            <li><b>Region</b>: Select the geographical region associated with your MyBMW account. This is crucial for connecting to the correct BMW API endpoint.</li>
            <li><b>CAPTCHA Token</b>: Enter the CAPTCHA token generated from the bimmer_connected documentation. A new token may be required upon plugin restart or authentication issues.</li>
            <li><b>Update Interval (Minutes)</b>: Defines how often the plugin will fetch updated status information from your BMW vehicle, in minutes. A lower value provides more frequent updates but may increase API requests.</li>
            <li><b>Debug Level</b>: Set the level of detail for logging messages. Higher debug levels provide more diagnostic information which can be helpful for troubleshooting.</li>
        </ul>
        <br/>
        <h2>Advanced Polling Configuration (Bmw.json)</h2>
        <p>For more granular control over polling behavior based on your vehicle's proximity to home, an optional configuration file named `Bmw.json` can be placed in the plugin's home folder. This JSON file allows you to define custom distances and associated fast polling delays. If this file is not present or is invalid, the plugin will revert to default values.</p>
        <p>The `Bmw.json` file supports the following parameters (all distances are in meters and delays in minutes):</p>
        <ul>
            <li><b>EnteringHomeDistance (m)</b>: This parameter defines the radius around your configured home location within which the car is considered "home". When the car is within this distance, the plugin will use the default polling interval set in the Domoticz plugin parameters. The default value is 1000 meters.</li>
            <li><b>EnteringHomeDistance_FastPollingDistance (m)</b>: This parameter defines a larger radius around your home. When the car is within this distance but outside the `EnteringHomeDistance`, the plugin will switch to a "fast polling" mode. The default value is 2000 meters.</li>
            <li><b>EnteringHomeDistance_FastPollingDelay (min)</b>: This parameter specifies the polling interval (in minutes) to be used when the car is within the `EnteringHomeDistance_FastPollingDistance` but not yet within the `EnteringHomeDistance`. This allows for more frequent updates as your vehicle approaches home. The default value is 2 minutes.</li>
        </ul>
        <h3>Example Bmw.json content:</h3>
        <pre><code>
{
    "EnteringHomeDistance (m)": 500,
    "EnteringHomeDistance_FastPollingDistance (m)": 1500,
    "EnteringHomeDistance_FastPollingDelay (min)": 1
}
        </code></pre>
        <p>This advanced configuration enables dynamic polling, ensuring that you receive more frequent updates when your BMW is nearing your home, providing a more responsive and intelligent integration with your Domoticz system.</p>
    </description>
    <params>
        <param field="Username" label="MyBMW Account Username" width="200px" required="true" default=""/>
        <param field="Password" label="MyBMW Account Password" width="200px" required="true" default="" password="true"/>
        <param field="Mode1" label="Vehicle Identification Number (VIN)" width="200px" required="true" default=""/>
        <param field="Mode2" label="Region" width="120px" required="true">
            <options>
                <option label="Rest Of World" value="rest_of_world"/>
                <option label="North America" value="north_america"/>
                <option label="China" value="china" default="Rest Of World"/>
            </options>
        </param>
        <param field="Mode3" label="CAPTCHA Token" width="200px" required="true" default=""/>
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
</plugin>
"""
# Standard library imports
import sys
import os
import datetime
import threading
import queue
import json
import time
import pytz
import asyncio
import functools
from pathlib import Path
from collections import deque
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple, Any, NamedTuple, TypedDict, Union, Callable, cast
from enum import IntEnum, Enum, auto

# Add the parent directory to the path for Domoticz imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# Domoticz imports
import DomoticzEx as Domoticz
from domoticzEx_tools import (
    DomoticzConstants, dump_config_to_log, update_device, timeout_device,
    get_device_n_value, get_unit, set_config_item_db, get_config_item_db, erase_config_item_db,
    get_distance
)

# BMW API related imports
from bimmer_connected.account import MyBMWAccount
from bimmer_connected.api.regions import get_region_from_name
from bimmer_connected.vehicle.remote_services import ExecutionState
from bimmer_connected.models import MyBMWCaptchaMissingError
from bimmer_connected.const import ATTR_STATE

class UnitIdentifiers(IntEnum):
    """Enum defining unit identifiers for various BMW data points in Domoticz"""
    MILEAGE = auto()
    DOORS = auto()
    WINDOWS = auto()
    REMAIN_RANGE_FUEL = auto()
    REMAIN_RANGE_ELEC = auto()
    CHARGING = auto()
    CHARGING_REMAINING = auto()
    BAT_LEVEL = auto()
    REMOTE_SERVICES = auto()
    CAR = auto()
    MILEAGE_COUNTER = auto()
    DRIVING = auto()
    HOME = auto()

class BmwRegion(str, Enum):
    """Enum containing BMW API region identifiers"""
    REST_OF_WORLD = 'rest_of_world'
    CHINA = 'china'
    NORTH_AMERICA = 'north_america'

class BmwRemoteService(str, Enum):
    """Enum containing BMW remote service command strings"""
    LIGHT_FLASH = 'light-flash'
    VEHICLE_FINDER = 'vehicle-finder'
    DOOR_LOCK = 'door-lock'
    DOOR_UNLOCK = 'door-unlock'
    HORN = 'horn-blow'
    AIR_CONDITIONING = 'climate-now'
    CHARGE_START = 'charge_start'
    CHARGE_STOP = 'charge_stop'

# Default image for devices
_IMAGE = 'Bmw'

class BmwConfigData(TypedDict, total=False):
    """TypedDict defining the structure of BMW configuration file"""
    EnteringHomeDistance: int  # in meters
    EnteringHomeDistance_FastPollingDistance: int  # in meters
    EnteringHomeDistance_FastPollingDelay: int  # in minutes

class OAuthData(TypedDict, total=False):
    """TypedDict for OAuth token data"""
    refresh_token: str
    gcid: str
    access_token: str
    session_id: str
    session_id_timestamp: float

class LocationPoint(NamedTuple):
    """NamedTuple for a geographic location point"""
    latitude: float
    longitude: float
    timestamp: datetime.datetime

@dataclass
class LocationTracker:
    """
    Class for tracking and analyzing the vehicle's location data.
    Maintains a history of locations and provides methods for location-based calculations.
    """
    history_size: int = 2
    history: deque = field(default_factory=lambda: deque(maxlen=2))
    error_reported: bool = False

    def __post_init__(self) -> None:
        """Initialize the deque with the specified max length"""
        self.history = deque(maxlen=self.history_size)

    def update(self, lat: Optional[float], lng: Optional[float], timestamp: Optional[datetime.datetime] = None) -> bool:
        """
        Update the location tracker with a new location.

        Args:
            lat: Latitude
            lng: Longitude
            timestamp: Time of the location data (defaults to now)

        Returns:
            bool: True if location was updated, False if invalid location
        """
        if timestamp is None:
            timestamp = datetime.datetime.now()

        if lat is not None and lng is not None:
            self.history.append(((lat, lng), timestamp))
            self.error_reported = False
            return True
        return False

    def current_location(self) -> Tuple[Optional[float], Optional[float]]:
        """
        Get the current location.

        Returns:
            tuple: (latitude, longitude) or (None, None) if no location
        """
        return self.history[-1][0] if self.history else (None, None)

    def previous_location(self) -> Tuple[Optional[float], Optional[float]]:
        """
        Get the previous location.

        Returns:
            tuple: (latitude, longitude) or (None, None) if no previous location
        """
        return self.history[-2][0] if len(self.history) > 1 else (None, None)

    def is_moving(self) -> bool:
        """
        Check if the vehicle is moving (location changed between last two points).

        Returns:
            bool: True if moving, False otherwise
        """
        return self.current_location() != self.previous_location() if len(self.history) > 1 else False

    def calculate_speed(self) -> float:
        """
        Calculate speed between the last two points in km/h.

        Returns:
            float: Speed in km/h, or 0 if can't be calculated
        """
        if len(self.history) < 2:
            return 0.0

        loc1, time1 = self.history[-2]
        loc2, time2 = self.history[-1]

        distance = get_distance(loc1, loc2)  # in km
        time_diff = (time2 - time1).total_seconds() / 3600  # in hours

        if time_diff > 0:
            return distance / time_diff
        return 0.0

    def distance_from_point(self, point: Tuple[float, float]) -> Optional[float]:
        """
        Calculate distance from current location to a point.

        Args:
            point: (latitude, longitude) tuple

        Returns:
            float: Distance in km, or None if no current location
        """
        if not self.history:
            return None
        return get_distance(self.current_location(), point)

    def get_location_history(self) -> List[Tuple[Tuple[float, float], datetime.datetime]]:
        """
        Get the full location history.

        Returns:
            list: List of ((latitude, longitude), timestamp) tuples
        """
        return list(self.history)

@dataclass
class PollingConfig:
    """
    Class to manage polling settings based on distance from home.
    Handles loading settings from configuration file and determining appropriate polling intervals.
    """
    home_distance: int = 1000  # meters
    fast_polling_distance: int = 2000  # meters
    fast_polling_delay: int = 2  # minutes
    default_polling_delay: int = 5  # minutes

    def load_from_config(self, config_file_path: Path, default_polling_delay: int) -> bool:
        """
        Load polling settings from configuration file.

        Args:
            config_file_path: Path to configuration file
            default_polling_delay: Default polling delay from Domoticz settings

        Returns:
            bool: True if config loaded successfully, False otherwise
        """
        self.default_polling_delay = default_polling_delay

        try:
            with config_file_path.open('r') as json_file:
                config: Dict[str, Any] = json.load(json_file)

            self.home_distance = config.get('EnteringHomeDistance (m)', self.home_distance)
            self.fast_polling_distance = config.get('EnteringHomeDistance_FastPollingDistance (m)', self.fast_polling_distance)
            self.fast_polling_delay = config.get('EnteringHomeDistance_FastPollingDelay (min)', self.fast_polling_delay)
            Domoticz.Debug(f"Loaded polling settings: Home distance={self.home_distance}m, Fast polling distance={self.fast_polling_distance}m, Fast polling delay={self.fast_polling_delay}min")
            return True

        except Exception as err:
            Domoticz.Debug(f"Configuration file not found or invalid, using default values: {err}")
            return False

    def get_polling_interval(self, distance_km: float) -> int:
        """
        Determine the appropriate polling interval based on distance from home.

        Args:
            distance_km: Distance from home in kilometers

        Returns:
            int: Polling interval in minutes
        """
        distance_m = distance_km * 1000

        if distance_m < self.home_distance:
            # Already home - use default polling
            return self.default_polling_delay
        elif distance_m < self.fast_polling_distance:
            # Approaching home - use fast polling
            return self.fast_polling_delay
        else:
            # Far from home - use default polling
            return self.default_polling_delay

    def is_home(self, distance_km: float) -> bool:
        """
        Determine if the vehicle is considered 'home' based on distance.

        Args:
            distance_km: Distance from home in kilometers

        Returns:
            bool: True if vehicle is considered at home, False otherwise
        """
        return distance_km * 1000 < self.home_distance

def handle_bmw_errors(func: Callable) -> Callable:
    """Decorator to handle common BMW API errors."""
    @functools.wraps(func)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        try:
            return func(self, *args, **kwargs)
        except MyBMWCaptchaMissingError:
            Domoticz.Debug(f"New login with CAPTCHA required with user {Parameters['Username']}.")
            self.captcha_required = True
            erase_config_item_db(key='oauth')  # Remove authentication tokens to force use of captcha
            self.my_bmw = None
            timeout_device(Devices)
            return False
        except Exception as err:
            Domoticz.Error(f"Error in {func.__name__}: {err}")
            if hasattr(self, 'error_level'):
                self.error_level += 1
            return None
    return wrapper


class BmwPlugin:
    """
    Main plugin class for the BMW Domoticz integration.
    Handles communication with the BMW API and manages device updates.
    """
    def __init__(self) -> None:
        """Initialize the plugin with default values."""
        self.run_again = DomoticzConstants.MINUTE
        self.stop = False
        self.error_level = 0

        self.oauth: Dict[str, Any] = {}
        self.captcha_required = False
        self.my_bmw = None
        self.my_vehicle = None

        self.last_car_opened_time = datetime.datetime.now()
        self.car_opened_status_given = False
        self.distance_from_home = 0.0

        self.location_tracker = LocationTracker()
        self.polling_config = PollingConfig()

        self.tasks_queue: queue.Queue = queue.Queue()
        self.tasks_thread: Optional[threading.Thread] = None

    def onStart(self) -> None:
        """
        Handle the plugin startup.
        Initialize devices and settings, start the worker thread.
        """
        Domoticz.Debug('onStart called')

        # Setup debugging if enabled
        if Parameters["Mode6"] != '0':
            try:
                Domoticz.Debugging(int(Parameters["Mode6"]))
                dump_config_to_log(Parameters, Devices)
            except:
                pass

        default_polling_delay = int(Parameters['Mode5'])
        config_path = Path(Parameters['HomeFolder']) / "Bmw.json"
        self.polling_config.load_from_config(config_path, default_polling_delay)

        # Create the BMW image if not present
        if _IMAGE not in Images:
            Domoticz.Image('Bmw.zip').Create()

        self.create_devices()

        # Initialize devices with timeout status
        timeout_device(Devices)

        # Start worker thread to handle tasks
        self.tasks_thread = threading.Thread(name='QueueThread', target=self.handle_tasks)
        self.tasks_thread.start()

        # Queue initial login task
        self.tasks_queue.put({'Action': 'Login'})

    def onStop(self) -> None:
        """
        Handle the plugin stopping.
        Clean up resources and wait for threads to exit.
        """
        Domoticz.Debug(f'onStop called - Threads still active: {threading.active_count()} (should be 1 = {threading.current_thread().name})')
        self.stop = True

        # Signal queue thread to exit
        self.tasks_queue.put(None)
        if self.tasks_thread:
            self.tasks_thread.join()

        # Wait until queue thread has exited
        Domoticz.Debug(f'Threads still active: {threading.active_count()} (should be 1)')
        endTime = time.time() + 70
        while (threading.active_count() > 1) and (time.time() < endTime):
            for thread in threading.enumerate():
                if thread.name != threading.current_thread().name:
                    Domoticz.Debug(f'Thread {thread.name} is still running, waiting otherwise Domoticz will abort on plugin exit.')
            time.sleep(1.0)

        Domoticz.Debug(f'Plugin stopped - Threads still active: {threading.active_count()} (should be 1)')

    def onConnect(self, Connection: Any, Status: int, Description: str) -> None:
        """Handle successful connection events."""
        Domoticz.Debug(f'onConnect called ({Connection.Name}) with status={Status}')

    def onMessage(self, Connection: Any, Data: Dict[str, Any]) -> None:
        """Handle incoming message events."""
        Domoticz.Debug(f'onMessage called ({Connection.Name})')

    def onCommand(self, DeviceID: str, Unit: int, Command: str, Level: int, Color: str) -> None:
        """
        Handle commands sent to devices.
        This allows control of remote services and functions.

        Args:
            DeviceID: The device identifier
            Unit: The unit within the device
            Command: The command to execute
            Level: The level parameter for the command
            Color: The color parameter for the command
        """
        if self.stop:
            return

        Domoticz.Debug(f'onCommand called for DeviceID/Unit: {DeviceID}/{Unit} - Parameter: {Command} - Level: {Level}')

        # Handle remote services commands
        if Unit == UnitIdentifiers.REMOTE_SERVICES and Command == 'Set Level':
            level_to_service = {
                10: BmwRemoteService.LIGHT_FLASH,
                20: BmwRemoteService.HORN,
                30: BmwRemoteService.AIR_CONDITIONING,
                40: BmwRemoteService.DOOR_LOCK,
                50: BmwRemoteService.DOOR_UNLOCK,
                60: BmwRemoteService.CHARGE_START,
                60: BmwRemoteService.CHARGE_STOP
            }

            if Level in level_to_service:
                remote_service = level_to_service[Level]
                self.tasks_queue.put({'Action': remote_service.value})

                # Additional status update for lock/unlock commands
                if remote_service in (BmwRemoteService.DOOR_LOCK, BmwRemoteService.DOOR_UNLOCK):
                    self.tasks_queue.put({'Action': 'StatusUpdate'})

    def onDisconnect(self, Connection: Any) -> None:
        """Handle disconnection events."""
        Domoticz.Debug(f'onDisconnect called ({Connection.Name})')

    def onHeartbeat(self) -> None:
        """
        Handle the periodic heartbeat event.
        Updates the vehicle status at configured intervals.
        """
        if self.stop:
            return

        self.run_again -= 1

        # Check if car is locked and warn if it has been unlocked for too long
        if (get_device_n_value(Devices, Parameters['Name'], UnitIdentifiers.CAR) and
            not self.car_opened_status_given and
            datetime.datetime.now() - self.last_car_opened_time > datetime.timedelta(minutes=60)):
            Domoticz.Status(f'ATTENTION: Car is not closed since {self.last_car_opened_time}!!')
            self.car_opened_status_given = True

        # Time to update status?
        if self.run_again <= 0 and not self.captcha_required:
            # Schedule login if needed, followed by status update
            if self.my_bmw is None:
                self.tasks_queue.put({'Action': 'Login'})
            self.tasks_queue.put({'Action': 'StatusUpdate'})

            self.run_again = DomoticzConstants.MINUTE * self.polling_config.get_polling_interval(self.distance_from_home)

            # If too many errors, slow down update rate to avoid API limits
            if self.error_level >= 3:
                timeout_device(Devices)
                self.run_again = self.error_level * DomoticzConstants.MINUTE * int(Parameters['Mode5'])
                Domoticz.Error('Too many errors received: devices are timed out! No updates will be done anymore '
                              'and retry rate will be slowed down until next successful communication...')

    async def safe_close_loop(self) -> None:
        """Safely close asyncio loop and cancel all running tasks"""
        try:
            # Get all tasks in the current loop
            tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

            # Cancel all tasks
            for task in tasks:
                task.cancel()

            # Wait for all tasks to complete with cancellation
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            Domoticz.Debug(f"Error closing asyncio loop: {e}")

    @handle_bmw_errors
    def handle_tasks(self) -> None:
        """
        Worker thread that handles tasks from the queue.
        Processes login, status updates, and remote commands.
        """
        try:
            Domoticz.Debug('Entering tasks handler')
            while True:
                # Get the next task from the queue
                task = self.tasks_queue.get(block=True)

                # None is the signal to exit the thread
                if task is None:
                    Domoticz.Debug('Exiting task handler')
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            asyncio.run(self.safe_close_loop())
                    except Exception as e:
                        Domoticz.Debug(f"Error in loop closure: {e}")
                    self.my_bmw = None
                    self.my_vehicle = None
                    self.tasks_queue.task_done()
                    break

                Domoticz.Debug(f'Handling task: {task["Action"]}.')

                # Process the task based on the action
                if task['Action'] == 'Login':
                    # Try to login to MyBMW
                    if not self.login_my_bmw():
                        # Supply (valid) Captcha and try again
                        self.login_my_bmw()

                elif task['Action'] == 'StatusUpdate':
                    if self.my_bmw:
                        # Connect to the BMW API using the credentials
                        try:
                            # WORKAROUND FOR https://github.com/bimmerconnected/bimmer_connected/issues/430
                            asyncio.run(self.my_bmw.get_vehicles())
                        except RuntimeError:
                            self.my_bmw = None
                            if not self.error_level:
                                Domoticz.Log('BMW Status Update: error occurred in getting info from BMW - activating workaround.')
                            self.error_level += 1

                        # Handle other errors
                        except Exception as err:
                            Domoticz.Log(f'BMW Status Update: error occurred in getting info from BMW ({err}).')
                            self.error_level += 1

                        # If successful, update vehicle information
                        else:
                            # Get the data for the specified VIN
                            self.my_vehicle = self.my_bmw.get_vehicle(Parameters['Mode1'])
                            if self.my_vehicle:
                                Domoticz.Debug(f'Car {self.my_vehicle.name} found after update!')
                                self.update_vehicle_status()
                                self.error_level = 0
                            else:
                                Domoticz.Log(f"BMW Status Update: BMW with VIN {Parameters['Mode1']} not found for user {Parameters['Username']}.")
                                self.error_level += 1

                        # Always update tokens regardless of success/failure
                        finally:
                            # Update refresh_token in storage
                            Domoticz.Debug(f'Authentication tokens (oauth): {self.oauth}')
                            self.store_oauth_to_db(self.oauth.get('session_id_timestamp'))

                # Handle remote service commands
                elif (action := task['Action']) in [service.value for service in BmwRemoteService]:
                    if self.my_vehicle:
                        try:
                            remote_functions = {
                                BmwRemoteService.LIGHT_FLASH.value: self.my_vehicle.remote_services.trigger_remote_light_flash,
                                BmwRemoteService.HORN.value: self.my_vehicle.remote_services.trigger_remote_horn,
                                BmwRemoteService.AIR_CONDITIONING.value: self.my_vehicle.remote_services.trigger_remote_air_conditioning,
                                BmwRemoteService.DOOR_LOCK.value: self.my_vehicle.remote_services.trigger_remote_door_lock,
                                BmwRemoteService.DOOR_UNLOCK.value: self.my_vehicle.remote_services.trigger_remote_door_unlock,
                                BmwRemoteService.CHARGE_START.value: self.my_vehicle.remote_services.trigger_charge_start,
                                BmwRemoteService.CHARGE_STOP.value: self.my_vehicle.remote_services.trigger_charge_stop
                            }

                            if action in remote_functions:
                                status = asyncio.run(remote_functions[action]())

                                # Check if the command was executed successfully
                                if status.state != ExecutionState.EXECUTED:
                                    Domoticz.Error(f'Error executing remote service {action} for {Parameters["Mode1"]} (not executed).')
                        except Exception as err:
                            Domoticz.Error(f'Error executing remote service {action} for {Parameters["Mode1"]} ({err}).')
                            Domoticz.Debug(f'Remote service error: {err}')
                    else:
                        Domoticz.Error(f'BMW with VIN {Parameters["Mode1"]} not found for user {Parameters["Username"]}.')

                    # Reset the remote services selector
                    update_device(True, Devices, Parameters['Name'], UnitIdentifiers.REMOTE_SERVICES, 2, 0)

                # Handle unknown actions
                else:
                    Domoticz.Error(f'Invalid task/action name: {task["Action"]}.')

                Domoticz.Debug(f'Finished handling task: {task["Action"]}.')
                self.tasks_queue.task_done()

        except Exception as err:
            Domoticz.Error(f'General error TaskHandler: {err}')
            # For debugging
            import traceback
            log_path = Path(Parameters['HomeFolder']) / "Bmw_traceback.txt"
            with log_path.open("a") as myfile:
                myfile.write(f'-General Error-{datetime.datetime.now()}------------------\n')
                myfile.write(f'{traceback.format_exc()}')
                myfile.write('---------------------------------\n')
            self.tasks_queue.task_done()

    def store_oauth_to_db(self, session_id_timestamp: Optional[float]) -> None:
        """
        Store OAuth authentication tokens in the database.

        Args:
            session_id_timestamp: Timestamp for the session ID
        """
        if not self.my_bmw:
            return

        oauth: OAuthData = {
            'refresh_token': self.my_bmw.config.authentication.refresh_token,
            'gcid': self.my_bmw.config.authentication.gcid,
            'access_token': self.my_bmw.config.authentication.access_token,
            'session_id': self.my_bmw.config.authentication.session_id,
            'session_id_timestamp': session_id_timestamp or time.time()
        }
        Domoticz.Debug(f'oauth data stored to database: {oauth}')
        set_config_item_db(key='oauth', value=oauth)

    def load_oauth_from_db(self) -> Dict[str, Any]:
        """
        Load OAuth tokens from database and apply them to the BMW account.

        Returns:
            dict: OAuth token information
        """
        if not self.my_bmw:
            return {}

        oauth = get_config_item_db(key='oauth', default=None)
        if not oauth:
            Domoticz.Debug(f'oauth data not loaded from database: {oauth}')
            return {}

        session_id_timestamp = oauth.pop('session_id_timestamp', None)

        # Pop session_id every 14 days so it gets recreated
        if (time.time() - (session_id_timestamp or 0)) > 14 * 24 * 60 * 60:
            oauth.pop('session_id', None)
            session_id_timestamp = None

        Domoticz.Debug(f'oauth data loaded from database: {oauth}')
        self.my_bmw.set_refresh_token(**oauth)

        return oauth | {'session_id_timestamp': session_id_timestamp}

    @handle_bmw_errors
    def login_my_bmw(self) -> bool:
        """
        Log in to the MyBMW account.

        Returns:
            bool: True if login was successful, False if captcha required
        """
        # Create MyBMW account object
        if self.captcha_required:
            Domoticz.Debug(f"Try login with captcha {Parameters['Mode3']}...")
            self.my_bmw = MyBMWAccount(
                Parameters['Username'],
                Parameters['Password'],
                get_region_from_name(Parameters['Mode2']),
                hcaptcha_token=Parameters['Mode3']
            )
        else:
            Domoticz.Debug("Try login without captcha...")
            self.my_bmw = MyBMWAccount(
                Parameters['Username'],
                Parameters['Password'],
                get_region_from_name(Parameters['Mode2'])
            )

        # Load saved OAuth tokens
        self.oauth = self.load_oauth_from_db()
        Domoticz.Debug(f'myBMW object created (no connection to the BMW API yet!): {self.my_bmw}')

        # Connect to BMW API
        Domoticz.Debug('Trying to get the vehicles from myBMW (includes login).')
        if self.my_bmw:
            asyncio.run(self.my_bmw.get_vehicles())

        # Login successful - store tokens
        Domoticz.Debug(f'Authentication tokens (oauth): {self.oauth}')
        self.store_oauth_to_db(self.oauth.get('session_id_timestamp'))

        # Get vehicle data for the specified VIN
        self.captcha_required = False
        self.my_vehicle = self.my_bmw.get_vehicle(Parameters['Mode1'])

        if self.my_vehicle:
            Domoticz.Status(f"Login successful! BMW {self.my_vehicle.name} and VIN {Parameters['Mode1']} found! Updating the status...")
            self.update_vehicle_status()
            self.error_level = 0
        else:
            Domoticz.Error(f"BMW with VIN {Parameters['Mode1']} not found for user {Parameters['Username']}.")
            timeout_device(Devices)

        return True

    def update_vehicle_status(self) -> None:
        """
        Update Domoticz devices with the latest vehicle status.
        Updates doors, windows, mileage, charging status, location, etc.
        """
        if self.stop or not self.my_vehicle:
            return

        # Update status of Doors
        update_device(False, Devices, Parameters['Name'], UnitIdentifiers.DOORS,
                    0 if self.my_vehicle.doors_and_windows.all_lids_closed else 1, 0)

        # Update status of Windows
        update_device(False, Devices, Parameters['Name'], UnitIdentifiers.WINDOWS,
                    0 if self.my_vehicle.doors_and_windows.all_windows_closed else 1, 0)

        # Update door lock status
        is_locked = self.my_vehicle.doors_and_windows.door_lock_state in ['SECURED', 'LOCKED']

        if not is_locked and update_device(False, Devices, Parameters['Name'], UnitIdentifiers.CAR, 1, 0):
            Domoticz.Debug('Car is opened now!')
            self.last_car_opened_time = datetime.datetime.now()
            self.car_opened_status_given = False
        else:
            update_device(False, Devices, Parameters['Name'], UnitIdentifiers.CAR, 0, 0)

        # Update Mileage
        mileage_value, mileage_unit = self.my_vehicle.mileage
        update_device(False, Devices, Parameters['Name'], UnitIdentifiers.MILEAGE,
                     mileage_value, mileage_value)
        update_device(False, Devices, Parameters['Name'], UnitIdentifiers.MILEAGE_COUNTER,
                     0, mileage_value)

        # Update unit display if needed
        mileage_device = get_unit(Devices, Parameters['Name'], UnitIdentifiers.MILEAGE)
        if mileage_unit not in mileage_device.Options['Custom']:
            update_device(False, Devices, Parameters['Name'], UnitIdentifiers.MILEAGE,
                        Options={'Custom': f'0;{mileage_unit}'})

        mileage_counter_device = get_unit(Devices, Parameters['Name'], UnitIdentifiers.MILEAGE_COUNTER)
        if mileage_unit not in mileage_counter_device.Options['ValueUnits']:
            update_device(False, Devices, Parameters['Name'], UnitIdentifiers.MILEAGE_COUNTER,
                        Options={'ValueUnits': mileage_unit, 'ValueQuantity': mileage_unit})

        # Update Remaining electric range
        elec_range = self.my_vehicle.fuel_and_battery.remaining_range_electric
        if elec_range != (None, None):
            elec_value, elec_unit = elec_range
            update_device(False, Devices, Parameters['Name'], UnitIdentifiers.REMAIN_RANGE_ELEC,
                        elec_value, elec_value)

            # Update unit display if needed
            elec_device = get_unit(Devices, Parameters['Name'], UnitIdentifiers.REMAIN_RANGE_ELEC)
            if elec_unit not in elec_device.Options['Custom']:
                update_device(False, Devices, Parameters['Name'], UnitIdentifiers.REMAIN_RANGE_ELEC,
                            Options={'Custom': f'0;{elec_unit}'})

        # Update Remaining fuel range
        fuel_range = self.my_vehicle.fuel_and_battery.remaining_range_fuel
        if fuel_range != (None, None):
            fuel_value, fuel_unit = fuel_range
            update_device(False, Devices, Parameters['Name'], UnitIdentifiers.REMAIN_RANGE_FUEL,
                        fuel_value, fuel_value)

            # Update unit display if needed
            fuel_device = get_unit(Devices, Parameters['Name'], UnitIdentifiers.REMAIN_RANGE_FUEL)
            if fuel_unit not in fuel_device.Options['Custom']:
                update_device(False, Devices, Parameters['Name'], UnitIdentifiers.REMAIN_RANGE_FUEL,
                            Options={'Custom': f'0;{fuel_unit}'})

        # Update Electric charging status
        if (charging_status := self.my_vehicle.fuel_and_battery.charging_status) is not None:
            is_charging = charging_status == 'CHARGING'
            update_device(False, Devices, Parameters['Name'], UnitIdentifiers.CHARGING,
                        1 if is_charging else 0, 1 if is_charging else 0)

        # Update Battery Percentage
        if (battery_percent := self.my_vehicle.fuel_and_battery.remaining_battery_percent) is not None:
            update_device(False, Devices, Parameters['Name'], UnitIdentifiers.BAT_LEVEL,
                        battery_percent, battery_percent)

        # Update Charging Time (minutes)
        charging_end = self.my_vehicle.fuel_and_battery.charging_end_time
        vehicle_timestamp = self.my_vehicle.timestamp

        Domoticz.Debug(f'Remaining charging time: {charging_end}; Last info time: {vehicle_timestamp}')

        if charging_end and vehicle_timestamp:
            # Calculate remaining charging time in minutes
            charging_time_remaining = max(0, round(
                (charging_end.astimezone(pytz.utc) -
                 vehicle_timestamp.replace(tzinfo=datetime.timezone.utc)).total_seconds() / 60, 2))
            update_device(False, Devices, Parameters['Name'], UnitIdentifiers.CHARGING_REMAINING,
                        charging_time_remaining, charging_time_remaining)
        else:
            update_device(False, Devices, Parameters['Name'], UnitIdentifiers.CHARGING_REMAINING, 0, 0)

        # Update vehicle location status
        Domoticz.Debug(f'Location of vehicle: {self.my_vehicle.vehicle_location} '
                      f'(or as workaround {self.my_vehicle.data[ATTR_STATE].get("location")})')

        # Check if location data is available (NULL when car geolocation is not activated)
        if (location := self.my_vehicle.vehicle_location.location):
            # Parse home location from settings
            home_loc = Settings['Location'].split(';')
            home_point = (float(home_loc[0]), float(home_loc[1]))

            # Update location in tracker with timestamp from vehicle data if available
            self.location_tracker.update(
                location.latitude,
                location.longitude,
                self.my_vehicle.timestamp
            )

            # Calculate distance from home using the tracker
            if (distance := self.location_tracker.distance_from_point(home_point)) is not None:
                self.distance_from_home = distance
                Domoticz.Debug(f'Distance car-home: {self.distance_from_home} km')

                # Update home status based on distance using PollingConfig
                is_home = self.polling_config.is_home(self.distance_from_home)
                update_device(False, Devices, Parameters['Name'], UnitIdentifiers.HOME,
                           1 if is_home else 0, 1 if is_home else 0)

            # Update driving status based on location change
            is_moving = self.location_tracker.is_moving()
            update_device(False, Devices, Parameters['Name'], UnitIdentifiers.DRIVING,
                       1 if is_moving else 0, 1 if is_moving else 0)

            # Calculate and log speed if moving
            if is_moving and (speed := self.location_tracker.calculate_speed()) > 0:
                Domoticz.Debug(f'Estimated speed: {speed:.1f} km/h')
        else:
            # Log a warning if location can't be retrieved (only once)
            if not self.location_tracker.error_reported:
                Domoticz.Status(f'Location of car {self.my_vehicle.name} cannot be retrieved. '
                              f'Home/Driving device will not be updated!!')
                self.location_tracker.error_reported = True

    def create_devices(self) -> None:
        """Create all required devices if they don't exist yet."""
        if not Devices.get(Parameters['Name'], None):
            # Create Mileage device
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

            level_names = '|' + '|'.join(service.value for service in [
                BmwRemoteService.LIGHT_FLASH,
                BmwRemoteService.HORN,
                BmwRemoteService.AIR_CONDITIONING,
                BmwRemoteService.DOOR_LOCK,
                BmwRemoteService.DOOR_UNLOCK,
                BmwRemoteService.CHARGE_START,
                BmwRemoteService.CHARGE_STOP
            ])

            remote_services_options = {
                'LevelActions': '|'*len(BmwRemoteService),
                'LevelNames': level_names,
                'LevelOffHidden': 'false',
                'SelectorStyle': '1'
            }

            Domoticz.Unit(
                DeviceID=Parameters['Name'],
                Unit=UnitIdentifiers.REMOTE_SERVICES,
                Name=f"{Parameters['Name']} - Remote Services",
                TypeName='Selector Switch',
                Options=remote_services_options,
                Image=Images[_IMAGE].ID,
                Used=1
            ).Create()

            # Create doors status device
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

            # Create remaining fuel range device
            Domoticz.Unit(
                DeviceID=Parameters['Name'],
                Unit=UnitIdentifiers.REMAIN_RANGE_FUEL,
                Name=f"{Parameters['Name']} - Remain mileage (fuel)",
                TypeName='Custom',
                Options={'Custom': '0;km'},
                Image=Images[_IMAGE].ID,
                Used=1
            ).Create()

            # Create remaining electric range device
            Domoticz.Unit(
                DeviceID=Parameters['Name'],
                Unit=UnitIdentifiers.REMAIN_RANGE_ELEC,
                Name=f"{Parameters['Name']} - Remain mileage (elec)",
                TypeName='Custom',
                Options={'Custom': '0;km'},
                Image=Images[_IMAGE].ID,
                Used=1
            ).Create()

            # Create charging status device
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

# Global plugin instance
_plugin = BmwPlugin()

def onStart() -> None:
    """Initialize the plugin when Domoticz starts."""
    global _plugin
    _plugin.onStart()

def onStop() -> None:
    """Clean up when the plugin stops."""
    global _plugin
    _plugin.onStop()

def onConnect(Connection: Any, Status: int, Description: str) -> None:
    """Handle connection events."""
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection: Any, Data: Dict[str, Any]) -> None:
    """Handle message events."""
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(DeviceID: str, Unit: int, Command: str, Level: int, Color: str) -> None:
    """Handle command events."""
    global _plugin
    _plugin.onCommand(DeviceID, Unit, Command, Level, Color)

def onDisconnect(Connection: Any) -> None:
    """Handle disconnection events."""
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat() -> None:
    """Handle heartbeat events."""
    global _plugin
    _plugin.onHeartbeat()
