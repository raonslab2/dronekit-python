import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import pandas as pd

def get_exif_data(image_path):
    """이미지로부터 EXIF 데이터를 추출합니다."""
    image = Image.open(image_path)
    exif_data = image._getexif()
    return {
        TAGS[key]: exif_data[key]
        for key in exif_data.keys() if key in TAGS
    } if exif_data else {}

def get_gps_data(exif_data):
    """EXIF 데이터로부터 GPS 정보를 추출합니다."""
    gps_info = exif_data.get("GPSInfo", {})
    gps_data = {
        GPSTAGS.get(key, key): gps_info[key]
        for key in gps_info.keys() if key in GPSTAGS
    }
    return gps_data

def extract_gps_coordinates(gps_data):
    """GPS 데이터로부터 위도와 경도를 추출합니다."""
    def convert_to_degress(value):
        """GPS 좌표를 도로 변환합니다."""
        d, m, s = value
        return d + (m / 60.0) + (s / 3600.0)

    lat = gps_data.get('GPSLatitude')
    lat_ref = gps_data.get('GPSLatitudeRef')
    lon = gps_data.get('GPSLongitude')
    lon_ref = gps_data.get('GPSLongitudeRef')

    if lat and lon and lat_ref and lon_ref:
        lat = convert_to_degress(lat)
        if lat_ref != "N":
            lat = -lat
        lon = convert_to_degress(lon)
        if lon_ref != "E":
            lon = -lon
        return lat, lon
    return None

def main(directory):
    """디렉토리의 모든 이미지를 스캔하고 GCP 데이터를 생성합니다."""
    gcp_data = []
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(directory, filename)
            exif_data = get_exif_data(image_path)
            gps_data = get_gps_data(exif_data)
            coords = extract_gps_coordinates(gps_data)
            if coords:
                gcp_data.append([filename, *coords])

    # 결과를 CSV 파일로 저장
    df = pd.DataFrame(gcp_data, columns=['Image', 'Latitude', 'Longitude'])
    df.to_csv('1test.csv', index=False)
    print("GCP 데이터가 gcp_data.csv 파일에 저장되었습니다.")

if __name__ == "__main__":
    directory = input("./test1/DJI_0002.JPG")
    main(directory)
