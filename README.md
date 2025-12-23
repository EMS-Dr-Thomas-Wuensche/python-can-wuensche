python-can plugin for CAN bus interfaces from EMS Dr. Thomas Wuensche e.K.  
This plugin provides integration of EMS Dr. Thomas Wuensche CAN interfaces (CPC-USB, CPC-PCIe, etc.) into the python-can library. It supports both Classic CAN and CAN FD with the common bitrate configurations.

### Dependencies
This project requires python-can (version >= 4.2). If it isn't automatically installed with this project, then you can manually install it using:  
`python -m pip install python-can`  

### Install
Install python-can plugin 'can-wuensche' by running the following command in a terminal. Ensure that the file is in the current directory or provide the full path to the file:  
`python -m pip install can-wuensche.whl` or  
`python -m pip install --no-index --find-links=can-wuensche.whl can_wuensche`  

### Usage
Simply change the interface type of your can.Bus instance to "wuensche" and adjust the other values (channel) accordingly.  
Examples to open a channel with interface from cpcconf.ini or specified directly.  
Example 1 CAN: `bus = can.Bus(interface="wuensche", channel="CHAN00", bitrate=500000)`  
Example 2 CAN: `bus = can.Bus(interface="wuensche", channel='{ "CHAN" : {"InterfaceType" : "CPC-USB", "SerialNumber" : "9999999"}}', bitrate=500000)`  
Example 3 CAN FD: `bus = can.Bus(interface="wuensche", channel="CHAN00", fd=1, nom_bitrate=1000000, data_bitrate=4000000)`  
Example 4 CAN FD: `bus = can.Bus(interface="wuensche", channel="CHAN00", fd=1, f_clock=40000000, nom_tseg1=15, nom_tseg2=4, nom_sjw=3, nom_brp=2, data_tseg1=7, data_tseg2=2, data_sjw=1, data_brp=1)`  
