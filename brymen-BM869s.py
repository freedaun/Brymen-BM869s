
import sys
import os
import hid
import time
from pathlib import Path




import msvcrt 

def key(): 
   x = msvcrt.kbhit()
   if x: 
      ret = ord(msvcrt.getch()) 
   else: 
      ret = 0 
   return ret
   
   
def rename_log(fname, depth):
    fbak = fname + ".bak";
    if Path(fbak).exists():
        depth -= 1
        if (depth == 0):
            os.remove(fbak);
        else:
            rename_log(fbak, depth)
    if Path(fname).exists():
        os.rename(fname, fbak);

   

def init_decode():
    digits = []
    for i in range(0, 256):
        digits.append(0);
    digits[0b10111110] = "0";
    digits[0b10100000] = "1";
    digits[0b11011010] = "2";
    digits[0b11111000] = "3";
    digits[0b11100100] = "4";
    digits[0b01111100] = "5";
    digits[0b01111110] = "6";
    digits[0b10101000] = "7";
    digits[0b11111110] = "8";
    digits[0b11111100] = "9";
    digits[0b00000000] = " ";
    digits[0b01000000] = "-";
    digits[0b01001110] = "F";
    digits[0b00011110] = "C";
    digits[0b00010110] = "L";
    digits[0b11110010] = "d";
    digits[0b00100000] = "i";
    digits[0b01110010] = "o";
    digits[0b01011110] = "E";
    digits[0b01000010] = "r";
    digits[0b01100010] = "n";
    return digits
digits = init_decode()



label = [10000, 10000]
def brymen869_decode(device, reply):
    global label
    display1 = " ";
    display2 = " ";
    unit1 = "";
    unit2 = "";

    if (len(reply.strip()) < 16):
        return ""

    for i in range(3, 9):
        if (reply[i] & 1):
            if (i != 3  and  i != 8):

                display1 += ".";
                display1 += digits[reply[i] - 1];

            else:
                display1 += digits[reply[i] - 1];

        else:
            display1 += digits[reply[i]];
    display1 = display1.rstrip();
    #print("["+display1+"]")

    # remove glitches
    if (len(display1) <= 3  or  display1[3] == ' '  or  display1[1] == ' '  or  (display1[3] == '-'  and  display1[3] == '-')):
        if (display1 != "  0.L"):
            return None;     # no data, some glitch

    if ((reply[2] >> 7) & 1):
        display1 = '-' + display1[1:];
    if ((reply[9] >> 4) & 1):
        display1 = '-' + display1[1:];

    kind1 = ""
    if (((reply[2]) & 1)  and  ((reply[1] >> 4) & 1)):
        kind1 = "DC+AC" + kind1
    elif ((reply[1] >> 4) & 1):
        kind1 = "DC" + kind1;
    elif ((reply[2]) & 1):
        kind1 = "AC" + kind1;
    elif (((reply[2] >> 1) & 1)  and  ((reply[2] >> 3) & 1)):
        kind1 = "T1-T2" + kind1;
    elif ((reply[2] >> 1) & 1):
        kind1 = "T1" + kind1;
    elif ((reply[2] >> 3) & 1):
        kind1 = "T2" + kind1;

    if ((reply[15] >> 4) & 1):
        unit1 = "R";
    elif (reply[15] & 1):
        unit1 = "Hz";
    elif ((reply[15] >> 1) & 1):
        unit1 = "dBm";
    elif (reply[8] & 1):
        unit1 = "V";
    elif ((reply[14] >> 7) & 1):
        unit1 = "A";
    elif ((reply[14] >> 5) & 1):
        unit1 = "F";
    elif ((reply[14] >> 4) & 1):
        unit1 = "S";
    elif ((reply[15] >> 7) & 1):
        unit1 = "D%";

    if ((reply[15] >> 6) & 1):
        unit1 = "k" + unit1;
    elif ((reply[15] >> 5) & 1):
        unit1 = "M" + unit1;
    elif ((reply[15] >> 2) & 1  and  not ((reply[15] >> 1) & 1)):
        unit1 = "m" + unit1;
    elif ((reply[15] >> 3) & 1):
        unit1 = "u" + unit1;
    elif ((reply[14] >> 6) & 1):
        unit1 = "n" + unit1;



    for i in range(10,14):
        if (i != 10  and  (reply[i]) & 1):
            display2 += ".";
            display2 += digits[reply[i] - 1];

        elif (i == 10  and  (reply[i] & 1)):
            display2 += digits[reply[i] - 1];

        else:
            display2 += digits[reply[i]];
    display2 = display2.rstrip();
    if (display2 == "diod"):
        display2 = "diode";

    kind2 = ""
    if ((reply[9] >> 5) & 1):
        kind2 = "AC" + kind2;
    elif ((reply[9] >> 6) & 1):
        kind2 = "T2" + kind2;

    if ((reply[14] >> 2) & 1):
        unit2 = "Hz";
    elif ((reply[9] >> 2) & 1):
        unit2 = "A";
    elif ((reply[14] >> 3) & 1):
        unit2 = "V";
    elif ((reply[9] >> 3) & 1):
        unit2 = "%4-20mA";

    if (reply[14] & 1):
        unit2 = "M" + unit2;
    elif ((reply[14] >> 1) & 1):
        unit2 = "k" + unit2;
    elif (reply[9] & 1):
        unit2 = "u" + unit2;
    elif (reply[9] >> 1 & 1):
        unit2 = "m" + unit2;

    #print("["+display1+"]")
    #print("["+display2+"]")
    label[device] += 1
    if (len(display2.strip()) < 2): 
        return f"{label[device]-1}: {display1}{unit1}-{kind1}";
    return f"{device}:{label[device]-1}: {display1}{unit1} {kind1}, {display2}{unit2} {kind2}";






TIMER_INTERVAL_MS = (100)
VID               = (0x0820)
PID               = (0x0001)
device_list = hid.enumerate(VID, PID)
#print(device_list)




dmm = [None,None]
response = ["", ""]

def brymen_read(device):
    #rd = device.read(64, 1000);
    #print("RD", rd)

    wr = device.write(b"\x00\x00\x86\x66");
    #print("WR", wr)
    response = b""
    while (1):
        rd = device.read(64, 1000);
        response += rd
        if (rd == b""):
            break
        time.sleep(0.01)
    return brymen869_decode(response)


def brymen_read_both():
    wr0 = dmm[0].write(b"\x00\x00\x86\x66");
    wr1 = dmm[1].write(b"\x00\x00\x86\x66");

    response0 = b""
    response1 = b""
    while (1):
        rd0 = dmm[0].read(64, 1000);
        rd1 = dmm[1].read(64, 1000);
        response0 += rd0
        response1 += rd1
        if (rd0 == b""  and  rd1 == b""):
            break
        time.sleep(0.05)
    print(response0)
    print(response1)
    return [brymen869_decode(response0), brymen869_decode(response1)]


def hid_open(device):
    global dmm, response
    if (len(device_list) > device):
        dmm[device] = hid.Device(VID, PID, path=device_list[device]["path"])
        print(f'[{device}]: {dmm[device].manufacturer} {dmm[device].product}')
    else:
        print(f"[{device}]: not found")




def brymen(flog):
    global response
    rename_log(flog, 4)
    log = open(flog, 'a');
    
    hid_open(0)
    hid_open(1)
    # time to wake DMM's 
    time.sleep(0.500)
    
    rd0 = b""
    rd1 = b""
    while (key() == 0):
        if (rd0 == b""  and  dmm[0]):
            wr0 = dmm[0].write(b"\x00\x00\x86\x66");
            measurement0 = brymen869_decode(0, response[0])
            if (measurement0):
                log.write(measurement0)
                log.write("\n")
                log.flush()
                print(measurement0)
            response[0] = b""
        if (rd1 == b""  and  dmm[1]):
            wr1 = dmm[1].write(b"\x00\x00\x86\x66");
            # write result
            measurement1 = brymen869_decode(1, response[1])
            if (measurement1):
                log.write(measurement1)
                log.write("\n")
                log.flush()
                print(measurement1)
            response[1] = b""
        if (dmm[0]):
            rd0 = dmm[0].read(64, 100);
            response[0] += rd0
        if (dmm[1]):
            rd1 = dmm[1].read(64, 100);
            response[1] += rd1

        time.sleep(0.05)

    log.close()
    # b'\x00\x11\x80\xbe\xbe\xbf\xbe\xa0\x00&\xbe\xbe\xbf\xbe\x80\x04\x86\x86\x86\x86\x00\x00\x00\x00'
    #print(response)
    



brymen("brymen.log")
#print("GLOBAL",response)

if (dmm[0]):
    dmm[0].close
if (dmm[1]):
    dmm[1].close



