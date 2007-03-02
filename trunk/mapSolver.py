#! /usr/bin/python2.4

import time
import heapq
import Queue
import random
import grapher
import loc
import sys

"""
This needs to solve best estimates for node location in terms of lat and long. We start with a set of lower bounds
on edge lengths. Lets init each unlabeled node to the nearest labeled location, then iteratively try and lower entropy
in the graph.
"""


class GraphSolver:

    def __init__(self):
        self.graph = Graph(grapher.Grapher())

    def Solve(self):
        self.InitSolve()
        print '[]'
        #time.sleep(5)
        self.graph.InitHeap()
        print '[]'
        #time.sleep(5)
        for i in range(1000):
            print i, ': Current Score:', self.GetGraphScore()
            print 'Perturbing . . .'
            self.graph.Perturb()
            print 'Sleeping . . .'
            #time.sleep(10)
            print 'Perturbing by heap . . .'
            self.graph.PerturbByHeap()
            self.SaveGraph(i)
            print 'Sleeping . . .'
            #time.sleep(10)


    def SaveGraph(self, i):
        self.SaveGraphNames(i)
        f=open('./maps/test-'+str(i)+'.data','w')
        for mac in self.graph.nodes:
            n=self.graph.nodes[mac]
            if((n.lat!=0.0)&(n.lon!=0.0)):
                if(n.fixed):
                    f.write(str(n.lon)+'\t'+str(n.lat)+'\t'+str(n.lat)+'\n')
                else:
                    f.write(str(n.lon)+'\t'+str(n.lat)+'\n')
        f.close()

    def SaveGraphNames(self, i):
        f=open('./maps/test-'+str(i)+'.id','w')
        for mac in self.graph.nodes:
            n=self.graph.nodes[mac]
            if((n.lat!=0.0)&(n.lon!=0.0)):
                if(n.fixed):
                    f.write(n.uniqueID+'\t'+str(n.lon)+'\t'+str(n.lat)+'\t'+str(n.lat)+'\n')
                else:
                    f.write(n.uniqueID+'\t'+str(n.lon)+'\t'+str(n.lat)+'\n')
        f.close()

    def GetGraphScore(self):
        totalScore=0
        for node in self.graph.nodes:
            totalScore+=self.graph.nodes[node].GetScore(self.graph, False)
        return totalScore

    def InitSolve(self):
        print 'Initing base solution . . .'
        #So have queue of nodes adjancent to fixed.
        q = self.InitQueue()
        #Now iter through list and attach to closest fixed node or self.
        while(not q.empty()):
            node = q.get(False)
            node.findLocalRoot(self.graph)
            for n in node.neighbors:
                if(self.graph.nodes[n].root==None):
                    q.put(self.graph.nodes[n])
        for mac in self.graph.nodes:
            node = self.graph.nodes[mac]
            if(node.root==None):
                continue
            node.lat = self.graph.nodes[node.root].lat
            node.lon = self.graph.nodes[node.root].lon
            if(node.lon==0.0):
                print node.lon
                sys.exit(0)

    def InitQueue(self):
        toReturn = Queue.Queue()
        for node in self.graph.fixedPoints:
            node.root = node.uniqueID
            node.fixed = True
            print 'LL', node.lat, node.lon
            node.distToRoot = 0
            for n in node.neighbors:
                actual=self.graph.nodes[n]
                toReturn.put(actual)
                actual.neighbors[node.uniqueID]=node.neighbors[n]
        return toReturn


class Graph:

    def __init__(self, grapher):
        self.nodes = {}
        self.fixedPoints = []
        self.createBaseNodes(grapher)
        self.loadNeighbors(grapher)
        self.heap = []

    def createBaseNodes(self, grapher):
        for mac in grapher.networkMap:
            self.nodes[mac] = Node(mac, grapher.macToESSID[mac])
        for loc in grapher.locationMap:
            self.nodes[loc] = Node(loc, loc)
            print 'LL:',grapher.locationToLL[loc]
            self.nodes[loc].lat, self.nodes[loc].lon = grapher.locationToLL[loc]
            if(grapher.locationToLL[loc]!=(0,0)):
                self.fixedPoints.append(self.nodes[loc])

    def loadNeighbors(self, grapher):
        for mac in grapher.networkMap:
            for item in grapher.networkMap[mac]:
                self.nodes[mac].addNeighbor(item, self)
        for loc in grapher.locationMap:
            for item in grapher.locationMap[loc]:
                self.nodes[loc].addNeighbor(item, self)

    def InitHeap(self):
        print 'Initing heap . . .'
        print 'Length:', len(self.nodes)
        i=0
        for mac in self.nodes:
            i+=1
            if(i%20 ==0):
                print 'Iter:', i
            n = self.nodes[mac]
            heapq.heappush(self.heap, (-n.GetScore(self, True), n))

    def PerturbByHeap(self):
        for i in range(100):
            score, n = heapq.heappop(self.heap)
            minScore, minLL = -score, (n.lat, n.lon)
            l1, l2 = minLL
            if(minLL==(0.0,0.0)):
                continue
            for i in range(20):
                n.Perturb(l1, l2)
                s = n.GetScore(self, True)
                if(s < minScore):
                    minScore = s
                    minLL = (n.lat, n.lon)    
                n.lat, n.lon = minLL
            heapq.heappush(self.heap, (-minScore, n))

    def Perturb(self):
        for mac in self.nodes:
            n=self.nodes[mac]
            minScore, minLL = n.GetScore(self, False), (n.lat, n.lon)
            l1, l2 = minLL
            if(minLL==(0.0,0.0)):
               continue
            for i in range(30):
                n.Perturb(l1, l2)
                s = n.GetScore(self, False)
                if(s < minScore):
                    minScore = s
                    minLL = (n.lat, n.lon)
            n.lat, n.lon = minLL
                

class Node:

    def __init__(self, uid, name):
        self.uniqueID = uid
        self.name = name
        self.neighbors = {}
        self.distToRoot = 10000000
        self.root = None
        self.lat = 0.0
        self.lon = 0.0
        self.fixed = False
    
    def addNeighbor(self, node, graph):
        mac,dist=node
        if(not mac in self.neighbors):
            self.neighbors[mac]=dist
            try:
                graph.nodes[mac].addNeighbor((self.uniqueID, dist), graph)
            except KeyError:
                pass

    def findLocalRoot(self, g):
        if(self.root!=None):
            return
        minNode, minDist = self.root, self.distToRoot
        for mac in self.neighbors:
            d=self.neighbors[mac]+g.nodes[mac].distToRoot
            if(d<minDist):
                minNode, minDist=mac, d
        self.root,self.distToRoot = minNode, minDist
        self.lat, self.lon = g.nodes[self.root].lat, g.nodes[self.root].lon

    def GetScore(self, graph, all):
        totalScore = 0.0
        if((self.root==None)|(self.lat==0)):
            return 0.0
        for n in self.neighbors:
            actual2 = graph.nodes[n]
            if((actual2.root==None)|(actual2.lat==0)):
                continue
            dist = self.neighbors[n]
            d=loc.LatLongDist(self.lat, actual2.lat, self.lon, actual2.lon)
            if(d>dist):
                if((actual2.fixed)|(self.fixed)):
                    totalScore += 100 * (d/dist-1.0)
                else:
                    totalScore += (d/dist-1.0)
        if(not all):
            return totalScore
        for mac in graph.nodes:
            if((mac in self.neighbors)|(mac==self.uniqueID)):
                continue
            actual2 = graph.nodes[mac]
            if((actual2.root==None)|(actual2.lat==0)):
                continue
            d=loc.LatLongDist(self.lat, actual2.lat, self.lon, actual2.lon)
            if((d<300)&(d>0)):
                totalScore += (400/d - .5)
        return totalScore

    def Perturb(self, l1, l2):
        a,b=0.0,0.0
        if(self.fixed):
            return
        r=random.random()
        if(r<.1):
            a=random.gauss(l1, .0001)
            b=random.gauss(l2, .0001)
        elif(r>.66):
            a=random.gauss(l1, .02)
            b=random.gauss(l2, .02)
        else:
            a=random.gauss(l1, .001)
            b=random.gauss(l2, .001)
        self.lat = a
        self.lon = b



def main():
    print 'Initing Graph . . .'
    g = GraphSolver()
    print 'Solving for locations . . .'
    g.Solve()

main()
