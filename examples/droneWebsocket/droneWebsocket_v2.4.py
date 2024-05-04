#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import asyncio
import sys
import json
import threading
import datetime
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative, Command
from pymavlink import mavutil
import websocket  # websocket 모듈 추가

class DroneController:
    def __init__(self, host, drone_host, receive_port):
        self.host = host
        self.drone_host = drone_host
        self.receive_port = receive_port
        self.vehicle = None

    def connect_vehicle(self):
        connection_string = "udpin:0.0.0.0:" + self.receive_port
        print('Connecting to vehicle on:', connection_string)
        self.vehicle = connect(connection_string, wait_ready=False, baud=57600)
        self.vehicle.wait_ready(True, raise_exception=False)
        print('Connected to vehicle')

    def start_websocket(self):
        print("host:", self.host)
        print("droneHost:", self.drone_host)
        ws = websocket.WebSocketApp(self.host,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        ws.on_open = self.on_open
        ws.run_forever()

    def on_message(self, ws, message):
        print("on_message:", message)
        rec_data = json.loads(message)
        dl_action = rec_data["dlAction"]
        dl_name = rec_data["dlName"]

        if dl_action == "arm":
            self.drone_arm()
        elif dl_action == "disarm":
            self.drone_disarm()
        elif dl_action == "reboot":
            self.drone_reboot()
        elif dl_action == "takeoff":
            self.drone_takeoff()
        elif dl_action == "land":
            self.drone_land()
        elif dl_action == "rtl":
            self.drone_rtl()
        elif dl_action == "missiondown":
            self.drone_mission_down(dl_name)
        elif dl_action == "waypoint":
            dl_waypoint = rec_data["dlWayPoint"]
            self.drone_waypoint(dl_waypoint)
        elif dl_action == "auto":
            self.drone_auto()
        elif dl_action == "goto":
            dl_option = rec_data["dlOption"]
            self.drone_goto(dl_option)
        else:
            print("Unknown action")

    def drone_arm(self):
        print("Arm motors")
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True

    def drone_disarm(self):
        print("Disarm motors")
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.disarm()

    def drone_reboot(self):
        print("Reboot drone")
        self.vehicle.reboot()

    def drone_takeoff(self):
        print("Taking off!")
        self.arm_and_takeoff(10)

    def arm_and_takeoff(self, target_altitude):
        print("Basic pre-arm checks")
        while not self.vehicle.is_armable:
            print("Waiting for vehicle to initialise...")
            time.sleep(1)

        print("Arming motors")
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True

        print("Taking off!")
        self.vehicle.simple_takeoff(target_altitude)

    def drone_land(self):
        print("Landing")
        self.vehicle.mode = VehicleMode("LAND")

    def drone_rtl(self):
        print("Returning to Launch")
        self.vehicle.mode = VehicleMode("RTL")

    def drone_mission_down(self, drone_name):
        now = datetime.datetime.now()
        now_date = now.strftime('%Y_%m_%d')
        now_time = now.strftime('%H%M%S')
        file_name = drone_name + "_" + now_date + "_" + now_time + ".txt"
        print("Drone Mission Download")
        self.save_mission(file_name)

    def save_mission(self, file_name):
        print("\nSaving mission from Vehicle to file:", file_name)
        missionlist = self.download_mission()
        output = 'QGC WPL 110\n'
        home = self.vehicle.home_location
        output += "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
        0, 1, 0, 16, 0, 0, 0, 0, home.lat, home.lon, home.alt, 1)
        for cmd in missionlist:
            commandline = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
            cmd.seq, cmd.current, cmd.frame, cmd.command, cmd.param1, cmd.param2, cmd.param3, cmd.param4, cmd.x, cmd.y,
            cmd.z, cmd.autocontinue)
            output += commandline
        with open(file_name, 'w') as file_:
            file_.write(output)

    def download_mission(self):
        print("Download mission from vehicle")
        missionlist = []
        cmds = self.vehicle.commands
        cmds.download()
        cmds.wait_ready()
        for cmd in cmds:
            missionlist.append(cmd)
        return missionlist

    def on_open(self, ws):
        json_object_drone = {"DATA_GUBUN": "DRONE", "DATA_REQUEST": "OPEN", "DATA_DRONE_ID": self.drone_host}
        json_string_drone = json.dumps(json_object_drone, indent=2)
        ws.send(json_string_drone)
        t = threading.Thread(target=self.thread_run, args=(ws, 1, 10000000, json_string_drone))
        t.start()

    def thread_run(self, ws, low, high, json_string_drone):
        for i in range(low, high):
            i = i + 1
            time.sleep(1)

    def on_error(self, ws, error):
        print("Retry:", time.ctime())
        time.sleep(2)
        self.start_websocket()

    def on_close(self, ws, close_status_code, close_msg):
        print("### closed ###")
        print("Retry:", time.ctime())
        time.sleep(2)
        self.start_websocket()

    async def drone_auto(self):
        print("Auto mode")
        self.vehicle.mode = VehicleMode("AUTO")

    async def drone_waypoint(self, dl_waypoint):
        print("Waypoint mode")
        cmds = self.vehicle.commands
        print("Clearing existing commands")
        cmds.clear()

        actions = dl_waypoint["actions"]
        mission_detail = dl_waypoint["missionDetail"]

        cmds.add(Command(0, 0, 0,
                         int(mission_detail[0][0]["_waypoinframe"]),  # frame
                         int(mission_detail[0][0]["_waypoinCommand"]),  # command
                         0,
                         0,
                         0,
                         0,
                         0,
                         0,
                         dl_waypoint["home"]["coordinate"][0],
                         dl_waypoint["home"]["coordinate"][1],
                         0))

        ssi = 0
        for tm_waypoint in actions:
            _waypoint_paran1 = mission_detail[ssi + 1][0]["_waypointParan1"] if mission_detail[ssi + 1][0][
                                                                                     "_waypointParan1"] else 0
            _waypoint_paran2 = mission_detail[ssi + 1][0]["_waypointParan2"] if mission_detail[ssi + 1][0][
                                                                                     "_waypointParan2"] else 0
            _waypoint_paran3 = mission_detail[ssi + 1][0]["_waypointParan3"] if mission_detail[ssi + 1][0][
                                                                                     "_waypointParan3"] else 0
            _waypoint_paran4 = mission_detail[ssi + 1][0]["_waypointParan4"] if mission_detail[ssi + 1][0][
                                                                                     "_waypointParan4"] else 0

            cmds.add(Command(
                0,  # target_system
                0,  # target_component
                0,  # seq
                int(mission_detail[ssi + 1][0]["_waypoinframe"]),  # frame
                int(mission_detail[ssi + 1][0]["_waypoinCommand"]),  # command
                0,  # current
                0,  # autocontinue
                int(_waypoint_paran1),  # param1
                int(_waypoint_paran2),  # param2
                int(_waypoint_paran3),  # param3
                int(_waypoint_paran4),  # param4
                tm_waypoint["coordinate"][0],  # lat x
                tm_waypoint["coordinate"][1],  # lon y
                tm_waypoint["elevation"]  # z
            ))
            ssi = ssi + 1

        print("Upload new commands to vehicle")
        cmds.upload()

    async def drone_goto(self, dl_option):
        print("Go to mode")
        st = dl_option.split('|')
        self.vehicle.mode = VehicleMode("GUIDED")
        point1 = LocationGlobalRelative(float(st[1]), float(st[0]), float(st[2]))
        tm_groundspeed = float(st[3])
        self.vehicle.simple_goto(point1, groundspeed=tm_groundspeed)


if __name__ == "__main__":
    websocket.enableTrace(True)
    if len(sys.argv) < 4:
        host = "ws://13.209.238.3:5010/websocket"
        drone_host = "lm_10001"
        receive_port = "14541"
    else:
        host = sys.argv[1]
        drone_host = sys.argv[2]
        receive_port = sys.argv[3]

    controller = DroneController(host, drone_host, receive_port)
    controller.connect_vehicle()
    controller.start_websocket()
