import sys
from droneWebsocketmodule import DroneController

if __name__ == "__main__":
    # 웹소켓 호스트, 드론 호스트, 포트 설정
    if len(sys.argv) < 4:
        host = "ws://13.209.238.3:5010/websocket"
        drone_host = "lm_10001"
        receive_port = "14541"
    else:
        host = sys.argv[1]
        drone_host = sys.argv[2]
        receive_port = sys.argv[3]

    # 드론 컨트롤러 초기화 및 연결
    controller = DroneController(host, drone_host, receive_port)
    controller.connect_vehicle()
    controller.start_websocket()
