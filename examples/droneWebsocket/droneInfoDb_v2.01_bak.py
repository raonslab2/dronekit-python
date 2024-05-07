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
import configparser

logger = logging.getLogger()


# ConfigParser 인스턴스 생성
config = configparser.ConfigParser()

# config.ini 파일 로드
config.read('config.ini')

# 데이터베이스 설정 읽기
db_host = config['database']['host']
db_user = config['database']['user']
db_password = config['database']['password']
db_name = config['database']['dbname']
db_charset = config['database']['charset']
local_infile = config['database'].getboolean('local_infile')

# 드론 설정 읽기
drone_host = config['drone']['drone_host']
drone_receive_port = config['drone']['receive_port']

# 웹소켓 설정 읽기
websocket_host = config['websocket']['host']
websocket_drone_host = config['websocket']['drone_host']
websocket_receive_port = config['websocket']['receive_port']


 
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
            
    
# 이전에 정의된 run 함수나 다른 함수에서 드론 호스트나 포트 정보 사용
async def run(droneInfo, *args):
    connection_string = f"udpin:0.0.0.0:{drone_receive_port}"
    print('Connecting to vehicle on: %s' % connection_string)
    drone = connect(connection_string, wait_ready=False, baud=57600)
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
        
 
import time

def getConnection(retry_count=5):
    while retry_count > 0:
        try:
            con = db.connect(host=db_host, 
                             user=db_user, 
                             password=db_password,
                             db=db_name, 
                             charset=db_charset,
                             local_infile=local_infile)
            return con
        except Exception as e:
            print(f"Database connection failed, retrying... ({retry_count} retries left)")
            time.sleep(2)  # 재시도 전 대기
            retry_count -= 1
    raise Exception("Failed to connect to the database after several attempts.")

 

  
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
    

    # 명령줄 인수 확인
    if len(sys.argv) < 3:
        # config.ini에서 읽은 값 사용
        host = websocket_host
        droneHost = drone_host
        receivePort = drone_receive_port
    else:
        # 명령줄에서 주어진 값 사용
        host = sys.argv[1]
        droneHost = sys.argv[2]
        receivePort = sys.argv[3]
        
    droneInfo = droneState()        
    print(droneHost)
    
   
    # Start the main function
    asyncio.ensure_future(run(droneInfo))

    # Runs the event loop until the program is canceled with e.g. CTRL-C
    asyncio.get_event_loop().run_forever()

