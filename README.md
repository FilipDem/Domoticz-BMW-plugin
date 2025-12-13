# 🚗 Domoticz-BMW-Plugin

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/)
![Status](https://img.shields.io/badge/Status-Stable-brightgreen)
![Domoticz](https://img.shields.io/badge/Domoticz-2022%2B-blue)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 1. 📢 Important Notice (Non-functional API)

The **old `bimmer_connected` API** is no longer functional due to restrictions on BMW's side.

* This plugin (from version 5.0.0 onwards) uses the **official BMW Open Data API (CarData)**.
* The code utilizing the official API is available in the **`CarData`** branch.

---

## 2. 🌟 Overview & Features

Since BMW blocked access to **BMW Connected Drive**, the [bimmer_connected](https://github.com/bimmerconnected/bimmer_connected) library no longer works.

From **plugin version 5.0.0**, this Domoticz plugin utilizes the official **BMW Open Data API (CarData)**. Please refer to the [CarData Customer Portal](https://bmw-cardata.bmwgroup.com/customer/public/api-documentation/Id-Introduction) for more details regarding the API.

### 2.1 Key Changes

| Function | Old API (Pre-5.0.0) | New API (CarData) | Note |
| :--- | :--- | :--- | :--- |
| **Data** | Full access (read/write) | **Read-only** | Remote services and charging limits are no longer supported. Related Domoticz devices will be marked as **UNUSED**. |
| **Updates** | Polling | **Streaming (MQTT) + Smart Polling** | Combines direct updates (on status change) with limited On-demand API (max. 50/day). |

### 2.2 Supported Information

* Mileage
* Driving status
* Home detection (geofencing)
* Status of doors, windows, and trunk
* Remaining range (fuel & electric)

**🔌 Additional for Electric Vehicles:**
* Charging status
* Remaining charging time
* Battery level

---

## 3. 🛠 Installation (Linux)

Follow these steps to install the Domoticz-BMW plugin:

1.  **Install required Python libraries:**
    ```bash
    sudo pip3 install paho-mqtt json datetime
    ```
2.  **Navigate to the Domoticz plugin directory:**
    ```bash
    cd ~/Domoticz/plugins
    ```
3.  **Clone the repository:**
    ```bash
    git clone https://github.com/FilipDem/Domoticz-BMW-plugin
    ```

4.  **update the repository:**
    ```bash
    git pull
    ```
---

## 4. ⚙️ Configuration

### 4.1 Activation of BMW CarData

The official [documentation](https://bmw-cardata.bmwgroup.com/customer/public/api-documentation/Id-Introduction) provides a comprehensive guide. Below is a summary of the steps required in the **MyBMW Portal**:

1.  Log in to the MyBMW Portal and go to **"Vehicle Overview"**.
2.  Navigate to the **"BMW CarData"** section.
3.  Scroll down to **"TECHNICAL ACCESS TO BMW CARDATA"**.
4.  Click on **"Create CarData-client"** and ensure both **"Request Access to CarData API"** and **"CarData Stream"** are activated.
5.  Go to the **"STREAM CARDATA"** section and click **"Change data selection"**.
6.  Select all data keys you wish to stream. **Necessary keys** can be found in section **4.4 Streaming Configuration**.

### 4.2 Plugin Configuration Parameters

These parameters are set in the Domoticz hardware configuration:

| Parameter | Description |
| :--- | :--- |
| **BMW CarData Client_id** | The unique Client ID obtained after creating the CarData Client in the MyBMW Portal. |
| **Vehicle Identification Number (VIN)** | The full, 17-character VIN of your BMW vehicle. |
| **Min. Update Interval (Minutes)** | The minimal interval (in minutes) to check for new data. This overrides shorter smart polling intervals. |
| **Debug Level** | The logging level (verbose). Higher levels provide more diagnostic information for troubleshooting. |

### 4.3 OAuth2 Authentication (First Run)

When the plugin is started for the first time, an authentication status message will appear in the Domoticz log.

1.  **Copy the complete verification URI** and open it in your browser.
2.  Complete the authentication process (you may need to re-enter your MyBMW credentials) **before the displayed expiry time**.

> **Example of the log message:**
>
> ```text
> ============================================================
> BMW CarData Authentication Required
> ============================================================
> User Code: [client_id]
> Please visit: [verification_uri_complete]
> Complete the authentication in your browser before 15:30:00...
> ============================================================
> ```

Successful authentication is confirmed with: *"BMW CarData Authentication successful! Starting BMW CarData MQTT connection..."* in the log.

### 4.4 Streaming Configuration (`Bmw_keys_streaming.json`)

The file `Bmw_keys_streaming.json` maps the BMW CarData streaming keys to the implemented Domoticz devices. The file supports multiple cars.

* The **default settings** should generally be correct and usually require no changes.
* **Update the VIN(s)** in the file to match your specific vehicle(s). You can add or remove VIN sections.

#### Configuration Logic
| Dependency | JSON Structure | Example |
| :--- | :--- | :--- |
| **Single key** | Single string | `"Mileage": "vehicle.vehicle.travelledDistance"` |
| **Multiple keys** | JSON Array | `"Doors": ["key1", "key2", ...]` |

> **NOTE:** If an option is removed from this JSON file, the corresponding Domoticz device will automatically be set to **UNUSED** (e.g., removing 'Charging' for a gasoline-only car). Information is only available if the keys are activated in the **Activation of BMW CarData** section.

#### Configuration File Example
```json
{
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
}
```

---

## 5. 💡 Tips & Privacy

### 5.1 Tips
* You can create a small script to activate other Domoticz devices once the car is detected as "Home" (geofencing). This is useful for getting your house ready before you arrive.

### 5.2 Privacy
* The **"Home" (geofencing)** function uses the car's geolocation.
* **IMPORTANT:** For privacy reasons, these coordinates are **NOT** stored persistently by the plugin. Only the last known coordinate is kept in volatile memory and systematically overwritten. These coordinates are lost immediately if Domoticz or the plugin is stopped or reset.

---

## 6. 💖 Donations

Developing and maintaining this plugin required considerable effort. Small contributions are very welcome!

### 6.1 Via Mobile Banking (QR Code)

Scan the QR codes below. They comply with the **EPC069-12 European Standard** for SEPA Credit Transfers (SCT).

> You can adjust the donation amount in your banking app.

| 5 EUR | 10 EUR |
| :---: | :---: |
| <img src="https://user-images.githubusercontent.com/16196363/110995432-a4db0d00-837a-11eb-99b4-e7059a85b68d.png" width="100" height="100"> | <img src="https://user-images.githubusercontent.com/16196363/110995495-bb816400-837a-11eb-9f71-8139df49e3fe.png" width="100" height="100"> |

### 6.2 Via PayPal

[![Donate via PayPal](https://www.paypalobjects.com/en_US/BE/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=AT4L7ST55JR4A)
