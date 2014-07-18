#!/usr/bin/python
#
# viking_client.py - generate some test traffic
#
# PoC really... Maybe create a UDP listener and take in syslog from your network
# security device(s) or SIEM.
#
# @gitrc 2014

from websocket import create_connection
from random import randrange
import socket
import GeoIP
import geoip2.database
import json
import re
import random
import os
import time

## super secret security
shared_secret = 'key007'

# preload the geoip (version 1) db (for ISP, only one available to me)
geoip = GeoIP.open("GeoIPISP.dat", GeoIP.GEOIP_STANDARD)

# preload the geoip2 db
reader = geoip2.database.Reader('GeoLite2-City.mmdb')

# create lookup
def geoLookup(source_ip, dest_ip, dest_port):
 try:
        response = reader.city(source_ip)
        response2 = reader.city(dest_ip)
        gs_lat = response.location.latitude
        gs_long = response.location.longitude
        gs_cc = response.country.iso_code
        gs_city = response.city.name
        gd_lat = response2.location.latitude
        gd_long = response2.location.longitude
        gd_cc = response2.country.iso_code
        gd_city = response2.city.name
	gs_org = geoip.org_by_addr(source_ip)

        # craft payload to return
        payload = {'latitude':gs_lat,'longitude':gs_long,'countrycode':gs_cc,'country':gs_cc,'city':gs_city,'org':gs_org,'latitude2':gd_lat,'longitude2':gd_long,'countrycode2':gd_cc,'country2':gd_cc,'city2':gd_city,'type':'','md5':source_ip,'dport':dest_port,'svc':dest_port,'zerg':''}
        return payload

 except:
	#print "ERR: GEOIP ERROR"
	next

ws = create_connection("ws://localhost:8888/")


def generateIP():
        blockOne = randrange(0, 255, 1)
        blockTwo = randrange(0, 255, 1)
        blockThree = randrange(0, 255, 1)
        blockFour = randrange(0, 255, 1)
        blockFive = randrange(1, 65535, 1)
        if blockOne == 10:
                return generateIP()
        elif blockOne == 172:
                return generateIP()
        elif blockOne == 192:
                return generateIP()
        else:
                return str(blockOne) + '.' + str(blockTwo) + '.' + str(blockThree) + '.' + str(blockFour)

file = '/etc/services'

ports = set()
for line in open(file):
    m = re.search(r'^[^#].*\s(\d+)/(tcp|udp)\s',line)
    if m:
       port = int(m.groups()[0])
       ports.add(port)

## begin loop
while True:

 try:
  source_ip, dest_ip = generateIP(), generateIP()
  dest_port = random.choice(tuple(ports))
  message = json.dumps(geoLookup(source_ip, dest_ip, dest_port))
  ws.send(shared_secret + message)
 except:
   next
 time.sleep(1)
