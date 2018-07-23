import os
import csv
import time
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from shutil import copyfile
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

property_list_file = "/home/mark/pytest/property_list_entire.csv"
#format is street address, city
img_directory = '/home/mark/Pictures/Drone_shots/07-08-18/'

class ImageMetaData(object):
    """
    Extract the exif data from any image. Data includes GPS coordinates,
    Focal Length, Manufacture, and more.
    """
    exif_data = None
    image = None

    def __init__(self, img_path):
        self.image = Image.open(img_path)
        self.get_exif_data()
        super(ImageMetaData, self).__init__()

    def get_exif_data(self):
        """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
        exif_data = {}
        info = self.image._getexif()
        if info:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    gps_data = {}
                    for t in value:
                        sub_decoded = GPSTAGS.get(t, t)
                        gps_data[sub_decoded] = value[t]

                    exif_data[decoded] = gps_data
                else:
                    exif_data[decoded] = value
        self.exif_data = exif_data
        return exif_data

    def get_if_exist(self, data, key):
        if key in data:
            return data[key]
        return None

    def convert_to_degress(self, value):
        """Helper function to convert the GPS coordinates
        stored in the EXIF to degress in float format"""
        d0 = value[0][0]
        d1 = value[0][1]
        d = float(d0) / float(d1)

        m0 = value[1][0]
        m1 = value[1][1]
        m = float(m0) / float(m1)

        s0 = value[2][0]
        s1 = value[2][1]
        s = float(s0) / float(s1)

        return d + (m / 60.0) + (s / 3600.0)

    def get_lat_lng(self):
        """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)"""
        lat = None
        lng = None
        exif_data = self.get_exif_data()
        if "GPSInfo" in exif_data:
            gps_info = exif_data["GPSInfo"]
            gps_latitude = self.get_if_exist(gps_info, "GPSLatitude")
            gps_latitude_ref = self.get_if_exist(gps_info, 'GPSLatitudeRef')
            gps_longitude = self.get_if_exist(gps_info, 'GPSLongitude')
            gps_longitude_ref = self.get_if_exist(gps_info, 'GPSLongitudeRef')
            if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
                lat = self.convert_to_degress(gps_latitude)
                if gps_latitude_ref != "N":
                    lat = 0 - lat
                lng = self.convert_to_degress(gps_longitude)
                if gps_longitude_ref != "E":
                    lng = 0 - lng
        return lat, lng


def get_images_gps(img_dir):
    start = time.time()
    img_gps_lst = []
    for file in os.listdir(img_dir):
        filename = os.fsdecode(file)
        if filename.endswith(".jpg") or filename.endswith(".JPG"):
            meta_data = ImageMetaData(img_dir + filename)
            latlng = meta_data.get_lat_lng()
            tpl = (filename, latlng)
            img_gps_lst.append(tpl)
    end = time.time()
    elapsed = end - start
    print("Got GPS from images in " + str(elapsed) + " seconds")
    return img_gps_lst

def get_gps_from_addy_list(filename):
    geolocator = Nominatim()
    max_retries = 3
    address_gps = []
    location = None
    start = time.time()
    print("Looking up GPS for property list addresses...")
    with open(filename,'r') as fp:
        reader = csv.reader(fp)
        for line in reader:
            for i in range(max_retries):
                try:
                    location = geolocator.geocode(line, addressdetails=False)
                except:
                    print("retrying geocoding for " + str(line))
                    continue  # retrying
                else:
                    break
            if location is not None:
                loc_addy = str(location.address)
                loc_addy.replace("United States of America","")
                location = (loc_addy, (location.latitude, location.longitude))
                address_gps.append(location)
    fp.close()
    end = time.time()
    elapsed = end - start
    print("Geocoded address list in " + str(elapsed) + " seconds")
    return address_gps

def create_prop_dir(root_dir, sub_dir, prop_dir):
    if os.path.exists(root_dir):
        if not os.path.exists(root_dir + sub_dir):
            os.mkdir(root_dir + sub_dir)
        if not os.path.exists(root_dir + sub_dir + prop_dir):
            os.mkdir(root_dir + sub_dir + prop_dir)
        path = root_dir + sub_dir + prop_dir
        return (path)


distance_threshold = .09 #475 feet
gps_list = get_images_gps(img_directory)
unmatched_images = []
property_gps = get_gps_from_addy_list(property_list_file)

for prop in property_gps:
    for gps in gps_list:
        miles = geodesic(prop[1], gps[1]).miles
        if miles < distance_threshold:
            path = create_prop_dir(img_directory,"geo_sorted_images/", str(prop[0]))
            copyfile(img_directory + str(gps[0]), path + "/" + str(gps[0]))
            while (True):
                try:
                    unmatched_images.remove(gps[0])
                    print("removed " + gps[0])
                except ValueError:
                    break
        else:
            unmatched_images.append(gps[0])

unmatched_images = list(set(unmatched_images))

print(unmatched_images)
