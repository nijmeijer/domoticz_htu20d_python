Domoticz python plugin for TE-HTU20D I2C humidity / temperature sensors


Status
------
Under development. Requires domoticz hardware-timeout to be set to 1 min. 

Prerequesites
-------------
An FTDI USB-I2C module (for example FT232h), with a HTU20D(F) sensor attached to it.

Limitations
------------

Install
-----------
in folder domoticz/plugins  :
git clone https://github.com/nijmeijer/domoticz_htu20d_python htu20d_ftdi
This will create a folder named htu20d_ftdi, containing the file "plugin.py" as expected by domoticz

Restart domoticz, and add the new HARDWARE.
