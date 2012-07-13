import SimpleHTTPServer
import os
import SocketServer
import ROOT
import signal
import sys
port = 12345

DUMMY_RESPONSE =" HELLO WORLD"

def list_root(f, prefix=''):
  response = ''
  for key in f.GetListOfKeys():
    response += key.GetClassName() + " " + prefix + key.GetTitle() + "\n"
    if key.GetClassName() == 'TDirectoryFile':
      d = f.Get(key.GetTitle())
      response += list_root(d, prefix + key.GetTitle() + '/')
  return response


class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
  def send_file(self, path):
    ext = '.'+path.split('.')[-1].upper().swapcase()
    file = open(path, 'r')
    self.send_response(200)
    if ext in self.extensions_map:
      self.send_header("Content-type", self.extensions_map[ext])
    else:
      self.send_header("Content-type", "binary/octet-stream")
    self.send_header("Content-length", os.path.getsize(path))
    self.end_headers()
    while 1:
      stuff = file.read(1024)
      if stuff == '':
        break
      self.wfile.write(stuff)

  def noexists(self, path):
    self.send_response(404)
    self.end_headers()

  def dirlist(self, path):
    response = 'dir listing'
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.send_header("Content-length", len(response))
    self.end_headers()
    self.wfile.write(response)

  def rootlist(self, tfile):
    response = list_root(tfile)
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.send_header("Content-length", len(response))
    self.end_headers()
    self.wfile.write(response)



    
  def do_GET(self):
    path = self.path.split('?')[0][1:]
    if path == '':
      path = '.'
    if len(self.path.split('?')) > 1:
      getvars = self.path.split('?')[1]
    else:
      getvars = ''

    print path
    response = ""

    if os.path.isdir(path):
      self.dirlist(path)
    elif os.path.isfile(path):
      ext = '.'+path.split('.')[-1].upper().swapcase()
      if ext == '.root':
        f = ROOT.TFile(path)
        if getvars:
          obj = f.Get(getvars)
          if obj:
            c = ROOT.TCanvas("c", "", 700, 500)
            obj.Draw()
            c.SaveAs("tmpPYTHONSERVER.png")
            self.send_file("tmpPYTHONSERVER.png")
            os.remove("tmpPYTHONSERVER.png")
          else:
            self.noexists(path)
        else:
          self.rootlist(f)
        f.Close()
      else:
        self.send_file(path)
    else:
      self.noexists(path)
      
  

httpd = SocketServer.TCPServer(("127.0.0.1", port), Handler)


print 'Ready on port', port
httpd.serve_forever()
