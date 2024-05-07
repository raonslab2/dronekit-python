from pymavlink import mavutil

 
import keyboard  
import time  

val = [
    # x, y, z, r
    # x: 드론의 pitch와 관련된 값 전후 이동과 관련된 값이다 
    # y: 드론의 roll과 관련된 값 좌우 이동과 관련된 값이다.
    # z: 드론의 추력과 관련된 값 상하 이동과 관련된 값이다.
    # r: 드론의 Yaw와 관련된 값 드론의 시계/반시계 방향 회전과 관련된 값이다.
    [0, 0, 0, 0], #land 0
    [250, 0, 500, 0], #front 1
    [-250, 0, 500, 0], #back 2
    [0, 250, 500, 0], #right 3
    [0, -250, 500, 0], #left 4
    [0, 0, 1000, 0], # up 5
    [0, 0, 250, 0], # down 6
    [0, 0, 500, 0] # hold 7
]
# master.mav.manual_control_send을 통해서 보내는 값.
# 이를 이용해서 드론을 제어할 수 있다.

master = mavutil.mavlink_connection('udpin:0.0.0.0:14540')
 
master.wait_heartbeat()
 

print('Drone is connected!')
while 1:
    if keyboard.is_pressed('d'):
        print('Start!')
        master.mav.command_long_send(master.target_system, master.target_component,mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)
 
        print("Waiting for the vehicle to arm")
        master.motors_armed_wait()
 
        print('Armed!')
    if keyboard.is_pressed('f'):
        print('stop!')
    master.mav.command_long_send(master.target_system,master.target_component,mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 0, 0, 0, 0, 0, 0, 0)
 
    master.motors_disarmed_wait()
    if keyboard.is_pressed('left'):
        print('Press Left!')
        master.mav.maual_control_send(master.target_system, val[4][0], val[4][1], val[4][2], val[4][3])
    if keyboard.is_pressed('right'):
        print('Press RIght!')
        master.mav.manual_control_send(mater.target_system, val[3][0], val[3][1], val[3][2], val[3][3])
    if keyboard.is_pressed('up'):
        print('Press front!')
        master.mav.manual_control_send(master.target_system, val[1][0], val[1][1], val[1][2], val[1][3])
    if keyboard.is_pressed('down'):
        print('Press back!')
        master.mav.manual_control_send(master.target_system, val[2][0], val[2][1], val[2][2], val[2][3])
    if keyboard.is_pressed('space'):
        print('Press space bar!')
        master.mav.manual_control_send(master.target_system, val[6][0], val[6][1], val[6][2], val[6][3])
    if keyboard.is_pressed('ctrl'):
        print('Press Control!')
        master.mav.manual_control_send(master.target_system, val[7][0], val[7][1], val[7][2], val[7][3])
    time.sleep(0.085)