#! /usr/bin/python2.4



from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import locator


class MyServer(HTTPServer):
    def __init__(self, server_address, HandlerClass):
        HTTPServer.__init__(self, server_address, HandlerClass)
        print 'In init!'
        self.macToLL={}
        self.AddMacFile()
        self.locator = locator.Locator()
        self.locator.Init()

    def AddMacFile(self):
        lines=open("./maps/test-19.id").read().split('\n')
        for line in lines:
            try:
                items=line.split('\t')
                if(len(items)<3):
                    continue
                mac,lat,lon=items[0],items[2],items[1]
                mac=mac.lower()
                self.macToLL[mac]=(lat, lon)
            except ValueError:
                pass

    def Localize(self, signals):
        self.locator.Init()
        for i in range(10):
            for signal in signals:
                mac, ss = signal
                self.locator.Update(mac, 10**((-32-ss)/25.0))
            self.locator.ReSample()
        for signal in signals:
            mac, ss = signal
            self.locator.Update(mac, 10**((-32-ss)/25.0))
        return self.locator.ReturnOldBestParticle()


class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        """
        Get will do something with locations of access points?
        Can do something simple of the form asking for AP locations
        or something more complicated of asking for user location from
        set of APs and signal strengths.
        """

        """
        I will need two modes. One where a user registers some sort of temporal presence.
                               The second is more of a one-time estimate of location.

        My only fear is that this is massively cpu intensive. Luckily mem req is small.
        """
        print 'hey!'
        print 'Path:'+self.path
        if(self.path.find("/loc?")==0):
            print 'Should give a location.'
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            query=self.path[5:]
            pairs=query.split('&')
            signals=[]
            for pair in pairs:
                mac,ss=pair.split('=')
                print 'Mac:',mac
                print 'SS:',ss
                signals.append((mac, int(ss)))
            lat, lon=self.server.Localize(signals)
            pre='http://maps.google.com/?ie=UTF8&z=17&ll='
            post='&spn=0.003693,0.007274&t=h'
            self.wfile.write('<html><a href="')
            self.wfile.write(pre)
            self.wfile.write(str(lat)+','+str(lon))
            self.wfile.write(post)
            self.wfile.write('">Your location, sir.</a></html>')

            
        elif(self.path.find("/mac?")==0):
            mac=self.path[5:]
            mac=mac.replace(':','')
            mac=mac.lower()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('<html>')
            print 'Mac:',mac
            if(mac in self.server.macToLL):
                self.wfile.write(str(self.server.macToLL[mac]))
            else:
                self.wfile.write('Sorry!')
            self.wfile.write('</html>')
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('<html>Hey!</html>')


    def do_POST(self):
        """
        Posts will accept some sort of trace data from users?
        """

        print 'yo!'





def main():
    try:
        server = MyServer(('', 1234), MyHandler)
        print 'Started server . . .'
        #server.AddMacFile()
        server.serve_forever()
    except KeyboardInterrupt:
        print 'Closing server...'
        server.socket.close()

if __name__ == '__main__':
    main()
