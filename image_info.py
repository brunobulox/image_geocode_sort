import os
import sys
from geopy.geocoders import Nominatim
from ImageMetaData import ImageMetaData

def get_image_data(directory_in_str):
    # returns data structure with all images from directory and their addresses
    geolocator = Nominatim()
    max_retries = 3
    location = ""

    if filename.endswith(".jpg") or filename.endswith(".JPG"):
        meta_data = ImageMetaData(directory_in_str + filename)
        latlng = meta_data.get_lat_lng()
        for i in range(max_retries):
            try:
                location = geolocator.reverse(latlng)
            except SomeException:
                print("retrying reverse geocoding")
                continue  # retrying
            else:
                break

        return filename, str(location)

    else:

        return None

directory_in_str = input("Enter the path of the directory: ")
directory = os.fsencode(directory_in_str)

assert os.path.exists(directory_in_str), "I did not find a directory at: , " + str(user_input)
print("I found the directory, reverse geocoding the images...")
address_list = []
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    data = get_image_data(directory_in_str)
    if data is not None:
        address_list += [data]
print(address_list)
