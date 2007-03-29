#! /usr/bin/python2.4



from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import locator


"""
This is a bare-bones start to a location which can give the user their location from the set of visible MAC addresses
over a standard HTTP query.
"""

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
            #pre='http://maps.google.com/?ie=UTF8&z=17&ll='
            #post='&spn=0.003693,0.007274&t=h'
            #self.wfile.write('<html><a href="')
            #self.wfile.write(pre)
            #self.wfile.write(str(lat)+','+str(lon))
            #self.wfile.write(post)
            #self.wfile.write('">Your location, sir.</a></html>')
            
            data=('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"\n'
                 '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
                  '<html xmlns="http://www.w3.org/1999/xhtml">\n'
                  ' <head>\n'
                  ' <meta http-equiv="content-type" content="text/html; charset=utf-8"/>\n'
                  ' <title>Google Maps JavaScript API Example</title>\n'
    '<script src="http://maps.google.com/maps?file=api&amp;v=2&amp;key=ABQIAAAAZC_HQ-tQunRCK-TG1Xe41BThCcWeYFMLujBthKmziAJWHsaebBSM977wWnnLn6tpPZIi_RyxQK6jvA"\n'
                  ' type="text/javascript"></script>\n'
                  ' <script type="text/javascript">\n'
                  '//<![CDATA[\n'
                  'function load() {\n'
                  'if (GBrowserIsCompatible()) {\n'
                  'var map = new GMap2(document.getElementById("map"));\n'
                  'map.setCenter(new GLatLng(')
            data+=str(lat)+', '+str(lon)+'), 16);\n'
            data+=('map.addControl(new GMapTypeControl());'
                   'map.setMapType( G_SATELLITE_TYPE ); '
                   '}\n'
                  '}\n'
                  '//]]>\n'
                  '</script>\n'
                  '</head>\n'
                  '<body onload="load()" onunload="GUnload()">\n'
                  '<div id="map" style="width: 500px; height: 300px"></div>\n'
                  '</body>\n'
                  '</html>\n')
            self.wfile.write(data)
            #self.wfile.write(open('test.html').read())

            
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
        server = MyServer(('', 12345), MyHandler)
        print 'Started server . . .'
        #server.AddMacFile()
        server.serve_forever()
    except KeyboardInterrupt:
        print 'Closing server...'
        server.socket.close()

if __name__ == '__main__':
    main()
