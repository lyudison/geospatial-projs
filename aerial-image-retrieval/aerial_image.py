import sys
import urllib
import json
import math
from PIL import Image
import io

level = 23

param = urllib.urlencode({"key":"ArSkGTLs-eC_9nbM84_EJ-tjISwN7rcDT0Vvw1jQhccWLoAGJYE4jX2AapF9aBKa"})

def latlon2pixelxy(lat,lon,mapSize):
    x=(lon+180)/360
    temp=math.sin(lat*math.pi/180)
    y=0.5-math.log((1+temp)/(1-temp))/(4*math.pi)
    pixelx = int(x*mapSize+0.5)
    pixely = int(y*mapSize+0.5)
    return [pixelx, pixely]

def pixelxy2tilexy(xy):
    x = xy[0]
    y = xy[1]
    tilex=int(x/256) 
    tiley=int(y/256)
    return [tilex, tiley]

def tilexytoquad(tx,ty):
	quad = ""
	for i in xrange(level,0, -1):
		digit='0'
		mask = (1 << (i - 1)) & 0xffffffff # python int is not size-fixed
		
		if (tx&mask) !=0:
			digit = chr(ord(digit) + 1)
		if (ty&mask) !=0:
			digit = chr(ord(digit) + 1)
			digit = chr(ord(digit) + 1)
		quad += digit
	return quad

def getTileQuadsInBound(tile1X, tile1Y, tile2X, tile2Y, p2level):
	tiles=[]
	for r in xrange(tile1Y, tile2Y+1):
                row = []
		for c in xrange(tile1X, tile2X+1):
                        c %= p2level
			row.append(tilexytoquad(c,r))
		tiles.append(row)
	return tiles  

def isSameImage(im1, im2):
    if im1.size != im2.size:
        return False
    for i in xrange(0, im1.height):
        for j in xrange(0, im1.width):
            if im1.getpixel((j, i)) != im2.getpixel((j, i)):
                return False
    return True

# MAIN #
print "Please input first latitude (number only)"
lat1 = sys.stdin.readline()[:-1]

print "Please input first longitude"
lon1 = sys.stdin.readline()[:-1]

print "Please input second latitude (number only)"
lat2 = sys.stdin.readline()[:-1]

print "Please input second longitude (number only)"
lon2 = sys.stdin.readline()[:-1]

lat1=float(lat1)
lat2=float(lat2)
lon1=float(lon1)
lon2=float(lon2)
lat1= min(max(lat1,-85.05112878),85.05112878)
lat2= min(max(lat2,-85.05112878),85.05112878)
lon1= min(max(lon1,-180),180)
lon2= min(max(lon2,-180),180)

if lat1 >= lat2:
    print 'invalid latitude and longitude. '
    exit()

tile1xy = None
tile1 = None 
while level > 0:
    mapsize= 256*2**level
    tile1xy = latlon2pixelxy(lat1, lon1, mapsize)
    tile1 = pixelxy2tilexy(tile1xy)
    testQuad = tilexytoquad(tile1[0], tile1[1])
    request = "http://h0.ortho.tiles.virtualearth.net/tiles/h%s.jpeg?g=131&%s" % (testQuad, param)
    url = urllib.urlopen(request)
    testImage = Image.open(io.BytesIO(url.read()))
    invalidImage = Image.open('invalid.jpeg')
    if isSameImage(testImage, invalidImage):
        print 'forbidden level %d in the bounding area. ' % level
    else:
        break
    level -= 1

if level == 0:
    print 'no available level in the bounding area. '
    exit()

tile2xy = latlon2pixelxy(lat2, lon2, mapsize)
tile2 = pixelxy2tilexy(tile2xy)

p2level = 2**level

if lon1 > lon2:
    tile2xy[0] += p2level * 256
    tile2[0] += p2level

print "calculating all the quads in bounding box..."
quads = getTileQuadsInBound(tile1[0], tile2[1], tile2[0], tile1[1], p2level)
print "finished calculation. "

if len(quads) == 0:
    print "no bounding area."
    exit()

print "downloading and stitching all the tiles..."
imageHeight = len(quads)
imageWidth = len(quads[0])
total = imageHeight * imageWidth
count = 0
image = Image.new('RGB', (imageWidth*256, imageHeight*256))
for r in xrange(0, len(quads)):
    for c in xrange(0, len(quads[0])):
        quad = quads[r][c]
        request = "http://h0.ortho.tiles.virtualearth.net/tiles/h%s.jpeg?g=131&%s" % (quad, param)
        url = urllib.urlopen(request)
        result = url.read()
        count += 1
        if url.getcode() != 200:
            obj = json.loads(result)
            errors = obj["errorDetails"]
            for string in errors:
                print string
        else:
            subImage = Image.open(io.BytesIO(result))
            image.paste(subImage, (c*256, r*256))
            print "%d/%d" % (count, total)

print "finished download and stitching. "

print "cropping image according to the bounding box..."
left = tile1xy[0] - tile1[0] * 256
upper = tile2xy[1] - tile2[1] * 256
right = tile2xy[0] - tile1[0] * 256
lower = tile1xy[1] - tile2[1] * 256
print 'map size:', p2level*256, 'map tile size:', p2level
print 'tile1xy:', tile1xy, 'tile1:', tile1
print 'tile2xy:', tile2xy, 'tile2:', tile2
print 'crop area:', left, upper, right, lower
cropImage = image.crop((left, upper, right, lower))

image.save("rawImage.jpeg")
cropImage.save("boundingImage.jpeg")

