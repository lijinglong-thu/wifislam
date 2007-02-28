#! /usr/bin/python2.4


import time

class DataPrinter:

    def __init__(self):
        self.APs = {}
        self.times = []
        self.maxTime = None
        self.minTime = None

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
        lines = open('./traces/'+name).read().split('\n')
        for line in lines:
            items=line.split(';')
            if(len(items)>3):
                mac,essid,ss,t=items[0],items[1],items[2],items[3]
                self.AddTrace(int(t), mac, int(ss))

    def SortTraces(self):
        for mac in self.APs:
            self.APs[mac].sort()

    def WriteTraces(self):
        print 'MinTime:', self.minTime
        print 'MaxTime:', self.maxTime
        print 'Num APs:', len(self.APs)
        i = self.minTime
        self.SortTraces()
        f = open('temp.out', 'w')
        for mac in self.APs:
            for i in self.times:
                if(len(self.APs[mac])>0):
                    if(i==self.APs[mac][0][0]):
                        f.write(str(-(self.APs[mac][0][1])))
                        self.APs[mac] = self.APs[mac][1:]
                    else:
                        f.write('inf')
                else:
                    f.write('inf')
                if(i!=self.times[-1]):
                    f.write(',')
                i += 1
            f.write('\n')
        

def main():
    print 'DataPrinter!'
    d = DataPrinter()
    d.OpenTrace('1172507645.out')
    d.OpenTrace('1172249788.out')
    d.OpenTrace('1172175199.out')
    d.WriteTraces()

main()
