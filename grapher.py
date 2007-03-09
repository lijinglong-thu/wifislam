#! /usr/bin/env python2.4


import os

#$ dot -Tgif second.dot -o second.gif -v


# TODO: This is the class that needs revision to fix the awful ./networks repo.
#       We should dynamicly build up the shortest distance between networks,
#       Also merge all of the ID files into one master file.

class Grapher:

    def __init__(self):
        self.macToESSID = {}
        self.networkMap = {}
        self.locationMap = {}
        self.locationToLL = {}
        self.loadTranslations()
        self.loadGraph()
        #self.trimGraph()
        self.clusterCount=0


    def loadTranslations(self):
        files = os.listdir('./networks/')
        for f in files:
            if(f.find('.id')==-1):
                continue
            data=open('./networks/'+f).read()
            self.macToESSID[f[:-3]]=data[6:-2].strip()

    def loadGraph(self):
        self.loadNetworks()
        self.loadLocations()

    def loadLocations(self):
        files = os.listdir('./locations/')
        for f in files:
            if(f.find('.out')>-1):
                edges=self.loadDataFile(open('./locations/'+f).read())
                self.locationMap["LOCATION"+f[:-4]]=edges
            elif(f.find('.id')>-1):
                ll = self.loadLLData(open('./locations/'+f).read())
                if(ll==(0,0)):
                    print 'FileName:', f
                self.locationToLL["LOCATION"+f[:-3]] = ll

    def loadNetworks(self):
        files = os.listdir('./networks/')
        for f in files:
            if(f.find('.out')==-1):
                continue
            edges = self.loadDataFile(open('./networks/'+f).read())
            self.networkMap[f[:-4]]=edges

    def loadLLData(self, data):
        lat,lon=0,0
        try:
            for line in data.split('\n'):
                if(line.find('LAT=')==0):
                    lat = float(line[4:])
                elif(line.find('LON')==0):
                    lon = float(line[4:])
        except ValueError:
            print 'LatLon Error:', line
        return (lat, lon)
            
    def loadDataFile(self, data):
        minDist, toReturn = {}, []
        for line in data.split('\n'):
            if(len(line)<3):
                continue
            try:
                mac, t, dist, end = line.split(';')
                dist=float(dist)
                #if((dist<0)|(dist>100)):
                if(dist<0):
                    continue
                if(not mac in minDist):
                    minDist[mac] = dist
                if(minDist[mac] < dist):
                    minDist[mac] = dist
            except ValueError, err:
                print 'ERROR1'
                print 'Line:', line
                print err
                break
        for key in minDist:
            toReturn.append((key, minDist[key]))
        return toReturn

    def trimGraph(self):
        #TODO: rank by distance.
        for node in self.networkMap:
            self.networkMap[node]=self.networkMap[node][:5]

    def makeGraphVizFile(self, translate):
        done, clusters = {}, {}
        f=open('./second.dot','w')
        f.write('graph G{\n')
        #f.write('overlap=scale;\n')
        #f.write('overlap=false;\n')
        self.drawEdges(f, self.locationMap, done, clusters, False)
        self.drawEdges(f, self.networkMap, done, clusters, True)
        f.write('}\n')
        f.close()
                

    def drawEdges(self, f, map, done, clusters, translate):
        for network in map:
            neighbors = map[network]
            if(not translate):
                f.write('subgraph "cluster'+str(self.clusterCount)+'"{\n')
                f.write('style=filled;\n')
            for item in neighbors:
                n, dist = item
                if(n==network):
                    continue
                if((not translate)&(not n in clusters)):
                    clusters[n]='cluster'+str(self.clusterCount)
                if(not (network, n) in done):
                    a,b=network,n
                    #if(a in clusters):
                    #   if(clusters[a]!='cluster'+str(self.clusterCount)):
                    #       a=clusters[a]
                    #if(b in clusters):
                    #    if(clusters[b]!='cluster'+str(self.clusterCount)):
                    #        b=clusters[b]
                    #if(a==b):
                    #    a,b=network,n
                    #if((a, b) in done):
                    #    continue
                    if(translate):
                        if(not network in done):
                            f.write('"'+network+'" [label="'+self.macToESSID[network]+'"];\n')
                        if(not n in done):
                            f.write('"'+n+'" [label="'+self.macToESSID[n]+'"];\n')
                        done[network], done[n] = None, None
                    #f.write('"'+a+'"--"'+b+'" [label="'+str(int(dist))+'" weight='+str((11-int(dist**.5)))+'];\n')
                    f.write('"'+a+'"--"'+b+'" [label="'+str(int(dist))+'"];\n')
                done[(network, n)], done[(n, network)] = None, None
                done[(a, b)], done[(b, a)] = None, None
            if(not translate):
                f.write('}\n')
                self.clusterCount+=1

def main():
    g = Grapher()
    g.makeGraphVizFile(True)

#main()
            
