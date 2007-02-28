#! /usr/bin/python2.4


import random
import loc

class Locator:

    def __init__(self):
        self.numParticles = 5000
        self.maxParticle = None
        self.particles = []
        self.macToLL = {}

    def Init(self):
        for i in range(self.numParticles):
            self.particles.append(Particle())
            self.particles[-1].Init(47.66, -122.31, .08, .08)
        self.LoadIDFile('./maps/test-4.id')

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
            lat, lon = self.macToLL[mac]
            for particle in self.particles:
                particle.Update(lat, lon, dist)
        else:
            print "Don't have a location for:", mac

    def ReSample(self):
        #print 'Start resample'
        newParticles = []
        totalLikelihood, maxLikelihood = 0.0, -1
        for p in self.particles:
            if(p.likelihood>maxLikelihood):
                maxLikelihood = p.likelihood
                self.maxParticle = p
            totalLikelihood += p.likelihood
        if(totalLikelihood == 0):
            return
        print '***'
        print 'Lat:', self.maxParticle.lat
        print 'Lon:', self.maxParticle.lon
        print 'L:',maxLikelihood
        delta = totalLikelihood / self.numParticles
        goal, total = random.uniform(0, delta), 0
        for p in self.particles:
            total += p.likelihood
            while(total >= goal):
                newParticles.append(p.Copy())
                goal += delta
            if(len(newParticles)+100>self.numParticles):
                break
        while(len(newParticles)<self.numParticles):
            newParticles.append(Particle())
            newParticles[-1].Init(47.66, -122.31, .08, .08)

        self.particles = newParticles
        for p in self.particles:
            p.Perturb()

    def GetLocation(self):
        return (self.maxParticle.lat, self.maxParticle.lon)


class Particle:
    def __init__(self):
        self.lat = None
        self.lon = None
        self.likelihood = None
        self.noise = .005

    def Init(self, lat, lon, r1, r2):
        self.lat = random.gauss(lat, r1)
        self.lon = random.gauss(lon, r2)
        self.likelihood = 0

    def Update(self, lat, lon, dist):
        d = loc.LatLongDist(self.lat, lat, self.lon, lon)
        #print 'Lat', self.lat
        #print 'Lat', lat
        
        #print 'd:', d
        #print 'dsit:', dist
        self.likelihood = 1 / (1+(d-dist)*(d-dist))
        #print 'likelihood:', self.likelihood

    def Perturb(self):
        self.lat = random.gauss(self.lat, self.noise)
        self.lon = random.gauss(self.lon, self.noise)

    def Copy(self):
        p = Particle()
        p.lat = self.lat
        p.lon = self.lon
        return p
