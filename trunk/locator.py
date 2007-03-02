#! /usr/bin/python2.4

import math
import random
import loc

class Locator:

    def __init__(self):
        self.numParticles = 3000
        self.prevMaxParticle = None
        self.updateCount=1
        self.maxParticle = None
        self.particles = []
        self.macToLL = {}

    def Init(self):
        for i in range(self.numParticles):
            self.particles.append(Particle())
            self.particles[-1].Init(47.66, -122.31, .08, .08)
        self.LoadIDFile('./maps/test-11.id')

    def LoadIDFile(self, name):
        data=open(name).read().split('\n')
        for line in data:
            if(len(line)<3):
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
            if(p.likelihood>maxLikelihood):
                maxLikelihood = p.likelihood
                self.prevMaxParticle = self.maxParticle
                self.maxParticle = p
            totalLikelihood += p.likelihood
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
            total += p.likelihood
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
            p.Perturb()

    def GetLocation(self):
        return self.ReturnBinnedParticle()

    def ReturnOldBestParticle(self):
        if(self.prevMaxParticle!=None):
            return ((self.maxParticle.lat+self.maxParticle.lat)/2,
                    (self.maxParticle.lon+self.maxParticle.lon)/2)
        return (self.maxParticle.lat, self.maxParticle.lon)

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
        bins = {}
        prec=1000
        maxCount,maxKey=0,None
        for p in self.particles:
            key1=(1, int(p.lat*prec)/prec, int(p.lon*prec)/prec)
            key2=(2, int(p.lat*prec+.5)/prec, int(p.lon*prec)/prec)
            key3=(3, int(p.lat*prec)/prec, int(p.lon*prec+.5)/prec)
            key4=(4, int(p.lat*prec+.5)/prec, int(p.lon*prec+.5)/prec)
            for key in [key1, key2, key3, key4]:
                if(not key in bins):
                    bins[key]=[p]    
                bins[key].append(p)
                if(len(bins[key])>maxCount):
                    maxKey=key
                    maxCount=len(bins[key])
        if(maxKey==None):
            return self.ReturnAveLoc()
        aveLat, aveLon, count = 0.0,0.0,0
        for p in bins[maxKey]:
            aveLat+=p.lat
            aveLon+=p.lon
            count+=1
        if(count==0):
            return self.ReturnAveLoc()
        return (aveLat/count, aveLon/count)


class Particle:
    def __init__(self):
        self.lat = 0.0
        self.lon = 0.0
        self.likelihood = 1
        self.noise = .00005

    def Init(self, lat, lon, r1, r2):
        self.lat = random.gauss(lat, r1)
        self.lon = random.gauss(lon, r2)
        self.likelihood = 1

    def Update(self, lat, lon, dist):
        d = loc.LatLongDist(self.lat, lat, self.lon, lon)
        #print 'Lat', self.lat
        #print 'Lat', lat
        #print 'd:', d
        #print 'dsit:', dist
        d = (1+(d-dist)*(d-dist))**.5
        self.likelihood *= 1 / d
        #print 'likelihood:', self.likelihood

    def Perturb(self):
        self.lat = random.gauss(self.lat, self.noise)
        self.lon = random.gauss(self.lon, self.noise)
        self.likelihood = 1

    def Copy(self):
        p = Particle()
        p.lat = self.lat
        p.lon = self.lon
        p.likelihood = self.likelihood
        return p
