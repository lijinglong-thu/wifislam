#! /usr/bin/env python2.4


import math

"""
This function finds approximate distance between two latitude and longitude pairs.
"""


def DegToRad(ang):
    return ang * math.pi / 180.0

def LatLongDist(lat1, lat2, long1, long2):
    d = 0.0
    R = 6371000 #km
    lat1 = DegToRad(lat1)
    lat2 = DegToRad(lat2)
    long1 = DegToRad(long1)
    long2 = DegToRad(long2)
    try:
        inner = math.sin(lat1)*math.sin(lat2)+math.cos(lat1)*math.cos(lat2)*math.cos(long2-long1)
        #print 'Inner:',inner
        if((inner-1.0<(2**-30))&(inner-1.0>0)):
            #print 'remainder:',(inner-1.0), (2**-30)
            return 0.0
        d = math.acos(inner)*R
        #print 'D:', d
        return d
    except ValueError, err:
        print 'Lat1:',lat1
        print 'Lat2:',lat2
        print 'Long1:',long1
        print 'Long2:',long2
        print 'Inner:', inner-1.0
        if(inner==1.0):
            print 'Equal to 1'
        print 'Err:', err
    return 0.0


    

#CSE
#http://maps.google.com/maps?f=q&hl=en&q=Seattle,+WA&ie=UTF8&om=1&z=17&ll=47.653276,-122.30607&spn=0.003693,0.010793

#Banister
#http://maps.google.com/maps?f=q&hl=en&q=Seattle,+WA&ie=UTF8&om=1&z=17&ll=47.670481,-122.314289&spn=0.003692,0.010793

#print LatLongDist(47.653276, 47.670481, -122.30607,-122.314289)
