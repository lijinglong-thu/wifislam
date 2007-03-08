#! /usr/bin/python2.4

import math
import random
import loc

# TODO: can I do better with making paths out of particle estimates?
#       Perhaps something with estimating current velocity and adding that
#       to the perturb gaussians?


class Locator:

    def __init__(self):
        self.numParticles = 2000
        self.prevMaxParticle = None
        self.updateCount=1
        self.maxParticle = None
        self.particles = []
        self.macToLL = {}
        self.prevLoc = None
        self.prevDir = None

    def Init(self):
        for i in range(self.numParticles):
            self.particles.append(Particle())
            self.particles[-1].Init(47.66, -122.31, .08, .08)
        #self.LoadIDFile('./maps/test-20.id')
        self.LoadIDFile('./newMap.data')
        #self.LoadIDFile('./map2.data')
        #for i in range(10):
        #    self.LoadIDFile('./newMap-'+str(i)+'-10.data')

    def LoadIDFile(self, name):
        data=open(name).read().split('\n')
        for line in data:
            if(len(line.split('\t'))!=3):
                continue
            try:
                mac, lon, lat = line.split('\t')
                self.macToLL[mac] = (float(lat), float(lon))
            except ValueError:
                print 'Error:',line

    def Update(self, mac, dist):
        mac = mac.replace(':', '')
        if(mac in self.macToLL):
            self.updateCount+=1
            lat, lon = self.macToLL[mac]
            for particle in self.particles:
                particle.Update(lat, lon, dist)
        else:
            print "Don't have a location for:", mac

    def ReSample(self):
        newParticles = []
        totalLikelihood, maxLikelihood = 0.0, -1
        if(self.maxParticle!=None):
            self.maxParticle.likelihood=0
        for p in self.particles:
            if(p.GetLikelihood()>maxLikelihood):
                maxLikelihood = p.GetLikelihood()
                self.prevMaxParticle = self.maxParticle
                self.maxParticle = p
            totalLikelihood += p.GetLikelihood()
        if(totalLikelihood == 0):
            return
        print '***'
        print 'Lat:', self.maxParticle.lat
        print 'Lon:', self.maxParticle.lon
        print 'L:',maxLikelihood
        print '-logL:', -math.log(maxLikelihood) / self.updateCount
        self.updateCount=1
        delta = totalLikelihood / (self.numParticles-20)
        goal, total = random.uniform(0, delta), 0
        for p in self.particles:
            total += p.GetLikelihood()
            while(total >= goal):
                newParticles.append(p.Copy())
                goal += delta
            if(len(newParticles)+20>self.numParticles):
                break
        while(len(newParticles)<self.numParticles):
            newParticles.append(Particle())
            newParticles[-1].Init(47.66, -122.31, .03, .03)
        self.particles = newParticles
        for p in self.particles:
            p.Perturb(self.prevDir)

    def GetLocation(self):
        loc = self.ReturnBinnedParticle()
        if(self.prevLoc != None):
            print 'Loc[0]', loc[0]
            print 'Loc[1]', loc[1]
            self.prevDir = (loc[0]-self.prevLoc[0], loc[1]-self.prevLoc[1])
            print 'PrevDir:', self.prevDir
        self.prevLoc = loc
        return loc

    def ReturnOldBestParticle(self):
        if(self.prevMaxParticle!=None):
            return ((self.maxParticle.lat+self.maxParticle.lat)/2,
                    (self.maxParticle.lon+self.maxParticle.lon)/2)
        if(self.maxParticle!=None):
            return (self.maxParticle.lat, self.maxParticle.lon)
        else:
            maxP=self.particles[0]
            for p in self.particles:
                if(p.GetLikelihood()>maxP.GetLikelihood()):
                    maxP=p
            return (maxP.lat, maxP.lon)

    def ReturnAveLoc(self):
        aveLat, aveLon, count = 0.0,0.0,0
        for p in self.particles:
            if((p.lat!=0)&(p.lon!=0)):
                aveLat+=p.lat
                aveLon+=p.lon
                count += 1
        if(count==0):
            return self.ReturnOldBestParticle()
        return (aveLat/count, aveLon/count)

    def ReturnBinnedParticle(self):
        sums,bins = {}, {}
        prec=1000
        maxKey=None
        for p in self.particles:
            key1=(1, int(p.lat*prec)/prec, int(p.lon*prec)/prec)
            key2=(2, int(p.lat*prec+.5)/prec, int(p.lon*prec)/prec)
            key3=(3, int(p.lat*prec)/prec, int(p.lon*prec+.5)/prec)
            key4=(4, int(p.lat*prec+.5)/prec, int(p.lon*prec+.5)/prec)
            for key in [key1, key2, key3, key4]:
                if(not key in bins):
                    bins[key]=[]
                    sums[key]=0.0
                bins[key].append(p)
                sums[key]+=p.GetLikelihood()
                if(maxKey==None):
                    maxKey=key
                if(sums[key]>sums[maxKey]):
                    maxKey=key
        if(maxKey==None):
            return self.ReturnAveLoc()
        aveLat, aveLon, count = 0.0,0.0,0.0
        for p in bins[maxKey]:
            aveLat+=p.lat*p.GetLikelihood()
            aveLon+=p.lon*p.GetLikelihood()
            count+=p.GetLikelihood()
        if(count==0.0):
            return self.ReturnAveLoc()
        return (aveLat/count, aveLon/count)


class Particle:
    def __init__(self):
        self.lat = 0.0
        self.lon = 0.0
        self.likelihood = 1
        self.elikelihood = 1
        self.valid = False
        self.noise = .00002
        self.updateCount = 1

    def Init(self, lat, lon, r1, r2):
        self.lat = random.gauss(lat, r1)
        self.lon = random.gauss(lon, r2)
        self.likelihood = 1
        self.updateCount = 1

    def Update(self, lat, lon, dist):
        d = loc.LatLongDist(self.lat, lat, self.lon, lon)
        r=(d-dist)
        if(r<0):
            r=-r
        d = math.log(1+r)
        if(d>100):
            d=100
        self.updateCount+=1
        self.likelihood += d
        self.valid = False

    def GetLikelihood(self):
        if(not self.valid):
            self.valid = True
            self.elikelihood = 2**-(self.likelihood/self.updateCount)
        return self.elikelihood

    def Perturb(self, dir):
        self.lat = random.gauss(self.lat, self.noise)
        self.lon = random.gauss(self.lon, self.noise)
        if(dir!=None):
            self.lat+=dir[0]
            self.lon+=dir[1]
        self.likelihood = 1
        self.updateCount=1

    def Copy(self):
        p = Particle()
        p.lat = self.lat
        p.lon = self.lon
        p.likelihood = self.likelihood
        p.updateCount = self.updateCount
        return p
