#! /usr/bin/env python2.4

import os
import time
import threading
import locator

class Scanner:

    def __init__(self):
        self.networks = {}
        self.traceFile = open('./traces/'+str(int(time.time()))+'.out', 'w')
        self.lastNetworkSave = time.time()
        self.tryingToExit = False
        self.location = ''
        self.locationTime = 0
        self.locator = locator.Locator()
        self.locator.Init()

    def setLocation(self, location):
        self.location = location
        self.locationTime = time.time()

    def scanCells(self):
        f = os.popen('iwlist eth1 scanning')
        return f.read()

    def scanForever(self):
        while 1:
            self.scan()
            if(self.tryingToExit):
                self.traceFile.close()
                return
            time.sleep(.5)

    def scan(self):
        currentTime = time.time()
        lines = [a.strip() for a in self.scanCells().split('\n')]
        macs = [self.getMac(a) for a in lines if(a.find('Address:')>-1)]
        essids = [self.getESSID(a) for a in lines if(a.find('ESSID:')>-1)]
        signals = [self.getSignal(a) for a in lines if(a.find('Signal level=')>-1)]
        try:
            for i in range(len(macs)):
                mac, essid, signal = macs[i], essids[i], signals[i]
                if(not (mac, essid) in self.networks):
                    self.networks[(mac, essid)] = Network(mac, essid)
                self.networks[(mac, essid)].addScan(signal, currentTime)
                #self.locator.Update(mac, 10**((-32-signal)/25.0))
                self.saveLine(mac, essid, signal)
        except IndexError:
            print 'Index Error!'
        #self.locator.ReSample()
        if(currentTime>self.lastNetworkSave+3): #Network save window
            self.saveNetworks()

    def getMac(self, mac):
        index = mac.find('Address')+9
        return mac[index:]

    def getESSID(self, essid):
        index = essid.find('ESSID')+7
        return essid[index:]

    def getSignal(self, signal):
        index = signal.find('Signal level=')+13
        return int(signal[index:index+3])

    def saveLine(self, mac, essid, signal):
        data = [str(a) for a in [mac, essid, signal, int(time.time())]]
        if(self.locationTime+2>time.time()): #Location save window
            data.append(self.location)
        self.traceFile.write(';'.join(data))
        self.traceFile.write('\n')

    def saveNetworks(self):
        for network in self.networks.values():
            network.saveLine(self.networks.values())
        self.lastNetworkSave = time.time()

    def printOut(self):
        for network in self.networks.values():
            network.printOut()

    def stop(self):
        self.tryingToExit = True


class Network:

    def __init__(self, mac, essid):
        self.macAddress = mac
        self.ESSID = essid
        self.signalLevels = []
        self.times = []
        f=open('./networks/'+mac.replace(':','')+'.id', 'w')
        f.write('ESSID='+essid+'\n')
        f.close()

    def addScan(self, signal, t):
        self.clear()
        self.signalLevels.append(signal)
        self.times.append(t)

    def getAveSignal(self):
        self.clear()
        l = len(self.signalLevels)
        if(l==0):
            return -1000
        return sum(self.signalLevels) / l

    def getAveDistance(self):
        self.clear()
        ave = self.getAveSignal()
        if(ave==-1000):
            return -10000
        return 10**((-32-ave)/25.0) #Map signal strength to distance.

    def saveLine(self, networks):
        self.clear()
        name = self.macAddress.replace(':','')+'.out'
        f = open('./networks/'+name, 'a')
        t = str(int(time.time()))
        for network in networks:
            netName = network.macAddress.replace(':','')
            dist = network.getAveDistance()+self.getAveDistance()
            if(dist>0):
                f.write(';'.join([netName,t,str(dist),'\n']))
        f.close()

    def clear(self):
        i, currentTime = 0, time.time()
        flag = False
        for i in range(len(self.times)):
            if(self.times[i]+3>currentTime): #Signal save window
                flag = True
                break
        if(not flag):
            i += 1
        self.times = self.times[i:]
        self.signalLevels = self.signalLevels[i:]

    def printOut(self):
        l = len(self.signalLevels)
        if(l==0):
            return
        ave = self.getAveSignal()
        d = self.getAveDistance()
        print self.ESSID,':',self.macAddress,'Signal=',ave,'Samples=',l,'Distance=',d 


class Manager:

    def __init__(self):
        self.location = 'I have no idea.'
        self.scanner = Scanner()
        self.scanThread = threading.Thread(target = self.scanner.scanForever)

    def run(self):
        self.scanThread.start()
        while 1:
            try:
                command = raw_input('> ')
                if(command=='exit'):
                    break
                elif(command=='locate me'):
                    self.getLocation()
                elif(command.find('set location')==0):
                    self.setLocation(command)
                elif(command=='ls'):
                    self.scanner.printOut()    
                elif(len(command)>0):
                    print 'Command not found.'
                    print 'Try: [exit, ls, locate me, set location].'
            except EOFError:
                break
        self.scanner.stop()

    def setLocation(self, data):
        index = data.find('set location')+12
        loc=data[index+1:]
        print 'Setting location to:',loc
        self.saveInMasterLocations(loc)
        self.scanner.setLocation(loc)
        f=open('./locations/'+loc+'.out', 'a')
        for network in self.scanner.networks.values():
            if(network.signalLevels==[]):
                continue
            addr = network.macAddress.replace(':','')
            dist = network.getAveDistance()
            t = str(int(time.time()))
            data=[addr, t, str(dist),'\n']
            if(dist>0):
                f.write(';'.join(data))
        f.close()

    def saveInMasterLocations(self, location):
        try:
            prevData = open('masterLocations.txt').read().split('\n')
        except IOError:
            prevData=[]
        if(not (location in prevData)):
            f=open('masterLocations.txt', 'a')
            f.write(location+'\n')
            f.close()

    def getLocation(self):
        lat, lon = self.scanner.locator.GetLocation()
        print 'Lat:', lat
        print 'Lon:', lon
        

def main():
    print 'w  w  w  i  fff  i'
    print 'w  w  w  i  f    i'
    print 'w w w w  i  fff  i'
    print 'ww   ww  i  f    i'
    manager = Manager()
    manager.run()



main()
