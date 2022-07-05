# bio-chain.py - a micro-ledger system for bio "mining"
# code by 220 for MP, IV & JG | 2022

import json
import serial
import datetime
import random
import hashlib
import uuid
import sqlite3

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
    def __init__ (self, block_id, previous_hash, timestamp, node_id, challenge, proof_of_work):
        self.block_data = {
            "block_id": block_id,
            "previous_hash": previous_hash,
            "timestamp": timestamp,
            "node_id": node_id,
            "challenge": challenge,
            "proof_of_work": proof_of_work
        }
        self.hash = None

class BioChainService:
    def __init__ (self):
        self.setupChainStorage ()
        print ("BioChain service initiated")

        self.executing = False
        self.last_block = None


        self.chain = []
        self.last_hash = None

        host_name = "localhost"
        server_port = 8036

        self.web_io = ThreadingHTTPServer ((host_name, server_port), MicroWebServer)

        self.web_thread = threading.Thread (target=self.web_io.serve_forever)
        self.web_thread.daemon = True
        self.web_thread.start ()

    def setupChainStorage (self):
        # load existing chain from storage
        self.chain_storage = sqlite3.connect ("bio-chain.db")
        self.sql = self.chain_storage.cursor ()

        self.sql.execute ("SELECT count (name) FROM sqlite_master WHERE type='table' AND name='blocks';")
        if self.sql.fetchone () [0]==0:
            self.initChainStorage ()

    def writeBlock (self, block):
        block_data = block.block_data
        block_hash = self.hashBlock (block_data)

        sql_query = "INSERT INTO blocks VALUES ({0}, '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".format (block_data ["block_id"], block_data ["previous_hash"], block_data ["timestamp"], block_data ["node_id"], block_data ["challenge"], block_data ["proof_of_work"], block_hash)
        self.sql.execute (sql_query)

    def readLastBlock (self):
        sql_query = "SELECT * FROM blocks ORDER BY block_id DESC LIMIT 1;"
        rows = self.sql.execute (sql_query).fetchall () [0]

        block = BioChainBlock (rows [0], rows [1], rows [2], rows [3], rows [4], rows [5])
        block.hash = rows [6]
        return block

    def initChainStorage (self):
        sql_query = "CREATE TABLE blocks (block_id INTEGER PRIMARY KEY, previous_hash TEXT NOT NULL, timestamp TEXT NOT NULL, node_id TEXT NOT NULL, challenge TEXT NOT NULL, proof_of_energy TEXT NOT NULL, block_hash TEXT)"
        self.sql.execute (sql_query)

        timestamp = datetime.datetime.now ()
        genesis_block = BioChainBlock (0, 'no_hash', timestamp, 'cryptogenesis', 'CH', 'POW')

        self.writeBlock (genesis_block)
        self.chain_storage.commit ()

        print ("[bio-chain service: created new bio-chain]")

    def addBlock (self, node_id, challenge, proof_of_work):
        last_block = self.readLastBlock ()
        last_data = last_block.block_data
        last_hash = last_block.hash

        block_id = last_data ["block_id"] + 1
        timestamp = datetime.datetime.now ()
        new_block = BioChainBlock (block_id, last_hash, timestamp, node_id, challenge, proof_of_work)

        self.writeBlock (new_block)
        self.chain_storage.commit ()

    def hashBlock (self, block_data):
        return hashlib.sha256 (str (block_data).encode ()).hexdigest ()

    def execute (self):
        print ("[bio-chain service: active]")

        self.executing = True
        while self.executing:
            # check if comms have arrived
            if port.in_waiting>0:
                input = port.readline ().decode ('ascii').rstrip ('\r\n')
                #print ("INPUT: {0}". format (input))

                if "NOP:" in input:
                    # spark sequence initiated!
                    # get node_id
                    node_id = input [4:]
                    print ("\nspark ignited!! {0}:".format (node_id))

                    answer = self.spark ()
                    if answer [0]==True:
                        print ("VALID answer - granted token to [{0}]".format (node_id))
                        challenge = answer [1]
                        proof_of_work = answer [2]

                        self.addBlock (node_id, challenge, proof_of_work)
                    else:
                        print ("...dropped.")

    def spark (self):
        # start challenge - pick a random uuid
        challenge = str (uuid.uuid4 ())
        challenge_string = "CH:"+challenge

        # send challenge to node
        port.write (challenge_string.encode ())
        # solve challenge
        challenge_answer = hashlib.sha256 (challenge.encode ()).hexdigest ()
        # get answer
        received_answer = port.readline ().decode ('ascii').rstrip ('\r\n')

        return [challenge_answer==received_answer, challenge, received_answer]

port = serial.Serial ('/dev/ttyACM0', 115200)
port.flush ()

biochain_service = BioChainService ()
biochain_service.execute ()
