# -*- coding: utf-8 -*-
#!/usr/bin/env python3

from __future__ import print_function

from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command
 
import asyncio
import websocket
from threading import Thread
import time
from datetime import datetime
import sys
import json
import random 
from mavsdk import System
import pymysql as db
import logging
from pymavlink.dialects.v20 import common as mavlink2
from pymavlink import mavutil
import subprocess
from subprocess import PIPE 
import os
import ctypes


logger = logging.getLogger()
 
class droneState :
    def __init__(self):
        self.__name = "lm_10001"
        self.__recevport = "54140"
        self.__satnum = 0
        self.__roll = "0"
        self.__pitch = "0"
        self.__yaw = "0"
        self.__latdeg = ""
        self.__londeg = ""
        self.__absalt = ""
        self.__relalt = ""
        
    def getRecevport(self):
        return self.__recevport
    
    def setRecevport(self, recevport):
        self.__recevport = recevport
        
    def getRoll(self):
        return self.__roll
    
    def setRoll(self, roll):
        self.__roll = roll
        
    def getPitch(self):
        return self.__pitch
    
    def setPitch(self, pitch):
        self.__pitch = pitch
        
    def getYaw(self):
        return self.__yaw
    
    def setYaw(self, yaw):
        self.__yaw = yaw
        
    def getName(self):
        return self.__name
    
    def setName(self, name):
        self.__name = name
        
    def getSatNum(self):
        return self.__satnum
    
    def setSatNum(self, satnum):
        self.__satnum = satnum
        
    def getLatDeg(self):
        return self.__latdeg
    
    def setLatDeg(self, latdeg):
        self.__latdeg = latdeg
        
    def getLonDeg(self):
        return self.__londeg
    
    def setLonDeg(self, londeg):
        self.__londeg = londeg
        
    def getAbsAlt(self):
        return self.__absalt
    
    def setAbsAlt(self, absalt):
        self.__absalt = absalt
          
    def getRelAlt(self):
        return self.__relalt
    
    def setRelAlt(self, relalt):
        self.__relalt = relalt
            
    
async def run(droneInfo,*args):
    

    
    # Init the drone
    #drone = System() 
    #drone = System(mavsdk_server_address="127.0.0.1", port=50051)
    print(f"Drone Connection")
    #await drone.connect(system_address="udp://:"+receivePort)
    
    connection_string = "udpin:0.0.0.0:"+receivePort;
    #connection_string = "/dev/serial1";

    # Connect to the Vehicle
    print('Connecting to vehicle on: %s' % connection_string)
    #drone = connect(connection_string, wait_ready=True)
    #drone = connect(connection_string, wait_ready=True, baud=57600) 
 
    drone = connect(connection_string, wait_ready=False, baud = 57600)
    drone.wait_ready(True, raise_exception=False)
 
    
    
    
    
    
    print(" Autopilot Firmware version: %s" % drone.version)
    
    #drone = System(mavsdk_server_address='localhost', port=14540)
    #await drone.connect()
    
    #await drone.connect(system_address="serial://COM30:57600")
    #await drone.connect(system_address="serial:///dev/serial0:921600")
    
    # MySQL Connection 연결
    #conn = db.connect(host='10.8.0.1', user='samsungdrone', password='Min002004!@#',db='sepm_db', charset='utf8')
    conn = getConnection()
    # Connection 으로부터 Cursor 생성
    curs = conn.cursor() 
    conn.ping(reconnect=True) # try reconnect
     
    
    asyncio.ensure_future(print_serversend(droneInfo,drone,conn,curs))

    
    
    
    #try:
    #    connect_websocket()
    #except Exception as err:
    #    print(err)
    #    print("connect failed")
        
 
def getConnection():
    
    try:     
        con = db.connect(host='192.168.0.23', 
                         user='mrdev', 
                         password='mrdev1',
                         db='sepm_db', 
                         charset='utf8',
                         local_infile = 1)
    except Exception as e:
        time.sleep(2)  
        con = getConnection() 
        
    return con 
 

  
async def print_serversend(droneInfo,drone,conn,curs):
    running = True
    tmName = droneHost; 
    
    
    while running:  
        now = datetime.now()
        nowtime = now.strftime('%Y-%m-%d %H:%M:%S.%f');
        sql = "INSERT INTO br_drone_state"+ \
            "(dl_id, st_status, st_satelite_num, st_bat_voltage, st_bat_level, st_speed, st_x, st_y, st_z, st_atitude,st_roll,st_pitch,st_yaw,st_head,st_state,st_mode,st_time)" + \
            "VALUES('" + tmName + "', " + \
            "1," + \
            " '"+str(drone.gps_0.satellites_visible)+"',"+ \
            " '"+str(round(drone.battery.voltage, 2) )+"',"+ \
            " '"+str(drone.battery.level)+"',"+ \
            " '"+str(round(drone.groundspeed, 1) )+"',"+ \
            " '"+str(drone.location.global_frame.lat)+"',"+ \
            " '"+str(drone.location.global_frame.lon)+"', "+ \
            " '"+str(drone.location.global_relative_frame.alt)+"', "+ \
            " '"+str(drone.location.global_frame.alt)+"', "+ \
            " '"+str(drone.attitude.roll*50)+"', "+ \
            " '"+str(drone.attitude.pitch*50)+"', "+ \
            " '"+str(drone.attitude.yaw*50)+"', "+ \
            " '"+str(drone.heading)+"', "+ \
            " '"+str(drone.system_status.state)+"', "+ \
            " '"+str(drone.mode.name)+"', "+ \
            " '"+nowtime+"');"            
        try:
            print("sql:: "+sql)    
            result = curs.execute(sql) 
        except Exception as e:
            await asyncio.sleep(2) 
            conn = getConnection()
            # Connection 으로부터 Cursor 생성
            curs = conn.cursor()  
        finally:
            # resources closing 
            conn.commit()
        await asyncio.sleep(1)  

async def print_position(droneInfo,drone,conn,curs):
    print("droneInfo========")    
     
    
    running = True
    tmName = droneHost; 
    
    while running: 
        async for position in drone.telemetry.position():
            if position.latitude_deg and position.longitude_deg:
                #latitude_deg = str(position.latitude_deg)
                droneInfo.setLatDeg(str(position.latitude_deg)); 
                #longitude_deg = str(position.longitude_deg)
                droneInfo.setLonDeg(str(position.longitude_deg)); 
                #absolute_altitude_m = int(position.absolute_altitude_m)
                droneInfo.setAbsAlt(str(position.absolute_altitude_m)); 
                #relative_altitude_m = str(position.relative_altitude_m) 
                droneInfo.setRelAlt(str(position.relative_altitude_m)); 
                print(f"drone: {position}")
                
    
if __name__ == "__main__":
    websocket.enableTrace(True) 
    
    droneInfo = droneState()
    if len(sys.argv) < 3: 
        host = "ws://192.168.0.23:5010/websocket" 
        droneHost = "lm_10001"; 
        receivePort = "14540"; 
    else:
        host = sys.argv[1]
        droneHost = sys.argv[2]
        receivePort = sys.argv[3]
        
        
    print(droneHost)
        

    #print(droneInfo.getName())
     
    #asyncio.run(main_async()) 
 
   
    # Start the main function
    asyncio.ensure_future(run(droneInfo))

    # Runs the event loop until the program is canceled with e.g. CTRL-C
    asyncio.get_event_loop().run_forever()

