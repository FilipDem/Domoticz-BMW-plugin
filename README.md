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
Domoticz plugin working with BMW Connected Drive. A big changes is introduced since version 2.0.0 of the plugin. BMW discontinued the BMW Connected Drive App and related services. 
* From plugin 2.0.0, the new services based on the MyBMW app are integrated. This version does not work anymore due to changes at the server side of BMW. The status of the vehicle cannot longer be retrieved.
* From plugin 3.0.0, the plugin uses bimmer_connected (https://github.com/bimmerconnected/bimmer_connected) in threading mode. It solves the problem with the vehicle status update by adding a workaround in the plugin.
* From plugin 3.1.0 (still working on it), all functionality is used from the bimmer_connected library without specific code as workaround. Minimal version of the bimmer_connected library is 0.8.0.

It is highly considered to follow the bimmer_connected evolutions on https://github.com/bimmerconnected/bimmer_connected as BMW is highly refactoring. You can also find more information about the supported cars (and functionality). Not all functionality is backported to Domoticz (yet). If there is an interesting functionality to add, let me know.

Currently it supports the keep track of the following information:
* Mileage
* Doors, windows and car: open - closed
* Remaining mileage for fuel and electric
* Remote services: flash light, horn, activate airco/heating, lock/unlock car (in case you installed a previous version without all these remote services, delete first the device in Domoticz, it will be recreated with all features afterwards)
* In case of electric support:
    * Charging status
    * Remaining charging time (working again as from version 3.1.0)
    * Battery level

If there are requests to integrate other information/functions, please leave a message.

Today, the plugin does not support BMW Connected Drive cars in China and USA.

Remark that using remote services heavily is blocked by BMW. They give a dedicated message back in that case (it will show up in the Domoticz log also). So fast executing remote service one after the other won't be successful.

Hint: you can use the remote services in combination with a script that looks to the Google Calendar... In this way it is possible to plan the start of the airco/heating.

## Installation (linux)
Preliminary install bimmer_connected by with ```sudo pip3 install bimmer_connected```.
Be sure that the python3 module ```threading``` and ```queue``` is installed (otherwise install them also as described below).

Follow this procedure to install the plugin.
* Go to "~/Domoticz/plugins" with the command ```cd ~/Domoticz/plugins```
* Create directory "Bmw" with the command ```mkdir Bmw```
* Copy all the files from github in the created directory
* Be sure the following python3 libraries are installed: urllib, json, datetime
   * use ```pip3 <library>``` to verify if the libraries are installed
   * to install the missing libraries: ```sudo pip3 install <library>```

## Configuration
Enter your BMW Connected Drive username and password, together with your with your VIN number (Vehicle Identification Number). The number can be found in your official BMW Connected Drive APP-Information.

Success!

**Don't forget a small gift by using the donation button...**
