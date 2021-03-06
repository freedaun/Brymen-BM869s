# Brymen-BM869s

### Logger of Brymen BM869s data

One or two BrymenBM869s (or similar) must be connected to the PC using a standard data-cable. 

Usage from windows cmd: 
    
    python brymen-BM869s.py
    
This should result in something like:

    C:\python>python brymen-BM869s.py
    [0]: Brymen Superior DMM
    [1]: Brymen Superior DMM
    1:10000:  00.001mA DC,  00.01mA AC
    0:10000:  09.824mA DC,  00.01mA AC
    0:10001:  09.824mA DC,  00.01mA AC

With a line for each multimeter you have connected. Line elements:
- `0:` indicates which multimeter
- `10001:` is a label, which increments for each multimeter & sample
- `09.824mA DC` readout of the main screen
- `00.01mA AC` readout of the second screen, when applicable

The same data is also written to `brymen.log`, for processing by another utility. Several backups are maintained, one for each session. 


### Installation

This script needs:

    python -m pip install pyserial
    python -m pip install hid               # succeeds but didn't work on 2 out of 3 PC's tested

Depending on the PC/Python install it may not find some DLL's (apparently even Python doesn't work predictably). If it complains about `hidapi`:
find Python.exe and place the [hidapi files](https://github.com/libusb/hidapi/releases/download/hidapi-0.10.1/hidapi-win.zip) next to it

This script accesses the HID interface, per the protocol documented by Brymen and on eevblog, and properly enumerates all HID devices under the Brymen VID (0x0820) and PID (0x0001). The script is easily extensible to support any number of multimeters. 

Attribution: [Brymen869s-XmlLib](https://github.com/DawOp/Brymen869s-XmlLib) provided inspiration. 



