#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command
import time
import math
from pymavlink import mavutil

import asyncio 
import websocket 
import time
import sys
import json
import threading
 


def on_message(ws, message):
    print("on_message: "+message) 
    
    print("vehicle::"+str(vehicle))
    recData = json.loads(message) 
    dlAction = recData["dlAction"]
    
    loop = asyncio.get_event_loop()
    
    if dlAction == "arm":
        loop.run_until_complete(drone_Arm())
    elif dlAction == "disarm":
        loop.run_until_complete(drone_DisArm())
    elif dlAction == "reboot":
        loop.run_until_complete(drone_Reboot())
    elif dlAction == "takeoff":
        loop.run_until_complete(drone_TakteOff())
    elif dlAction == "land":
        loop.run_until_complete(drone_Land())
    elif dlAction == "rtl":
        loop.run_until_complete(drone_Rtl())
    elif dlAction == "waypoint":
        dlWayPoint = recData["dlWayPoint"]
        loop.run_until_complete(drone_WayPoint(dlWayPoint))
    elif dlAction == "auto":
        loop.run_until_complete(drone_Auto())
    elif dlAction == "goto":
        dlOption = recData["dlOption"]
        loop.run_until_complete(drone_Goto(dlOption))
    else:
        print("======알수없음============") 
     
    #loop = asyncio.get_event_loop()
    #loop.run_until_complete(drone_Arm())
    print("======complete============") 
    
    
async def drone_Auto():
    print("Auto msg =======================================") 
    vehicle.mode = VehicleMode("AUTO")
    
async def drone_WayPoint(dlWayPoint):
    print("waypoint msg =======================================") 
    #print(dlWayPoint["actions"]);
    #print(dlWayPoint["home"]["coordinate"][0]);
    #print(dlWayPoint["home"]["coordinate"][1]);
    #for homePosition in dlWayPoint["home"]["coordinate"]:
    #    print(homePosition);
    cmds = vehicle.commands
    print(" Clear any existing commands")
    cmds.clear() 
    
    print(" Define/add new commands.")
    #Add MAV_CMD_NAV_TAKEOFF command. This is ignored if the vehicle is already in the air.
    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0, 10))
    cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, dlWayPoint["home"]["coordinate"][0], dlWayPoint["home"]["coordinate"][1], 11))
    
    actions = dlWayPoint["actions"]
    ssi = 11
    for tmWayPoint in actions:
        cmds.add(Command( 
                0, 
                0, 
                0, 
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, 
                mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 
                0, 0, 0, 0, 0, 0,
                tmWayPoint["coordinate"][0],
                tmWayPoint["coordinate"][1], 
                ssi
            ))
        ssi = ssi +1
        
    print(" Upload new commands to vehicle")
    cmds.upload()
    
async def drone_Rtl():
    print("Returning to Launch")
    vehicle.mode = VehicleMode("RTL")
    
async def drone_Reboot():
    print("drone_Reboot")
    vehicle.reboot();
    
async def drone_Arm():
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't let the user try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

        
    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True
    
async def drone_DisArm():
    # Copter should arm in GUIDED mode
    print("disarm motors")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.disarm();
    
async def drone_Goto(dlOption):
    # Copter should arm in GUIDED mode 
    st = dlOption.split('|') 
    vehicle.mode = VehicleMode("GUIDED")
    point1 = LocationGlobalRelative(float(st[1]) ,float(st[0]) ,float(st[2]) )
    tmgroundspeed = float(st[3]);
    vehicle.simple_goto(point1, groundspeed=tmgroundspeed) 
    

async def drone_Land(): 
    print("Now let's land")
    vehicle.mode = VehicleMode("LAND")
    print(vehicle.mode) 

    
def on_open(ws): 
    #drone first open
    json_object_drone = {"DATA_GUBUN":"DRONE","DATA_REQUEST":"OPEN","DATA_DRONE_ID":droneHost}
    json_string_drone = json.dumps(json_object_drone, indent=2)
    #ws.send("Hello %d" % json_string)
    ws.send(json_string_drone)
    
    
    t = threading.Thread(target=threadRun, args=(ws,1, 10000000,json_string_drone))
    t.start()
    
def threadRun(ws,low, high,json_string_drone):
    total = 0
    running = True
    
    i = 0
    for i in range(low, high):
        #print("i ", i)
        #ws.send(json_string_drone)
        i = i + 1
        time.sleep(1)
 
    

def on_error(ws, error):
    print ("Retry : %s" % time.ctime())
    time.sleep(2)
    connect_websocket() # retry per 10 seconds
    
def on_close(ws, close_status_code, close_msg):
    print("### closed ###")
    print ("Retry : %s" % time.ctime())
    time.sleep(2)
    connect_websocket() # retry per 10 seconds
    
async def drone_TakteOff():
    arm_and_takeoff(10)
    
def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't let the user try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

        
    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True
    

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
    #  after Vehicle.simple_takeoff will execute immediately).
    #while True:
    #    print(" Altitude: ", vehicle.location.global_relative_frame.alt)      
    #    if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95: #Trigger just below target alt.
    #        print("Reached target altitude")
    #        break
    #    time.sleep(1)

def connect_websocket(): 
    
    print ("host : %s" % host)
    print ("droneHost : %s" % droneHost)
    ws = websocket.WebSocketApp(host,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever() 
 

if __name__ == "__main__":
    websocket.enableTrace(True)
    if len(sys.argv) < 3:
        host = "ws://10.8.0.1:5010/websocket"
        #host = "ws://34.64.140.142:5010/websocket"       
        #host = "ws://127.0.0.1:5010/websocket"   
        droneHost = "lm_10001";
        receivePort = "14541";
    else:
        host = sys.argv[1]
        droneHost = sys.argv[2]
        receivePort = sys.argv[3]
 
    connection_string = "udpin:127.0.0.1:"+receivePort;

    # Connect to the Vehicle
    print('Connecting to vehicle on: %s' % connection_string)
    vehicle = connect(connection_string, wait_ready=True)
    
    try:
        connect_websocket()
    except Exception as err:
        print(err)
        print("connect failed")
    
    #arm_and_takeoff(10)

