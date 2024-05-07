# -*- coding: utf-8 -*-
#!/usr/bin/env python3

from dronekit import connect, VehicleMode
import asyncio
import pymysql as db
import configparser
import time
from datetime import datetime
import sys
import os
import argparse

# 로깅 설정
import logging


logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

config = configparser.ConfigParser()
base_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(base_path, 'config.ini')
config.read(config_path)

db_config = config['database']
drone_config = config['drone']
websocket_config = config['websocket']

class DroneState:
    def __init__(self, name="lm_10001", receive_port="14540"):
        self.name = drone_config.get('drone_host', name)
        self.receive_port = drone_config.get('receive_port', receive_port)
        self.satellites_visible = 0
        self.battery_voltage = 0
        self.battery_level = 0
        self.groundspeed = 0
        self.lat = 0
        self.lon = 0
        self.alt = 0
        self.roll = 0
        self.pitch = 0
        self.yaw = 0

def getConnection():
    try:
        return db.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            db=db_config['dbname'],
            charset=db_config['charset'],
            autocommit=True
        )
    except db.Error as e:
        logger.error(f"Database connection failed: {e}")
        raise

async def update_drone_state(drone_state, drone, curs):
    while True:        
        sql = f"""INSERT INTO br_drone_state (
                    dl_id,
                    st_satelite_num,
                    st_bat_voltage,
                    st_bat_level,
                    st_speed,
                    st_x,
                    st_y,
                    st_z,
                    st_atitude,
                    st_roll,
                    st_pitch,
                    st_yaw,
                    st_head,
                    st_state,
                    st_mode,
                    st_time
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )"""
        params = (
            drone_state.name,
            drone.gps_0.satellites_visible,
            round(drone.battery.voltage, 2),
            drone.battery.level,
            round(drone.groundspeed, 1),
            drone.location.global_frame.lat,
            drone.location.global_frame.lon,
            drone.location.global_relative_frame.alt,
            drone.location.global_frame.alt,
            drone.attitude.roll * 50,
            drone.attitude.pitch * 50,
            drone.attitude.yaw * 50,
            drone.heading,
            drone.system_status.state,
            drone.mode.name,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        )


        try:
            #logger.info(f"params: {params}")  # 매개변수 로그 
            curs.execute(sql, params)
        except db.Error as e:
            logger.error(f"Failed to insert drone state: {e}")
            await asyncio.sleep(1)
            continue

        await asyncio.sleep(1)

async def main(args):
    conn = getConnection()
    curs = conn.cursor()

    drone_state = DroneState(name=args.drone_host, receive_port=args.receive_port)
    connection_string = f"udpin:0.0.0.0:{drone_state.receive_port}"
    logger.info(f'Connecting to vehicle on: {connection_string}')
    drone = connect(connection_string, wait_ready=True, baud=57600)

    asyncio.create_task(update_drone_state(drone_state, drone, curs))

    await asyncio.Event().wait()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Configure drone connection and database logging")
    parser.add_argument('--drone_host', default="lm_10001", help="Drone host ID")
    parser.add_argument('--receive_port', default="14540", help="UDP port for receiving data")
    args = parser.parse_args()

    asyncio.run(main(args))