#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

from dronekit import connect, VehicleMode, LocationGlobalRelative, Command
import time
import math
from pymavlink import mavutil

import asyncio 
import websocket 
import sys
import json
import threading
import datetime

def on_message(ws, message):
    print("on_message: " + message)
    
    recData = json.loads(message)
    dlAction = recData.get("dlAction")
    dlName = recData.get("dlName")
    
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # No running loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if dlAction == "arm":
        loop.run_until_complete(drone_Arm())
    elif dlAction == "disarm":
        loop.run_until_complete(drone_DisArm())
    elif dlAction == "reboot":
        loop.run_until_complete(drone_Reboot())
    elif dlAction == "takeoff":
        loop.run_until_complete(drone_TakeOff())
    elif dlAction == "land":
        loop.run_until_complete(drone_Land())
    elif dlAction == "rtl":
        loop.run_until_complete(drone_Rtl())
    elif dlAction == "missiondown":
        loop.run_until_complete(drone_Mission_Down(dlName))
    elif dlAction == "waypoint":
        dlWayPoint = recData.get("dlWayPoint")
        loop.run_until_complete(drone_WayPoint(dlWayPoint))
    elif dlAction == "auto":
        loop.run_until_complete(drone_Auto())
    elif dlAction == "goto":
        dlOption = recData.get("dlOption")
        loop.run_until_complete(drone_Goto(dlOption))
    else:
        print("======알 수 없음============")
    print("======완료============")

async def drone_Auto():
    print("Auto msg =======================================")
    vehicle.mode = VehicleMode("AUTO")

async def drone_WayPoint(dlWayPoint):
    print("waypoint msg =======================================")
    cmds = vehicle.commands
    print("Clear any existing commands")
    cmds.clear()

    print("Define/add new commands.")
    
    actions = dlWayPoint["actions"]
    missiondetail = dlWayPoint["missionDetail"]
    
    if missiondetail and missiondetail[0]:
        cmds.add(Command( 
            0, 
            0, 
            0,
            int(missiondetail[0][0]["_waypoinframe"]),  # frame
            int(missiondetail[0][0]["_waypoinCommand"]), # command
            0, 
            0, 
            0, 
            0, 
            0, 
            0, 
            dlWayPoint["home"]["coordinate"][0], 
            dlWayPoint["home"]["coordinate"][1], 
            0
        ))

    for i, tmWayPoint in enumerate(actions):
        if i + 1 < len(missiondetail) and missiondetail[i + 1]:
            _waypointParan1 = missiondetail[i + 1][0].get("_waypointParan1", "0")
            _waypointParan2 = missiondetail[i + 1][0].get("_waypointParan2", "0")
            _waypointParan3 = missiondetail[i + 1][0].get("_waypointParan3", "0")
            _waypointParan4 = missiondetail[i + 1][0].get("_waypointParan4", "0")
            
            _waypointParan1 = int(_waypointParan1) if _waypointParan1 else 0
            _waypointParan2 = int(_waypointParan2) if _waypointParan2 else 0
            _waypointParan3 = int(_waypointParan3) if _waypointParan3 else 0
            _waypointParan4 = int(_waypointParan4) if _waypointParan4 else 0
            
            cmds.add(Command(
                0,  # target_system
                0,  # target_component
                0,  # seq
                int(missiondetail[i + 1][0]["_waypoinframe"]),  # frame
                int(missiondetail[i + 1][0]["_waypoinCommand"]), # command
                0,  # current
                0,  # autocontinue
                int(_waypointParan1),  # param1
                int(_waypointParan2),  # param2
                int(_waypointParan3),  # param3
                int(_waypointParan4),  # param4
                tmWayPoint["coordinate"][0], # lat x
                tmWayPoint["coordinate"][1], # lon y
                tmWayPoint["elevation"]  # z
            ))

    print("Upload new commands to vehicle")
    cmds.upload()

async def drone_Rtl():
    print("Returning to Launch")
    vehicle.mode = VehicleMode("RTL")

async def drone_Mission_Down(droneName):
    now = datetime.datetime.now()
    now_date = now.strftime('%Y_%m_%d')
    now_time = now.strftime('%H%M%S')
    aFileName = f"{droneName}_{now_date}_{now_time}.txt"
    print("Drone Mission Download")
    save_mission(aFileName)

async def drone_Reboot():
    print("drone_Reboot")
    vehicle.reboot()

async def drone_Arm():
    print("Basic pre-arm checks")
    while not vehicle.is_armable:
        print("Waiting for vehicle to initialise...")
        time.sleep(1)
    print("Arming motors")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

async def drone_DisArm():
    print("disarm motors")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = False

async def drone_Goto(dlOption):
    st = dlOption.split('|')
    vehicle.mode = VehicleMode("GUIDED")
    point1 = LocationGlobalRelative(float(st[1]), float(st[0]), float(st[2]))
    tmgroundspeed = float(st[3])
    vehicle.simple_goto(point1, groundspeed=tmgroundspeed)

async def drone_Land():
    print("Now let's land")
    vehicle.mode = VehicleMode("LAND")
    print(vehicle.mode)

def download_mission():
    print("Download mission from vehicle")
    missionlist = []
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()
    for cmd in cmds:
        missionlist.append(cmd)
    return missionlist

def save_mission(aFileName):
    print("\nSave mission from Vehicle to file: %s" % aFileName)
    missionlist = download_mission()
    output = 'QGC WPL 110\n'
    home = vehicle.home_location
    output += "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
        0, 1, 0, 16, 0, 0, 0, 0, home.lat, home.lon, home.alt, 1)
    for cmd in missionlist:
        commandline = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
            cmd.seq, cmd.current, cmd.frame, cmd.command, cmd.param1, cmd.param2, cmd.param3, cmd.param4, cmd.x, cmd.y, cmd.z, cmd.autocontinue)
        output += commandline
    with open(aFileName, 'w') as file_:
        print("========================================================================================")
        print(output)
        print("========================================================================================")
        file_.write(output)

def on_open(ws):
    json_object_drone = {"DATA_GUBUN":"DRONE","DATA_REQUEST":"OPEN","DATA_DRONE_ID":droneHost}
    json_string_drone = json.dumps(json_object_drone, indent=2)
    ws.send(json_string_drone)

    t = threading.Thread(target=threadRun, args=(ws, 1, 10000000, json_string_drone))
    t.start()

def threadRun(ws, low, high, json_string_drone):
    for i in range(low, high):
        time.sleep(1)

def on_error(ws, error):
    print("Retry : %s" % time.ctime())
    time.sleep(2)
    connect_websocket()  # retry after 2 seconds

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")
    print("Retry : %s" % time.ctime())
    time.sleep(2)
    connect_websocket()  # retry after 2 seconds

async def drone_TakeOff():
    arm_and_takeoff(10)

def arm_and_takeoff(aTargetAltitude):
    print("Basic pre-arm checks")
    while not vehicle.is_armable:
        print("Waiting for vehicle to initialise...")
        time.sleep(1)
    print("Arming motors")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude)  # Take off to target altitude

def connect_websocket():
    print("host : %s" % host)
    print("droneHost : %s" % droneHost)
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
        droneHost = "lm_10001"
        receivePort = "14541"
    else:
        host = sys.argv[1]
        droneHost = sys.argv[2]
        receivePort = sys.argv[3]

    connection_string = "udpin:0.0.0.0:" + receivePort
    # connection_string = "/dev/serial1";

    print('Connecting to vehicle on: %s' % connection_string)
    vehicle = connect(connection_string, wait_ready=False, baud=57600)
    vehicle.wait_ready(True, raise_exception=False)

    print('start')

    try:
        connect_websocket()
    except Exception as err:
        print(err)
        print("connect failed")
