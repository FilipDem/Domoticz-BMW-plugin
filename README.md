# Donation
It took me quite some effort to get the plugin available. Small contributions are welcome...

[![](https://www.paypalobjects.com/en_US/BE/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=AT4L7ST55JR4A)

# Domoticz-BMW-plugin
Domoticz plugin working with BMW Connected Drive. Currently it supports the keep track of the mileage, but can easily be extended with other information and even with actions or other inforamtion (eg, GPS tracking, window status, horn, ...).

If there are requests to integrate other information/functions, please leave a message.

Currently only support for European vehicles.

## Installation (linux)
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
