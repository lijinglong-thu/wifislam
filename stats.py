#!/usr/bin/env python2.4



def loadDataFile(name):
    f=open('./AccessPoints2.data','w')
    lines = open(name).read().split('\n')
    currentTime,count,baseTime=-1,0,0
    for line in lines:
        if(len(line)<3):
            continue
        items = line.split(';')
        mac,ESSID,dist,t=items[0],items[1],items[2],items[3]
        t=int(t)
        if(currentTime==-1):
            baseTime = t
        if(t>currentTime):
            if(count>0):
                f.write(str(currentTime-baseTime)+'\t')
                f.write(str(count)+'\n')
            currentTime=t
            count=0
        else:
            count+=1

#loadDataFile('./traces/1171917458.out')
loadDataFile('./traces/1171990062.out')
