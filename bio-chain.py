# bio-chain.py code by 220 for MP, IV & JG
# a micro-ledger system for bio "mining"

import serial
import datetime
import random
import hashlib
import uuid
import json

import threading

from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

class MicroWebServer (BaseHTTPRequestHandler):
    def do_GET (self):
        self.send_response (200)
        self.send_header ("Content-type", "text/html")
        self.end_headers ()

        self.wfile.write (bytes ("<html><head><title>cryptogenesis</title></head>", "utf-8"))
        self.wfile.write (bytes ("<h1>cryptogenesis</h1>", "utf-8"))
        self.wfile.write (bytes ("Total blocks: <br />", "utf-8"))
        #self.wfile.write (bytes ("<p>cryptogenesis</p>", "utf-8"))
        self.wfile.write (bytes ("</body></html>", "utf-8"))

class BioChainBlock:
    def __init__ (self, last_hash, node_id):
        timestamp = datetime.datetime.now ()
        self.block_data = {
            "previous_hash": last_hash,
            "node_id": node_id,
            "timestamp": timestamp
        }
        self.hash = None

class BioChainService:
    def __init__ (self):
        # load existing chain from storage

        # ...or:
        self.chain = []
        print ("BioChain service initiated")

        self.last_hash = None
        self.addBlock (BioChainBlock (1, 1))

        self.executing = False

        host_name = "localhost"
        server_port = 8036


        self.web_io = ThreadingHTTPServer ((host_name, server_port), MicroWebServer)

        self.web_thread = threading.Thread (target=self.web_io.serve_forever)
        self.web_thread.daemon = True
        self.web_thread.start ()


    def addBlock (self, block):
        bcb_hash = self.hashBlock (block.block_data)
        block.hash = bcb_hash

        self.chain.append (block)
        print ("Adding block {0} to chain: {1}".format (bcb_hash, block.block_data))
        print ("Blockchain size: {0}".format (len (self.chain)))

        self.bc_data = open ("./bio-chain.data", "a")
        self.bc_data.write ("{0}\n{1}\n{2}\n\n".format (self.last_hash, block.block_data ["node_id"], block.hash))
        self.bc_data.close ()

        self.last_hash = bcb_hash

    def hashBlock (self, block_data):
        return hashlib.sha256 (str (block_data).encode ()).hexdigest ()

    def execute (self):
        print ("BioChain service executing")

        self.executing = True
        while self.executing:
            # check if comms have arrived
            if port.in_waiting>0:
                input = port.readline ().decode ('ascii').rstrip ('\r\n')

                if input=="NOP":
                    # spark sequence initiated!
                    # get node_id
                    node_id = port.readline ().decode ('ascii').rstrip ('\r\n')
                    print ("\nspark ignited!! {0}:".format (node_id))

                    if self.spark ():
                        print ("VALID answer from [{0}]".format (node_id))
                        self.addBlock (BioChainBlock (self.last_hash, node_id))

    def spark (self):
        # start challenge - pick a random uuid
        challenge = str (uuid.uuid4 ())
        print ("challenge:"+challenge)
        # send challenge to node
        port.write (challenge.encode ())

        # solve challenge
        challenge_answer = hashlib.sha256 (challenge.encode ()).hexdigest ()

        # get answer
        received_answer = port.readline ().decode ('ascii').rstrip ('\r\n')
        print ("Ranswer: {0}".format (received_answer))

        return challenge_answer==received_answer

port = serial.Serial ('/dev/ttyACM0', 115200)
port.flush ()

biochain_service = BioChainService ()
biochain_service.execute ()
