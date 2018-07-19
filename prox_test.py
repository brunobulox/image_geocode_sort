from geopy.geocoders import Nominatim
import os
import csv
from geopy.distance import geodesic

from ImageMetaData import ImageMetaData

directory = '/home/mark/pytest/pics/'
gps_list = []
filename_lst = []
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.endswith(".jpg") or filename.endswith(".JPG"):
        meta_data = ImageMetaData(directory + filename)
        latlng = meta_data.get_lat_lng()
        filename_lst += [filename]
        gps_list += [latlng]



geolocator = Nominatim()
max_retries = 3
addresses = []
address_gps = []
with open("/home/mark/pytest/property_list.csv",'r') as fp:
    reader = csv.reader(fp)
    #thefile = open('/home/mark/pytest/addy_test.txt', 'w')
    for line in reader:
        print(line)
        #addresses += line
        for i in range(max_retries):
            try:
                location = geolocator.geocode(line)
            except:
                print("retrying geocoding")
                continue  # retrying
            else:
                break
        if location is not None:
            address_gps += location

    #print (address_gps)
    fp.close()
#ofile = open("/home/mark/pytest/property_list_gps.csv", 'w')
#writer = csv.writer(ofile,delimiter=',', quotechar="'",quoting=csv.QUOTE_NONE, escapechar='\\' )
for addy in address_gps:
    #writer.writerow("%s\n\n" % str(addy))
    addy = addy.split(addy, "\n")
    print (addy)
#ofile.close()

    #thefile.write("%s\n\n" % address_gps)
    #thefile.close()
#print('files decoded; ' + str(filename_lst))
#print('gps found in files' + str(gps_list))





