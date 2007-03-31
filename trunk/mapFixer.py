#! /usr/bin/python2.4

import os
import sys
import locator

class MapFixer:

    def __init__(self):
        self.macs = {}
        self.macLocs = {}
        self.num = 0
        self.total = 1
        self.locator = locator.locator()

    def Init(self):
        self.LoadData()
        self.num=int(sys.argv[1])
        self.total=int(sys.argv[2])
        self.locator.Init()

    def LoadData(self):
        traces= os.listdir('./traces/')
        paths = os.listdir('./paths/')
        for fileName in paths:
            f=fileName[10:]
            if(f in traces):
                print f
                self.LoadDataFile(f)
        self.LoadMacLocs()

    def LoadMacLocs(self):
        lines=open('./maps/test-20.id').read().split('\n')
        for line in lines:
            try:
                mac, lon, lat=line.split('\t')
                self.macLocs[mac]=(float(lat), float(lon))
            except ValueError:
                if(len(line)>1):
                    print 'Error: LoadMacLocs:', line

    def LoadDataFile(self, f):
        timeToLoc = self.LoadPath(f)
        self.LoadTrace(f, timeToLoc)

    def LoadPath(self, f):
        timeToLoc={}
        pathData=open('./paths/new-trace-'+f).read().split('\n')
        for line in pathData:
            try:
                items=line.split('\t')
                t,lat,lon=int(items[0]),float(items[8]),float(items[7])
                timeToLoc[t]=(lat, lon)
            except IndexError:
                pass
            except ValueError:
                pass
        return timeToLoc

    def LoadTrace(self, f, timeToLoc):
        traceData=open('./traces/'+f).read().split('\n')
        for line in traceData:
            try:
                items=line.split(';')
                mac,essid,ss,t=items[0],items[1],items[2],int(items[3])
                mac=mac.replace(':','')
                if(t in timeToLoc):
                    if(not mac in self.macs):
                        self.macs[mac]=[]
                    self.macs[mac].append((int(ss), timeToLoc[t]))
            except ValueError:
                print 'Line:', line
            except IndexError:
                pass

    def ReviseGraph(self):
        print 'Revising Graph . . .'
        total,count=len(self.macs),0
        f=open('newMap-'+str(self.num)+'-'+str(self.total)+'.data','w')
        for mac in self.macs:
            # TODO: if not in macLocs, then maybe assign default
            # of current user with slightly larger guass?
            if(mac in self.macLocs):
                count+=1
                if(hash(mac)%self.total!=self.num):
                    continue
                print str(count)+'/'+str(total)
                self.ReviseNode(mac, f)
                f.flush()
        f.close()

    # TODO: This should use locator to particleFilter it.
    def ReviseNode(self, mac, f):
        lat,lon=self.macLocs[mac]
        readings,particles=self.macs[mac],[]
        for i in range(2000):
            particles.append(self.GaussParticle(lat, lon))
        particles.append(locator.Particle())
        particles[-1].lat=lat
        particles[-1].lon=lon
        for p in particles:
            for r in readings:
                ss,ll=r
                lat, lon = ll
                p.Update(lat, lon, 10**((-32-ss)/25.0))
        print 'Base:', lat, lon
        ll = self.GetAveLocation(particles)
        print 'Average:', ll
        f.write(str(mac)+'\t'+str(ll[1])+'\t'+str(ll[0])+'\n')

    def GetAveLocation(self, particles):
        count,aveLat,aveLon=0.0,0.0,0.0
        for p in particles:
            aveLat+=p.lat*p.GetLikelihood()
            aveLon+=p.lon*p.GetLikelihood()
            count+=p.GetLikelihood()
        return (aveLat/count, aveLon/count)

    def GaussParticle(self, lat, lon):
        p=locator.Particle()
        p.Init(lat, lon, .0005, .0005)
        return p


def main():
    m=MapFixer()
    m.Init()
    m.ReviseGraph()

main()
