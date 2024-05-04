# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import asyncio 
import websocket 
import time
import sys
import json 
from mavsdk import System


class droneMission:
    
    """
    droneMission Class
    """
    def __init__(self, drone):
        self._drone = drone 
        
    def setMission(self):
        print(1)
 