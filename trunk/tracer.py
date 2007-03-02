#! /usr/bin/python2.4

import os
import locator


class Tracer:

    def __init__(self):
        self.locator = locator.Locator()

    def Init(self):
        self.locator.Init()

    def loadTrace(self, name):
        data=open('./traces/'+name).read().split('\n')
        f=open('./paths/test-trace-'+name,'w')
        oldTime,total,count=0,len(data),0
        oldLat, oldLon = 0.0, 0.0
        ooldLat, ooldLon = 0.0, 0.0
        for line in data:
            count+=1
            print str(count)+'/'+str(total)
            if(len(line)<3):
                continue
            items=line.split(';')
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
                self.locator.ReSample()
                oldTime=t


                                
def main():
    t = Tracer()
    t.Init()
    t.loadTrace('1172767258.out')
    #t.loadTrace('1172594315.out')
    #t.loadTrace('1172608619.out')
    for f in os.listdir('./traces/'):
        t.loadTrace(f)

main()
