import sys
import urllib
import json

level = 18
p2level = pow(2, level)
width = height = 256 * p2level
degreePerTileX = 360.0/p2level
degreePerTileY = degreePerTileX/2

param = urllib.urlencode({"key":"ArSkGTLs-eC_9nbM84_EJ-tjISwN7rcDT0Vvw1jQhccWLoAGJYE4jX2AapF9aBKa"})

print "Please input first latitude (number only)"

lat1 = sys.stdin.readline()[:-1]

print "Please input first longitude"

lon1 = sys.stdin.readline()[:-1]

print "Please input second latitude (number only)"

lat2 = sys.stdin.readline()[:-1]

print "Please input second longitude (number only)"

lon2 = sys.stdin.readline()[:-1]

firstTileX = int((float(lon1)+180)/degreePerTileX)
lastTileX = int((float(lon2)+180)/degreePerTileX)
firstTileY = int((float(lat1)+90)/degreePerTileY)
lastTileY = int((float(lat2)+90)/degreePerTileY)

count = 0
print lastTileX, firstTileX, lastTileY, firstTileY
total = (lastTileX-firstTileX+1)*(lastTileY-firstTileY+1)

for i in xrange(firstTileX, lastTileX+1):
    # decide the left and right bound
    segLon1 = None
    segLon2 = None
    if i == firstTileX:
        segLon1 = float(lon1)
    else:
        segLon1 = i*degreePerTileX-180
    if i == lastTileX:
        segLon2 = float(lon2)
    else:
        segLon2 = (i+1)*degreePerTileX-180
    
    segWidth = None
    if i == firstTileX or i == lastTileX:
        segWidth = int((segLon2-segLon1)*width/360)
    else:
        segWidth = 256
    for j in xrange(firstTileY, lastTileY+1):
        # decide the top and bottom bound
        segLat1 = None
        segLat2 = None
        if j == firstTileY:
            segLat1 = float(lat1)
        else:
            segLat1 = j*degreePerTileY-90
        if j == lastTileY:
            segLat2 = float(lat2)
        else:
            segLat2 = (j+1)*degreePerTileY-90

        # decide the size of interest
        segHeight = None
        if j == firstTileY or j == lastTileY:
            segHeight = int((segLat2-segLat1)*height/180)
        else:
            segHeight = 256

        centerLat = (segLat1+segLat2)/2
        centerLon = (segLon1+segLon2)/2
        # request the current tile from Bing map
        # request = "http://dev.virtualearth.net/REST/v1/Imagery/Map/Aerial?mapSize=%d,%d&mapArea=%f,%f,%f,%f&%s" % (segWidth, segHeight, segLat1, segLon1, segLat2, segLon2, param)
        request = "http://dev.virtualearth.net/REST/v1/Imagery/Map/Aerial/%f,%f/%d?mapSize=%d,%d&%s" % (centerLat, centerLon, level, segWidth, segHeight, param)
        print request
        url = urllib.urlopen(request)

        result = url.read()
        count += 1

        if url.getcode() != 200:
            obj = json.loads(result)
            errors = obj["errorDetails"]
            for string in errors:
                print string
        else:
            file = open("result%d.jpeg" % count,"wb")
            file.write(result)
            print "%d/%d" % (count, total)
            file.close()
