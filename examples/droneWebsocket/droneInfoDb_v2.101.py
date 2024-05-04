# -*- coding: utf-8 -*-
#!/usr/bin/env python3

from __future__ import print_function
import json
import asyncio
import time
from datetime import datetime
import sys
import pymysql as db
import logging
from dronekit import connect
import websocket

def read_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# 로깅 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # DEBUG 레벨 이상의 모든 로그를 출력합니다.

# 콘솔 출력용 핸들러 생성
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)  # DEBUG 레벨 이상의 모든 로그를 출력합니다.

# 파일 출력용 핸들러 생성
file_handler = logging.FileHandler('drone_info.log')
file_handler.setLevel(logging.ERROR)  # ERROR 레벨 이상의 로그를 파일에 기록합니다.

# 로그 포매터 설정
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 핸들러를 로거에 추가
logger.addHandler(console_handler)
logger.addHandler(file_handler)

class DroneState:
    def __init__(self):
        self.name = "lm_10001"
        self.receive_port = "14540"
        self.sat_num = 0
        self.roll = "0"
        self.pitch = "0"
        self.yaw = "0"
        self.lat_deg = ""
        self.lon_deg = ""
        self.abs_alt = ""
        self.rel_alt = ""

async def run(drone_info, receive_port):
    connection_string = "udpin:0.0.0.0:" + receive_port
    logger.info('Connecting to vehicle on: %s', connection_string)
    drone = connect(connection_string, wait_ready=False, baud=57600)
    drone.wait_ready(True, raise_exception=False)
    logger.info("Autopilot Firmware version: %s", drone.version)

    mysql_connector = MySQLConnector(host='13.209.238.3', user='mrdev', password='mrdev1', database='sepm_db')
    mysql_connector.connect()

    await print_serversend(drone_info, drone, mysql_connector)

async def print_serversend(drone_info, drone, connector):
    running = True
    tm_name = drone_info.name

    while running:
        now = datetime.now()
        now_time = now.strftime('%Y-%m-%d %H:%M:%S.%f')
        sql = f"INSERT INTO br_drone_state (dl_id, st_status, st_satelite_num, st_bat_voltage, st_bat_level, st_speed, st_x, st_y, st_z, st_atitude, st_roll, st_pitch, st_yaw, st_head, st_state, st_mode, st_time) VALUES ('{drone_host}', 1, '{drone.gps_0.satellites_visible}', '{round(drone.battery.voltage, 2)}', '{drone.battery.level}', '{round(drone.groundspeed, 1)}', '{drone.location.global_frame.lat}', '{drone.location.global_frame.lon}', '{drone.location.global_relative_frame.alt}', '{drone.location.global_frame.alt}', '{drone.attitude.roll*50}', '{drone.attitude.pitch*50}', '{drone.attitude.yaw*50}', '{drone.heading}', '{drone.system_status.state}', '{drone.mode.name}', '{now_time}')"
        try:
            logger.debug("Executing SQL query: %s", sql)
            connector.execute_query(sql)
        except db.Error as e:
            logger.error("Failed to execute SQL query: %s", e, exc_info=True)  # 예외 정보를 로깅에 추가
            await asyncio.sleep(2)
            logger.info("Attempting to reconnect to the database...")
            connector.close()
            connector.connect()
        await asyncio.sleep(1)

class MySQLConnector:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        while True:
            try:
                self.connection = db.connect(host=self.host, user=self.user, password=self.password, database=self.database, charset='utf8', local_infile=1)
                break
            except Exception as e:
                time.sleep(2)
                logger.error("Failed to connect to the database: %s", e, exc_info=True)  # 연결 실패 시 로그에 기록합니다.

    def close(self):
        if self.connection:
            self.connection.close()

    def execute_query(self, query):
        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            cursor.close()

if __name__ == "__main__":
    websocket.enableTrace(True)
    
    if len(sys.argv) < 3:
        #host = "ws://13.209.238.3:5010/websocket"
        host = "ws://13.209.238.3:5010/websocket"
        #host = "ws://127.0.0.1:5010/websocket"
        drone_host = "lm_10001"; 
        receive_port = "14540"; 
    else:
        host = sys.argv[1]
        drone_host = sys.argv[2]
        receive_port = sys.argv[3]
    

    drone_info = DroneState()   
    
    db_host = '13.209.238.3'
    db_user = 'mrdev'
    db_password = 'mrdev1'
    db_database = 'sepm_db'

    asyncio.run(run(drone_info, receive_port))
