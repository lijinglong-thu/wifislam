#! /usr/bin/python2.4


import locator

class Tracer:

    def __init__(self):
        self.locator = locator.Locator()

    def Init(self):
        self.locator.Init()

    def loadTrace(self, name):
        data=open(name).read().split('\n')
        f=open('test-trace.out','w')
        oldTime,total,count=0,len(data),0
        for line in data:
            count+=1
            print str(count)+'/'+str(total)
            if(len(line)<3):
                continue
            items=line.split(';')
            mac,essid,ss,t=items[0],items[1],items[2],items[3]
            self.locator.Update(mac, 10**((-32-int(ss))/25.0))
            if(t!=oldTime):
                if(oldTime!=0):
                    lat,lon=self.locator.GetLocation()
                    f.write(str(lon)+'\t'+str(lat)+'\n')
                self.locator.ReSample()
                oldTime=t


                                
def main():
    t = Tracer()
    t.Init()
    t.loadTrace('./traces/1172594315.out')

main()
