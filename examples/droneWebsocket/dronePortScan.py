# -*- coding: utf-8 -*-
#!/usr/bin/env python3 

import socket

port = 14539
addr =("127.0.0.1",port)

socket.setdefaulttimeout(2)

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    try :
        s.sendto("data".encode(),addr)
        s.recvfrom(1024)
        print("{}udp port is opend".format(port))

    except Exception as e:
        print(e)
        if str(e) == "timed out" :
            print("{} udp is opened".format(port))
        else :
            print("{} udp is closed".format(port))