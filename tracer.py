#! /usr/bin/python2.4

import os
import sys
import locator

#TODO: I should only grab location every x seconds and linear interpolate between.
# (Max likelihood?) Something?

class Tracer:

    def __init__(self):
        self.locator = locator.Locator()
        self.ReSampleCount = 2
        self.num = int(sys.argv[1])
        self.total = int(sys.argv[2])

    def Init(self):
        self.locator.Init()

    def loadTrace(self, name):
        if(hash(name)%self.total!=self.num):
            return
        data=open('./traces/'+name).read().split('\n')
        f=open('./paths/revised-trace-'+name,'w')
        oldTime,total,count=0,len(data),0
        oldLat, oldLon = 0.0, 0.0
        ooldLat, ooldLon = 0.0, 0.0
        for line in data:
            count+=1
            print str(count)+'/'+str(total)
            if(len(line)<3):
                continue
            items=line.split(';')
            if(len(items)<4):
                f=open('err.out','a')
                f.write('Error, Tracer:'+line+'\n')
                f.close()
                continue
            mac,essid,ss,t=items[0],items[1],items[2],int(items[3])
            self.locator.Update(mac, 10**((-32-int(ss))/25.0))
            if(t>oldTime):
                if(oldTime!=0):
                    f.write(str(t)+'\t')
                    lat,lon=self.locator.ReturnOldBestParticle()
                    f.write(str(lon)+'\t'+str(lat))
                    lat,lon=self.locator.ReturnAveLoc()
                    f.write('\t'+str(lon)+'\t'+str(lat))
                    lat,lon=self.locator.GetLocation()
                    f.write('\t'+str(lon)+'\t'+str(lat))
                    if(oldLat!=0.0):
                        if(ooldLat==0.0):
                            f.write('\t'+str((lon+oldLon)/2)+'\t'+str((lat+oldLat)/2))
                        else:
                            f.write('\t'+str((ooldLon+2*oldLon+3*lon)/6))
                            f.write('\t'+str((ooldLat+2*oldLat+3*lat)/6))
                    ooldLat, ooldLon = oldLat, oldLon
                    oldLat,oldLon=lat,lon
                    f.write('\n')
                    f.flush()
                if(t%self.ReSampleCount==0):
                    self.locator.ReSample()
                oldTime=t


                                
def main():
    t = Tracer()
    t.Init()
    t.loadTrace('1172767258.out')
    #t.loadTrace('1172594315.out')
    #t.loadTrace('1172608619.out')
    #files=os.listdir('./traces/')
    #files.reverse()
    #for f in files:
    #    if(f.find('.out')>-1):
    #        t.loadTrace(f)

main()
