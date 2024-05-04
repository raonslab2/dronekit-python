from __future__ import print_function
from PIL import Image
import imagehash   
from PIL.Image import Exif
from PIL.ExifTags import TAGS, GPSTAGS 
import json
from GPSPhoto import gpsphoto


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

localPath = 'D://girPj//test1002//';
fileName = "";
totalCnt = 49
for i in range(totalCnt):
	ti = i+1
	if(i<9): 
		fileName = "DJI_000"+str(ti)+".JPG"
	elif i>9 and i<99:
		fileName = "DJI_00"+str(ti)+".JPG" 
	globals()['filename'+str(i+1)] = localPath+fileName
 
  
	
if __name__ == "__main__":
    exif1 = get_exif(filename1)
    geo1 = get_geo(exif1)
    
    exif2 = get_exif(filename2)
    geo2 = get_geo(exif2)
    
    exif3 = get_exif(filename3)
    geo3 = get_geo(exif3)
    
    exif4 = get_exif(filename4)
    geo4 = get_geo(exif4)
    
    print(geo1)
    #print("GPSLatitude:::"+str(geo1.get("GPSLatitude", "")))
    #print("GPSLongitude:::"+str(geo1.get("GPSLongitude", "")))
    
    test1 = Image.open(filename1)
    test2 = Image.open(filename2)
    test3 = Image.open(filename3)
    test4 = Image.open(filename4) 
       
    
    imageHash1 = imagehash.average_hash(test1)
    imageHash2 = imagehash.average_hash(test2)
    imageHash3 = imagehash.average_hash(test3)
    imageHash4 = imagehash.average_hash(test4)
    
    print(gpsphoto.getGPSData(filename1))
    print(gpsphoto.getGPSData(filename1)['Latitude'])

   
    print(imageHash1,gpsphoto.getGPSData(filename1)['Latitude'],gpsphoto.getGPSData(filename1)['Longitude'])
    print(imageHash2,gpsphoto.getGPSData(filename2)['Latitude'],gpsphoto.getGPSData(filename2)['Longitude'])
    print(imageHash3,gpsphoto.getGPSData(filename3)['Latitude'],gpsphoto.getGPSData(filename3)['Longitude'])
    print(imageHash4,gpsphoto.getGPSData(filename4)['Latitude'],gpsphoto.getGPSData(filename4)['Longitude'])
  
    print(imageHash1 - imageHash1)
    print(imageHash1 - imageHash2)
    print(imageHash1 - imageHash3)
    print(imageHash1 - imageHash4)
   
  
   
	 


