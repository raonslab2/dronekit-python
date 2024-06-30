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
import datetime
 


def on_message(ws, message):
    print("on_message: "+message) 
    
    print("vehicle::"+str(vehicle))
    recData  = json.loads(message) 
    dlAction = recData["dlAction"]
    dlName   =  recData["dlName"]
    
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
    elif dlAction == "missiondown":
        loop.run_until_complete(drone_Mission_Down(dlName))
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
    
    actions = dlWayPoint["actions"]
    missiondetail = dlWayPoint["missionDetail"]
    #Add MAV_CMD_NAV_TAKEOFF command. This is ignored if the vehicle is already in the air.
    #cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0, 10))
 
    cmds.add(Command( 0, 
                      0, 
                      0,
                      int(missiondetail[0][0]["_waypoinframe"]),  #frame
                      int(missiondetail[0][0]["_waypoinCommand"]), #command
                      0, 
                      0, 
                      0, 
                      0, 
                      0, 
                      0, 
                      dlWayPoint["home"]["coordinate"][0], 
                      dlWayPoint["home"]["coordinate"][1], 
                      0))
    

    ssi = 0 
    for tmWayPoint in actions:
        _waypointParan1 = missiondetail[ssi+1][0]["_waypointParan1"]
        if _waypointParan1 == "":
            _waypointParan1 = 0
            
        _waypointParan2 = missiondetail[ssi+1][0]["_waypointParan2"]
        if _waypointParan2 == "":
            _waypointParan2 = 0
            
        _waypointParan3 = missiondetail[ssi+1][0]["_waypointParan3"]
        if _waypointParan3 == "":
            _waypointParan3 = 0
            
        _waypointParan4 = missiondetail[ssi+1][0]["_waypointParan4"]
        if _waypointParan4 == "":
            _waypointParan4 = 0
        
        cmds.add(Command( 
                0,  #target_system
                0,  #target_component
                0,  #seq
                int(missiondetail[ssi+1][0]["_waypoinframe"]),  #frame
                int(missiondetail[ssi+1][0]["_waypoinCommand"]), #command
                0,  #current
                0,  #autocontinue
                int(_waypointParan1),  #param1
                int(_waypointParan2),  #param2
                int(_waypointParan3),  #param3
                int(_waypointParan4),  #param4
                tmWayPoint["coordinate"][0], #lat  x
                tmWayPoint["coordinate"][1], #lon  y
                #tmWayPoint["coordinate"][2]  # z
                tmWayPoint["elevation"]  # z
            ))
        ssi = ssi +1
    #last
 
    
    print(" Upload new commands to vehicle")
    cmds.upload()
    
async def drone_Rtl():
    print("Returning to Launch")
    vehicle.mode = VehicleMode("RTL")
    
async def drone_Mission_Down(droneName):
    now = datetime.datetime.now()
    now_date = now.strftime('%Y_%m_%d')
    now_time = now.strftime('%H%M%S')
    aFileName = droneName+"_"+now_date+"_"+now_time+".txt"
    print("Drone Mission Download")
    save_mission(aFileName);
    
    
    
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

    
def download_mission():
    """
    Downloads the current mission and returns it in a list.
    It is used in save_mission() to get the file information to save.
    """
    print(" Download mission from vehicle")
    missionlist=[]
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()
    for cmd in cmds:
        missionlist.append(cmd)
    return missionlist

def save_mission(aFileName):
    """
    Save a mission in the Waypoint file format 
    (http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format).
    """
    print("\nSave mission from Vehicle to file: %s" % aFileName)    
    #Download mission from vehicle
    missionlist = download_mission()
    #Add file-format information
    output='QGC WPL 110\n'
    #Add home location as 0th waypoint
    home = vehicle.home_location
    output+="%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (0,1,0,16,0,0,0,0,home.lat,home.lon,home.alt,1)
    #Add commands
    for cmd in missionlist:
        commandline="%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (cmd.seq,cmd.current,cmd.frame,cmd.command,cmd.param1,cmd.param2,cmd.param3,cmd.param4,cmd.x,cmd.y,cmd.z,cmd.autocontinue)
        output+=commandline
    with open(aFileName, 'w') as file_:
        print("========================================================================================")
        print(output)
        print("========================================================================================")
        file_.write(output)
    
    
    
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
        host = "ws://192.168.0.29:5010/websocket"   
        droneHost = "lm_10001";  
        receivePort = "14542";
    else:
        host = sys.argv[1]
        droneHost = sys.argv[2]
        receivePort = sys.argv[3]
 
    connection_string = "udpin:0.0.0.0:"+receivePort;
    #connection_string = "/dev/serial1";

    # Connect to the Vehicle
    print('Connecting to vehicle on: %s' % connection_string)
    #vehicle = connect(connection_string, wait_ready=True)
    vehicle = connect(connection_string, wait_ready=False, baud = 57600)
    vehicle.wait_ready(True, raise_exception=False)
 
    
    print('start')
    
    try:
        connect_websocket()
    except Exception as err:
        print(err)
        print("connect failed")
    
    #arm_and_takeoff(10)

