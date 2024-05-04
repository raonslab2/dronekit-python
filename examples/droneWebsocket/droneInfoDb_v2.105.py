import sys
import time
from datetime import datetime  
from pymavlink import mavutil

class GPSLogger:
    def __init__(self, port=14540):
        self.port = port
        self.connection_string = 'udp:localhost:{}'.format(self.port)
        self.master = mavutil.mavlink_connection(self.connection_string)
        self.master.wait_heartbeat()
        self.master.mav.request_data_stream_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_DATA_STREAM_POSITION, 1, 1
        )
        self.master.mav.request_data_stream_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_DATA_STREAM_EXTENDED_STATUS, 1, 1  
        )
        self.master.mav.request_data_stream_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_DATA_STREAM_EXTRA1, 1, 1  
        )
        self.master.mav.request_data_stream_send(
            self.master.target_system, self.master.target_component,
            mavutil.mavlink.MAV_DATA_STREAM_ALL, 1, 1  
        )

    def log_drone_state(self):
        print("Logging drone state (GPS, battery, ground speed, attitude, and satellites)...")
        try:
            while True:
                self.log_data()
                time.sleep(1)  # Wait for 1 second

        except KeyboardInterrupt:
            print("Logging stopped.")

    def log_data(self):
        msg_gps = self.recv_match('GLOBAL_POSITION_INT')
        lat, lon, alt, relative_alt = self.extract_gps_info(msg_gps)

        msg_battery = self.recv_match('SYS_STATUS')
        voltage, current, battery_remaining = self.extract_battery_info(msg_battery)

        msg_gps_raw = self.recv_match('GPS_RAW_INT')
        ground_speed = self.extract_ground_speed(msg_gps_raw)

        satellites_visible = msg_gps_raw.satellites_visible

        msg_attitude = self.recv_match('ATTITUDE')
        roll, pitch, yaw = self.extract_attitude(msg_attitude)

        msg_hud = self.recv_match('VFR_HUD')
        heading = msg_hud.heading

        msg_heartbeat = self.recv_match('HEARTBEAT')
        system_status, custom_mode = self.extract_heartbeat_info(msg_heartbeat)

        now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

        self.print_data(lat, lon, alt, relative_alt, voltage, current, battery_remaining, ground_speed, satellites_visible, roll, pitch, yaw, heading, system_status, custom_mode, now_time)

    def recv_match(self, msg_type):
        return self.master.recv_match(type=msg_type, blocking=True)

    def extract_gps_info(self, msg_gps):
        return msg_gps.lat / 1e7, msg_gps.lon / 1e7, msg_gps.alt / 1000.0, msg_gps.relative_alt / 1000.0

    def extract_battery_info(self, msg_battery):
        return msg_battery.voltage_battery / 1000.0, msg_battery.current_battery / 100.0, msg_battery.battery_remaining

    def extract_ground_speed(self, msg_gps_raw):
        return msg_gps_raw.vel / 100.0

    def extract_attitude(self, msg_attitude):
        return msg_attitude.roll, msg_attitude.pitch, msg_attitude.yaw

    def extract_heartbeat_info(self, msg_heartbeat):
        return msg_heartbeat.system_status, msg_heartbeat.custom_mode

    def print_data(self, lat, lon, alt, relative_alt, voltage, current, battery_remaining, ground_speed, satellites_visible, roll, pitch, yaw, heading, system_status, custom_mode, now_time):
        print("GPS - Latitude: {:.7f}, Longitude: {:.7f}, Altitude: {:.2f} meters, Relative Altitude: {:.2f} meters, Battery - Voltage: {:.2f} V, Current: {:.2f} A, Battery Remaining: {}%, Ground Speed: {:.2f} m/s, Satellites Visible: {}, Roll: {:.2f} , Pitch: {:.2f} , Yaw: {:.2f} , Heading: {:.2f}, System Status: {}, Custom Mode: {} , now_time: {}".format(
            lat, lon, alt, relative_alt, voltage, current, battery_remaining, ground_speed, satellites_visible, roll, pitch, yaw, heading, system_status, custom_mode, now_time
        ))
        
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
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 14540
    logger = GPSLogger(port)
    logger.log_drone_state()
