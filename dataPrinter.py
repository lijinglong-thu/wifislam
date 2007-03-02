#! /usr/bin/python2.4

import os
import time
import locator

class DataPrinter:

    def __init__(self):
        self.APs = {}
        self.times = []
        self.maxTime = None
        self.minTime = None
        self.locator = locator.Locator()
        self.locator.Init()

    def AddTrace(self, t, mac, ss):
        toAdd = (t, ss)
        if(len(self.times)==0):
            self.times.append(t)
        elif(self.times[-1]!=t):
                self.times.append(t)
        if(mac in self.APs):
            self.APs[mac].append(toAdd)
        else:
            self.APs[mac] = [toAdd]
        if((t<self.minTime)|(self.minTime==None)):
            self.minTime = t
        if((t>self.maxTime)|(self.maxTime==None)):
            self.maxTime = t   

    def OpenTrace(self, name):
        print 'Opening:',name
        lines = open('./traces/'+name).read().split('\n')
        for line in lines:
            items=line.split(';')
            if(len(items)>3):
                mac,essid,ss,t=items[0],items[1],items[2],items[3]
                mac=mac.replace(':','')
                if(mac in self.locator.macToLL):
                    lat,lon=self.locator.macToLL[mac]
                    if((lat<47.655)):
                        if(lon>-122.31):
                            self.AddTrace(int(t), mac, int(ss))


    def SortTraces(self):
        self.times.sort()
        for mac in self.APs:
            self.APs[mac].sort()

    def WriteTraces(self):
        print 'MinTime:', self.minTime
        print 'MaxTime:', self.maxTime
        print 'Num APs:', len(self.APs)
        i = self.minTime
        self.SortTraces()
        f = open('temp.out', 'w')
        total,count=len(self.APs),0
        for mac in self.APs:
            count+=1
            print str(count)+'/'+str(total)
            #f.write('Mac:'+str(mac)+':')
            for i in self.times:
                while(len(self.APs[mac])>0):
                    if(i>self.APs[mac][0][0]):
                        self.APs[mac] = self.APs[mac][1:]
                    else:
                        break
                if(len(self.APs[mac])>0):
                    if(i==self.APs[mac][0][0]):
                        f.write(str(-(self.APs[mac][0][1])))
                        self.APs[mac] = self.APs[mac][1:]
                    else:
                        #print 'i:', i
                        #print 't:', self.APs[mac][0][0]
                        #print '-'
                        f.write('1000')
                else:
                    f.write('1000')
                if(i!=self.times[-1]):
                    f.write(',')
                i += 1
            #print 'mac:',mac
            #print 'blah',self.APs[mac]
            f.write('\n')
        

def main():
    print 'DataPrinter!'
    d = DataPrinter()
    # Allen Center floor two.
    #d.OpenTrace('1172780027.out')
    #
    #d.OpenTrace('1172507645.out')
    #d.OpenTrace('1172249788.out')
    #d.OpenTrace('1172175199.out')
    for f in os.listdir('./traces'):
        if(f.find('.out')>-1):
            if(len(d.times)>4000):
                break
            d.OpenTrace(f)
    d.WriteTraces()

main()
