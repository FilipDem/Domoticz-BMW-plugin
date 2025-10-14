#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Domoticz Utility Functions

This module provides a collection of utility functions for Domoticz plugins.
These functions handle common tasks such as device management, configuration,
location calculations, and API communication.

Version: 2.0.0
License: MIT
"""

# Standard library imports
from datetime import datetime
from enum import IntEnum
from math import radians, sin, cos, atan2, sqrt
from typing import Any, Dict, List, Optional, Tuple, Union

# Try to import Domoticz module
try:
    import DomoticzEx as Domoticz
except ImportError:
    # For development environments without Domoticz module
    pass

class DomoticzConstants(IntEnum):
    """Constants used throughout Domoticz plugins."""
    TIMEDOUT = 1      # Timeout status value
    MINUTE = 6        # Heartbeat is every 10 seconds

# For strong typing of device collections
DeviceCollection = Dict[str, Any]
UnitCollection = Dict[int, Any]

def dump_config_to_log(parameters: Dict[str, str], devices: DeviceCollection) -> None:
    """
    Dump plugin parameters and device information to the debug log.
    
    Args:
        parameters: Dictionary of plugin parameters
        devices: Dictionary of plugin devices
    """
    # Log non-empty parameters
    for parameter, value in parameters.items():
        if value:
            Domoticz.Debug(f'Parameter {parameter}: {value}')
    
    Domoticz.Debug(f'Got {len(devices)} devices:')
    
    # Log device information
    for i, (device_name, device) in enumerate(devices.items()):
        Domoticz.Debug(f'{i} Device name:     {device_name}')
        Domoticz.Debug(f'{i} Device ID:       {device.DeviceID}')
        Domoticz.Debug(f'{i} Device got {len(device.Units)} units:')
        
        # Log unit information
        for j, unit_number in enumerate(device.Units):
            unit = device.Units[unit_number]
            Domoticz.Debug(f'{i}.{j} Unit number:    {unit_number}')
            Domoticz.Debug(f'{i}.{j} Unit name:      {unit.Name}')
            Domoticz.Debug(f'{i}.{j} Unit nValue:    {unit.nValue}')
            Domoticz.Debug(f'{i}.{j} Unit sValue:    {unit.sValue}')
            Domoticz.Debug(f'{i}.{j} Unit LastLevel: {unit.LastLevel}')


def update_device(
    always_update: bool, 
    devices: DeviceCollection, 
    device_id: str, 
    unit: int, 
    n_value: Optional[int] = None, 
    s_value: Optional[str] = None, 
    **kwargs
) -> bool:
    """
    Update a device with new values, considering various options.
    
    Args:
        always_update: Force update even if values haven't changed
        devices: Dictionary of devices
        device_id: ID of the device to update
        unit: Unit number within the device
        n_value: New numeric value (or None to keep current value)
        s_value: New string value (or None to keep current value)
        **kwargs: Additional parameters: Image, BatteryLevel, SignalLevel, Options
        
    Returns:
        bool: True if the device was updated, False otherwise
    """
    # Default update flags
    _update_standard = _update_properties = _update_options = False
    
    # Get device and unit if they exist
    if not (device := devices.get(device_id)) or not (unit_obj := device.Units.get(unit)):
        Domoticz.Debug(f'Device with DeviceID/Unit {device_id}/{unit} does not exist... No update done...')
        return False

    Domoticz.Debug(f'Update device with AlwaysUpdate={always_update}; DeviceID={device_id}; Unit={unit}; nValue={n_value}; sValue={s_value}; others={kwargs}')
        
    # Use current values if new ones not provided
    n_value = unit_obj.nValue if n_value is None else n_value
    s_value = unit_obj.sValue if s_value is None else s_value   
    
    # Check if standard values need update
    if always_update or (unit_obj.nValue != int(n_value)) or (unit_obj.sValue != str(s_value)):
        unit_obj.nValue = int(n_value)
        unit_obj.sValue = str(s_value)
        _update_standard = True
        
    # Update device properties if provided and different
    property_updates = {
        'Image': 'Image',
        'BatteryLevel': 'BatteryLevel',
        'SignalLevel': 'SignalLevel',
        'Used': 'Used'
    }
    
    for kwarg_name, property_name in property_updates.items():
        if kwarg_name in kwargs and getattr(unit_obj, property_name) != kwargs[kwarg_name]:
            setattr(unit_obj, property_name, kwargs[kwarg_name])
            _update_properties = True
        
    # Update options if provided and different
    if 'Options' in kwargs and kwargs['Options'] and unit_obj.Options != kwargs['Options']:
        unit_obj.Options = kwargs['Options']
        _update_options = True

    # Perform the update if needed
    if _update_standard or _update_properties or _update_options:
        unit_obj.Update(UpdateProperties=_update_properties, UpdateOptions=_update_options)
    else:
        unit_obj.Touch()

    # Clear timeout status if device was in timeout
    if device.TimedOut:
        device.TimedOut = 0

    return _update_standard or _update_properties or _update_options


def timeout_device(devices: DeviceCollection, device_id: Optional[str] = None, timed_out: int = DomoticzConstants.TIMEDOUT) -> None:
    """
    Set device(s) to timed-out status.
    
    Args:
        devices: Dictionary of devices
        device_id: Specific device ID to timeout, or None for all devices
        timed_out: Timeout value to set (default: TIMEDOUT constant)
    """
    if device_id is None:
        # Timeout all units and all devices
        for name, device in devices.items():
            if device.TimedOut != timed_out:
                device.TimedOut = timed_out
                Domoticz.Debug(f'Device ID {device.DeviceID} set to timeout {bool(timed_out)}.')
    elif device := devices.get(device_id):
        if device.TimedOut != timed_out:
            device.TimedOut = timed_out
            Domoticz.Debug(f'Device ID {device_id} set to timeout {bool(timed_out)}.')


def check_activity_units_and_timeout(
    devices: DeviceCollection, 
    seconds_last_update_required: int, 
    device_id: Optional[str] = None
) -> List[str]:
    """
    Check all devices of a hardware if there was recent activity and timeout if not.
    
    Args:
        devices: Dictionary of devices
        seconds_last_update_required: Maximum seconds since last update before timing out
        device_id: Specific device ID to check, or None for all devices
    
    Returns:
        List[str]: Names of timed out devices
    """
    timed_out_devices = []
    
    if device_id is None:
        # Check all devices
        for device_name, device in devices.items():
            for unit_number, unit in device.Units.items():
                if seconds_since_last_update(devices, device.DeviceID, unit_number) > seconds_last_update_required:
                    timeout_device(devices, device_id=device.DeviceID)
                    timed_out_devices.append(unit.Name)
    elif device := devices.get(device_id):
        # Check specified device
        for unit_number, unit in device.Units.items():
            if seconds_since_last_update(devices, device_id, unit_number) > seconds_last_update_required:
                timeout_device(devices, device_id=device_id)
                timed_out_devices.append(unit.Name)
                
    return timed_out_devices


def touch_device(devices: DeviceCollection, device_id: str, unit: int) -> None:
    """
    Touch a device to update its last updated timestamp.
    
    Args:
        devices: Dictionary of devices
        device_id: ID of the device to touch
        unit: Unit number within the device
    """
    if (device := devices.get(device_id)) and (unit_obj := device.Units.get(unit)):
        unit_obj.Touch()


def get_device_s_value(devices: DeviceCollection, device_id: str, unit: int) -> Optional[str]:
    """
    Get the sValue of a device.
    
    Args:
        devices: Dictionary of devices
        device_id: ID of the device
        unit: Unit number within the device
        
    Returns:
        Optional[str]: The sValue or None if device not found
    """
    if (device := devices.get(device_id)) and (unit_obj := device.Units.get(unit)):
        return unit_obj.sValue
    return None


def get_device_n_value(devices: DeviceCollection, device_id: str, unit: int) -> Optional[int]:
    """
    Get the nValue of a device.
    
    Args:
        devices: Dictionary of devices
        device_id: ID of the device
        unit: Unit number within the device
        
    Returns:
        Optional[int]: The nValue or None if device not found
    """
    if (device := devices.get(device_id)) and (unit_obj := device.Units.get(unit)):
        return int(unit_obj.nValue)
    return None


def get_unit(devices: DeviceCollection, device_id: str, unit: int) -> Any:
    """
    Get a unit object from a device.
    
    Args:
        devices: Dictionary of devices
        device_id: ID of the device
        unit: Unit number within the device
        
    Returns:
        Any: The unit object or None if not found
    """
    if (device := devices.get(device_id)) and (unit_obj := device.Units.get(unit)):
        return unit_obj
    return None


def seconds_since_last_update(devices: DeviceCollection, device_id: str, unit: int) -> Optional[float]:
    """
    Get the seconds since the last update of a device.
    
    Args:
        devices: Dictionary of devices
        device_id: ID of the device
        unit: Unit number within the device
        
    Returns:
        Optional[float]: Seconds since last update or None if device not found
    """
    if (device := devices.get(device_id)) and (unit_obj := device.Units.get(unit)):
        if last_update_time := date_string_to_datetime(unit_obj.LastUpdate):
            return (datetime.now() - last_update_time).total_seconds()
    return None


def date_string_to_datetime(date_str: Optional[str], date_frm: str = '%Y-%m-%d %H:%M:%S') -> Optional[datetime]:
    """
    Convert string in format %Y-%m-%d %H:%M:%S to datetime object.
    Handles the Python bug http://bugs.python.org/issue27400
    
    Args:
        date_str: Date string to convert
        date_frm: Format of the date string (default: '%Y-%m-%d %H:%M:%S')
        
    Returns:
        Optional[datetime]: Datetime object or None if conversion failed
    """
    if not date_str:
        return None
        
    try:
        return datetime.strptime(date_str, date_frm)
    except TypeError:
        # Handle Python bug workaround
        try:
            import time
            return datetime(*(time.strptime(date_str, date_frm)[0:6]))
        except Exception:
            return None
    except Exception:
        return None


def get_config_item_db(key: Optional[str] = None, default: Any = {}) -> Any:
    """
    Get configuration variable from Domoticz database.
    
    Args:
        key: Configuration key to retrieve (None for all config)
        default: Default value to return if key not found
        
    Returns:
        Any: The configuration value or default if not found
    """
    try:
        config = Domoticz.Configuration()
        # Return specific key or entire config
        return config[key] if key is not None else config
    except KeyError:
        return default
    except Exception as inst:
        Domoticz.Error(f'Domoticz.Configuration read failed: {inst}')
        return default


def set_config_item_db(key: Optional[str] = None, value: Any = None) -> Dict[str, Any]:
    """
    Set configuration variable in Domoticz database.
    
    Args:
        key: Configuration key to set (None to set entire config)
        value: Value to set
        
    Returns:
        Dict[str, Any]: The updated configuration
    """
    try:
        config = Domoticz.Configuration()
        # Set specific key or entire config
        if key is not None:
            config[key] = value
        else:
            config = value
        return Domoticz.Configuration(config)
    except Exception as inst:
        Domoticz.Error(f'Domoticz.Configuration operation failed: {inst}')
        return {}


def erase_config_item_db(key: Optional[str] = None) -> Dict[str, Any]:
    """
    Erase configuration variable from Domoticz database.
    
    Args:
        key: Configuration key to erase (None to clear all)
        
    Returns:
        Dict[str, Any]: The updated configuration
    """
    try:
        config = Domoticz.Configuration()
        # Delete specific key or clear all
        if key is not None:
            del config[key]
        else:
            config.clear()
        return Domoticz.Configuration(config)
    except Exception as inst:
        Domoticz.Error(f'Domoticz.Configuration operation failed: {inst}')
        return {}


def get_distance(origin: Tuple[float, float], destination: Tuple[float, float], unit: str = 'km') -> float:
    """
    Calculate distance between two GPS coordinates using the haversine formula.
    
    Args:
        origin: (latitude, longitude) of origin point
        destination: (latitude, longitude) of destination point
        unit: Unit of distance ('km' or 'm')
        
    Returns:
        float: Distance in specified unit
    """
    # Earth's radius in kilometers
    radius = 6371

    # Convert latitude/longitude differences to radians
    dlat = radians(destination[0] - origin[0])
    dlon = radians(destination[1] - origin[1])
    
    # Haversine formula
    a = sin(dlat/2)**2 + cos(radians(origin[0])) * cos(radians(destination[0])) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance_km = radius * c

    # Return in requested units
    return distance_km * 1000 if unit == 'm' else distance_km


def average(values: List[Any]) -> Optional[float]:
    """
    Calculate the average of numeric values in a list.
    
    Args:
        values: List of values (can contain mixed types, only numeric used)
        
    Returns:
        Optional[float]: Average of numeric values or None if no numeric values
    """
    # Filter only numeric values
    numeric_values = [value for value in values if isinstance(value, (int, float))]
    
    # Calculate average if there are numeric values
    return sum(numeric_values) / len(numeric_values) if numeric_values else None


def domoticz_api(parameters: Dict[str, str], params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Call the Domoticz API with the given parameters.
    
    Args:
        parameters: Plugin parameters including address, port, username, password
        params: Parameters to send to the API
        
    Returns:
        Optional[Dict[str, Any]]: JSON response from API or None if failed
    """
    import httpx

    url = f"http://{parameters['Address']}:{parameters['Port']}/json.htm"

    try:
        # Make the API request
        response = httpx.get(
            url, 
            params=params, 
            auth=(parameters['Username'], parameters['Password']), 
            timeout=3
        )
        Domoticz.Debug(f'DomoticzAPI: url sent {response.url} - Receiving status code: {response.status_code}')
        
        # Process the response
        if response.status_code == 200:
            result_json = response.json()
            if result_json['status'] == 'OK':
                return result_json
            
            Domoticz.Debug(f"Domoticz API returned an error: status = {result_json['status']}")
        else:
            Domoticz.Debug(f"Domoticz API: http error = {response.status_code}")
            
    except Exception as e:
        Domoticz.Debug(f"Error calling '{url}' ({e})")
        import traceback
        Domoticz.Debug(f'Stack trace error: {traceback.format_exc()}')

    return None

def log_backtrace_error(parameters: Dict[str, str]) -> None:
    """
    Write the backtrace to a logfile on disk.
    Args:
        parameters: Plugin parameters including address, port, username, password
    """
    # For debugging
    import traceback
    from pathlib import Path
    log_path = Path(parameters['HomeFolder']) / f"{parameters['Name']}_traceback.txt"
    with log_path.open("a") as myfile:
        myfile.write(f'-General Error-{datetime.now()}------------------\n')
        myfile.write(f'{traceback.format_exc()}')
        myfile.write('---------------------------------\n')


# Constants for backward compatibility
TIMEDOUT = DomoticzConstants.TIMEDOUT
MINUTE = DomoticzConstants.MINUTE

# Create aliases for backward compatibility
DumpConfigToLog = dump_config_to_log
UpdateDevice = update_device
TimeoutDevice = timeout_device
CheckActivityUnitsandTimeout = check_activity_units_and_timeout
TouchDevice = touch_device
GetDevicesValue = get_device_s_value
GetDevicenValue = get_device_n_value
getUnit = get_unit
SecondsSinceLastUpdate = seconds_since_last_update
DateStringtoDateTime = date_string_to_datetime
getConfigItemDB = get_config_item_db
setConfigItemDB = set_config_item_db
eraseConfigItemDB = erase_config_item_db
getDistance = get_distance
Average = average
DomoticzAPI = domoticz_api


# Define the module's public API for better IDE support
__all__ = [
    'DomoticzConstants', 'TIMEDOUT', 'MINUTE',
    'dump_config_to_log', 'update_device', 'timeout_device',
    'check_activity_units_and_timeout', 'touch_device', 'get_device_s_value',
    'get_device_n_value', 'get_unit', 'seconds_since_last_update',
    'date_string_to_datetime', 'get_config_item_db', 'set_config_item_db',
    'erase_config_item_db', 'get_distance', 'average', 'domoticz_api',
    'log_backtrace_error',
    
    # Aliases for backward compatibility
    'DumpConfigToLog', 'UpdateDevice', 'TimeoutDevice',
    'CheckActivityUnitsandTimeout', 'TouchDevice', 'GetDevicesValue',
    'GetDevicenValue', 'getUnit', 'SecondsSinceLastUpdate',
    'DateStringtoDateTime', 'getConfigItemDB', 'setConfigItemDB',
    'eraseConfigItemDB', 'getDistance', 'Average', 'DomoticzAPI'
]
