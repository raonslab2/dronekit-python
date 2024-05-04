from __future__ import print_function
from PIL import Image
import imagehash   
from PIL.Image import Exif
from PIL.ExifTags import TAGS, GPSTAGS 
import json
from GPSPhoto import gpsphoto
import os
import cv2
import glob
import sys
from matplotlib.pyplot import spring
import time
from datetime import datetime
import pymysql as db

def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == "S" or ref =='W' :
        decimal_degrees = -decimal_degrees
    return decimal_degrees

def image_coordinates(image_path):

    with open(image_path, 'rb') as src:
        img = Image(src)
    if img.has_exif:
        try:
            img.gps_longitude
            coords = (decimal_coords(img.gps_latitude,
                      img.gps_latitude_ref),
                      decimal_coords(img.gps_longitude,
                      img.gps_longitude_ref))
        except AttributeError:
            print ('No Coordinates')
    else:
        print ('The Image has no EXIF information')
        
    return({"imageTakenTime":img.datetime_original, "geolocation_lat":coords[0],"geolocation_lng":coords[1]})

def get_exif(file_name) -> Exif:
    image: Image.Image = Image.open(file_name)
    return image.getexif()


def get_geo(exif):
    for key, value in TAGS.items():
        if value == "GPSInfo":
            break
    gps_info = exif.get_ifd(key)
    return {
        GPSTAGS.get(key, key): value
        for key, value in gps_info.items()
    }
    
def getConnection():
    
    try:     
        con = db.connect(host='13.209.238.3', 
                         user='mrdev', 
                         password='mrdev1',
                         db='sepm_db', 
                         charset='utf8',
                         local_infile = 1)
    except Exception as e:
        time.sleep(2)  
        con = getConnection() 
        
    return con 
	
if __name__ == "__main__":
    if len(sys.argv) < 1: 
        path = "D:\\girPj\\test1002\\*" 
    else: 
        path = path = "D:\\girPj\\test1002\\*" 
    
 
    file_list = glob.glob(path)  ## 폴더 안에 있는 모든 파일 출력
    
    conn = getConnection()
    curs = conn.cursor() 
    conn.ping(reconnect=True) # try reconnect
    
    for data in file_list:
        #print(data)
        exif = get_exif(data)
        geo = get_geo(exif)
        #print(geo)
        
        imgOpen = Image.open(data)
        meta_data = imgOpen._getexif()
        make_time = meta_data[36867] 
        #print(imgOpenResize)
        imageHash = imagehash.average_hash(imgOpen) 
        
        now = datetime.now()
        nowtime = now.strftime('%Y-%m-%d %H:%M:%S.%f');
        sql = "INSERT INTO br_way_hash"+ \
            "(ha_time, ha_hash, ha_lat, ha_lng, ha_alt, ha_writetime)" + \
            "VALUES('" + make_time + "', " + \
            " '"+str(imageHash)+"',"+ \
            " '"+str(gpsphoto.getGPSData(data)['Latitude'])+"',"+ \
            " '"+str(gpsphoto.getGPSData(data)['Longitude'])+"',"+ \
            " '"+str(gpsphoto.getGPSData(data)['Altitude'])+"',"+ \
            " '"+nowtime+"');"  
        try:
            print("sql:: "+sql)    
            result = curs.execute(sql) 
        except Exception as e:
            sleep(2) 
            conn = getConnection()
            # Connection 으로부터 Cursor 생성
            curs = conn.cursor()  
        finally:
            # resources closing 
            conn.commit()
            
        print(make_time,imageHash,gpsphoto.getGPSData(data)['Latitude'],gpsphoto.getGPSData(data)['Longitude'],gpsphoto.getGPSData(data)['Altitude'])
        

  
   
	 


