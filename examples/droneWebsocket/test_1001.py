from pymavlink import mavutil

# 드론이 송신하는 IP 주소 및 포트
DRONE_IP = '0.0.0.0'  # 모든 IP에서 들어오는 메시지를 수신하려면 '0.0.0.0'을 사용합니다.
DRONE_PORT = 14542  # 드론이 사용하는 UDP 포트

# UDP 소켓을 통해 드론으로부터 메시지를 수신합니다.
master = mavutil.mavlink_connection('udp:{0}:{1}'.format(DRONE_IP, DRONE_PORT))

# 드론으로부터 메시지를 읽고 출력하는 루프를 시작합니다.
while True:
    try:
        # 메시지를 한 줄씩 읽습니다.
        msg = master.recv_match()
        
        if msg:
            # GLOBAL_POSITION_INT 메시지일 때 GPS 정보를 출력합니다.
            if msg.get_type() == 'GLOBAL_POSITION_INT':
                print("Latitude:", msg.lat / 1e7)  # 위도
                print("Longitude:", msg.lon / 1e7)  # 경도
                print("Altitude:", msg.alt / 1e3)  # 고도
                print("Relative Altitude:", msg.relative_alt / 1e3)  # 상대 고도
                print("Velocity (m/s):", msg.vx / 100.0)  # x 속도
                print("Velocity (m/s):", msg.vy / 100.0)  # y 속도
                print("Velocity (m/s):", msg.vz / 100.0)  # z 속도
                print("Heading:", msg.hdg / 100.0)  # 방향
                print("--------------------------------------------------")
                
    except Exception as e:
        print(e)
