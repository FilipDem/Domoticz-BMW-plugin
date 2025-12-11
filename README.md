# PRELIMINARY REMARK !!
The bimmer_connected API is no longer working due to restrictions at BMW side. A version of the plugin using the official BMW API is available in the branch CarData!!!

# Donation
It took me quite some effort to get the plugin available. Small contributions are welcome...

## Use your Mobile Banking App and scan the QR Code
The QR codes comply the EPC069-12 European Standard for SEPA Credit Transfers ([SCT](https://www.europeanpaymentscouncil.eu/sites/default/files/KB/files/EPC069-12%20v2.1%20Quick%20Response%20Code%20-%20Guidelines%20to%20Enable%20the%20Data%20Capture%20for%20the%20Initiation%20of%20a%20SCT.pdf)). The amount of the donation can possibly be modified in your Mobile Banking App.
| 5 EUR      | 10 EUR      |
|------------|-------------|
| <img src="https://user-images.githubusercontent.com/16196363/110995432-a4db0d00-837a-11eb-99b4-e7059a85b68d.png" width="80" height="80"> | <img src="https://user-images.githubusercontent.com/16196363/110995495-bb816400-837a-11eb-9f71-8139df49e3fe.png" width="80" height="80"> |

## Use PayPal
[![](https://www.paypalobjects.com/en_US/BE/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=AT4L7ST55JR4A) 

# Domoticz-BMW-plugin
Since BMW blocked all access to the BMW Connected Drive, the [bimmer_connected](https://github.com/bimmerconnected/bimmer_connected) library is no longer operational.
From plugin 5.0.0, the Domoticz-BMW-plugin is using data from the BMW Open Data Platform based on the official API from BMW, shortly called "CarData". For an introduction, please refer to [CarData Customer Portal](https://bmw-cardata.bmwgroup.com/customer/public/api-documentation/Id-Introduction).
This has also an impact on the Domoticz-BMW-plugin functionality:
* As CarData is "read-only", it cannot be used to activate/deactivate services towards the car. This means that the "remote services" are no longer supported by the Domoticz-BMW-plugin. For the same reason, also the charging limits and the charging mode can no longer be set. The Domoticz devices created for this purpose are automatically changed to an "unused" stage (you can still see them in the Hardware - Devices list).
* BMW supports an "unlimited" streaming service for the CarData, ie an MQTT broker that sends the selected streaming keys. However new data is sent only when some status changes are effected at car level. When the car is "idle", no update is received. Even when an electric car is charging, from experience it shows that at a certain moment no updates are coming in...
* BMW supports also an API to get data "on request", however there is a quota on the number of messages currently defined at 50. This means that it limits the speed of polling.

Domoticz-BMW-plugin take benefit from both possibilities, ie streaming and API requests. All streaming information coming in is processed. On top, there is a smart polling mechanism to actively update the information "on request". The smart polling algorthm will spread the available API Quota over the remaining day-time, taking into account the possible refresh of data through the streaming channel.

Currently the Domoticz-BMW-plugin supports tracking of the following information:
* Mileage (several devices are created to followup the mileage)
* Driving (indicates whether the car is driving or not)
* Home (indicates whether the car is located within a defined area)
* Doors, windows and car: open - closed
* Remaining mileage for fuel and electric
* In case of electric support:
    * Charging status
    * Remaining charging time
    * Battery level

If there are requests to integrate other information/functions, please leave a message.

## Installation (linux)
Preliminary install the python3 library paho-mqtt by with ```sudo pip3 install paho-mqtt```.

Follow this procedure to install the plugin.
* Go to "~/Domoticz/plugins" with the command ```cd ~/Domoticz/plugins```
* Create directory "Bmw" with the command ```mkdir Bmw```
* Copy all the files from github in the created directory
* Be sure the following python3 libraries are installed: paho-mqtt, json, datetime
   * use ```pip3 <library>``` to verify if the libraries are installed
   * to install the missing libraries: ```sudo pip3 install <library>```

## Configuration
### Activation of BMW CarData
The steps below summarize how to activate the BMW CarData service within the MyBMW portal. For a detailed, comprehensive guide, please visit the official [documentation](https://bmw-cardata.bmwgroup.com/customer/public/api-documentation/Id-Introduction).
* Navigate to the MyBMW Portal, log in with your credentials, and go to the "Vehicle Overview" section.
* Proceed to the "BMW CarData" section.
* Scroll down to the "TECHNICAL ACCESS TO BMW CARDATA" section.
* Click on "Create CarData-client" and ensure both "Request Access to CarData API" and "CarData Stream" options are activated.
* Scroll to the "STREAM CARDATA" section and click "Change data selection.
* Select all data keys you wish to include in the stream. Refer to the **Streaming Configuration** section below for required keys.

### Plugin Configuration Parameters
The following parameters are required for initial plugin setup:
* **BMW CarData Client_id**: The unique value obtained from the MyBMW portal after creating the CarData Client.
* **Vehicle Identification Number (VIN)**: The full, 17-character VIN of your BMW vehicle, used to identify the specific car to monitor.
* **Min. Update Interval (Minutes)**: Defines the minimal interval (in minutes) at which the plugin will check for new data. If the smart polling would arrive at a shorter interval, it will be overwritten by this value.
* **Debug Level**: Sets the logging verbosity. Higher levels provide more diagnostic information for troubleshooting purposes.

### OAuth2 Authentication
When the plugin is started for the first time, an authentication status message will appear in the Domoticz log. 
Copy the complete verification URI, open it in your browser, and complete the process before the displayed expiry time (you may be prompted to re-enter your MyBMW username and password).
```
        ============================================================<
        BMW CarData Authentication Required
        ============================================================
        User Code: [client_id]
        Please visit: [verification_uri_complete]
        Complete the authentication in your browser before 15:30:00...
        ============================================================
```
Upon successful authentication, you will see the confirmation message: "BMW CarData Authentication successful! Starting BMW CarData MQTT connection..." in the Domoticz log.

### Streaming configuration (Bmw_keys_streaming.json)
The configuration file, "Bmw_keys_streaming.json," maps BMW CarData streaming keys to the corresponding implemented Domoticz devices. This JSON file supports multiple cars. The default settings should typically be correct and require no changes. The example shows configurations for a fuel car and a hybrid fuel/electric car.
Ensure you update the configuration file with your specific VIN(s). You may add or remove VIN sections to monitor multiple or fewer vehicles.
Don't forget to update the VIN to your specific car in the Bmw_keys_streaming.json file.

Configuration Rules:
* If a device status depends on **one single** BMW CarData key, list only that key (e.g., mileage information).
* If a device status depends on data from **several** BMW CarData keys, use a JSON array.
* If an option is removed or not required, deleting its entry from the JSON file will automatically set the corresponding Domoticz device to **UNUSED** (e.g., removing 'Charging' status for a gasoline-only vehicle).

Note that information will only be available if the respective BMW CarData keys are actively included in the data stream (as configured in the **Activation of BMW CarData** chapter above).

Example of the configuration file:
```
        "WBAJF11YYYYYYYYYY": {
            "Mileage": "vehicle.vehicle.travelledDistance",
            "Doors": ["vehicle.cabin.door.row1.driver.isOpen", "vehicle.cabin.door.row1.passenger.isOpen", "vehicle.cabin.door.row2.driver.isOpen", "vehicle.cabin.door.row2.passenger.isOpen", "vehicle.body.trunk.door.isOpen"],
            "Windows": ["vehicle.cabin.window.row1.driver.status", "vehicle.cabin.window.row1.passenger.status", "vehicle.cabin.window.row2.driver.status", "vehicle.cabin.window.row2.passenger.status", "vehicle.cabin.sunroof.overallStatus"],
            "Locked": "vehicle.cabin.door.status",
            "Location": ["vehicle.cabin.infotainment.navigation.currentLocation.latitude", "vehicle.cabin.infotainment.navigation.currentLocation.longitude"],
            "Driving": "vehicle.isMoving",
            "RemainingRangeTotal": "vehicle.drivetrain.totalRemainingRange"
        },
        "WBA21EFXXXXXXXXXX": {
            "Mileage": "vehicle.vehicle.travelledDistance",
            "Doors": ["vehicle.cabin.door.row1.driver.isOpen", "vehicle.cabin.door.row1.passenger.isOpen", "vehicle.cabin.door.row2.driver.isOpen", "vehicle.cabin.door.row2.passenger.isOpen", "vehicle.body.trunk.door.isOpen"],
            "Windows": ["vehicle.cabin.window.row1.driver.status", "vehicle.cabin.window.row1.passenger.status", "vehicle.cabin.window.row2.driver.status", "vehicle.cabin.window.row2.passenger.status", "vehicle.cabin.sunroof.overallStatus"],
            "Locked": "vehicle.cabin.door.status",
            "Location": ["vehicle.cabin.infotainment.navigation.currentLocation.latitude", "vehicle.cabin.infotainment.navigation.currentLocation.longitude"],
            "Driving": "vehicle.isMoving",
            "RemainingRangeTotal": "vehicle.drivetrain.totalRemainingRange",
            "RemainingRangeElec": "vehicle.drivetrain.electricEngine.kombiRemainingElectricRange",
            "Charging": "vehicle.drivetrain.electricEngine.charging.hvStatus",
            "BatteryLevel": "vehicle.drivetrain.batteryManagement.header",
            "ChargingTime": "vehicle.drivetrain.electricEngine.charging.timeRemaining"
        }
```

## Tips/Hints
* you can create a small script that activate other devices one the car is detected coming "home". I personally use this to switch already on several devices so that my house is "ready" once arriving by car.

## Privacy
For the management of the "Home" function, the geolocation of the car is used. This means that the location coordinates of the car is known by the plugin. However for privacy reason, these coordinates are NOT stored in any matter in the plugin. Only the last coordinate is kept in volatile memory and systematically overwritten. This coordinates are also lost once Domoticz or the plugin is stopped, reset, removed, ...


Success!

**Don't forget a small gift by using the donation button...**
