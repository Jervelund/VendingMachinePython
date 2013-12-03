#!/usr/bin/python

import sys
import time
import dbus
import serial
from optparse import OptionParser, make_option

print "Loading twitter library"
execfile("twt.py")
print "Loading tweets and status checker"
execfile("tweets.py")

def readData():
    try:
        print "Connecting to bluetooth"
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object("org.bluez", "/"),
                                                       "org.bluez.Manager")
        option_list = [
                        make_option("-i", "--device", action="store",
                                        type="string", dest="dev_id"),
                        ]
        parser = OptionParser(option_list=option_list)
        (options, args) = parser.parse_args()
        if options.dev_id:
            adapter_path = manager.FindAdapter(options.dev_id)
        else:
            adapter_path = manager.DefaultAdapter()
        adapter = dbus.Interface(bus.get_object("org.bluez", adapter_path),
                                                                "org.bluez.Adapter")
        address = "00:12:02:10:41:01"
        service = "spp"
        path = adapter.FindDevice(address)
        dbus_serial = dbus.Interface(bus.get_object("org.bluez", path),
                                                        "org.bluez.Serial")
        node = dbus_serial.Connect(service)

        print "Connected %s to %s" % (node, address)

        # Create serial port
        time.sleep(2)
        ser = serial.Serial(node,115200)
    except:
        print "Could not initialize bluetooth connection. Retrying."
        time.sleep(5)

    if ser:
      while True:
        ser.write("S")
        time.sleep(2);
        sodaStatus = ser.read(ser.inWaiting())
        if sodaStatus:
            parseStatus(sodaStatus)
            time.sleep(300)
        else:
            print "no response"
            break

      print "Dropped bluetooth connection. Sleeping for 5 seconds."
      dbus_serial.Disconnect(node)
      time.sleep(5)
      print "Retrying."

while True:
    readData()