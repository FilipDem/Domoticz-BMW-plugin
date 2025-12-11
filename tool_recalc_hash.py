#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TOOL to recalculate the hash value of the keys in the JSON configuration file.
This key is also stored in the plugin settings (hardware table of the domoticz.db).

Author: Filip Demaertelaere
Version: 5.0.0
License: MIT
"""

import sys, os
import hashlib
import json

# Streaming key filename
_STREAMING_KEY_FILE = 'Bmw_keys_streaming.json'

try:
    with open(f"{_STREAMING_KEY_FILE}", "r") as json_file:
        streamingKeys = json.load(json_file)
    for vin_number, vehicle_data in streamingKeys.items():
        print(f"\n VIN: {vin_number}")
        # Iterate over the values in the dictionary (parent.streamingKeys)
        container_keys = []
        for value, key in vehicle_data.items():
            if isinstance(key, str):
                container_keys.append(key)
            elif isinstance(key, list):
                container_keys.extend(key)
            print(f"      {key}")
        sorted_keys = str(tuple(sorted(set(container_keys))))
        key_hash = hashlib.sha256(sorted_keys.encode('utf-8')).hexdigest()
        print(f" CONTAINER: {sorted_keys}")
        print(f" HASH: {key_hash}")
except Exception as e:
    print(f"Problem: {e})!")

