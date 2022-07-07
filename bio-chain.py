# bio-chain.py - a ledger blockchain system for organic resources harvesting
# code by 220 for MP, IV & JG | 2022

import serial
import datetime
import random
import hashlib
import uuid
import sqlite3

# [PARAMS]
# a token for every <token_rate> seconds
token_rate = 60

# serial comm:
port_id = "/dev/ttyACM0"
port_rate = 115200

class BioChainBlock:
    def __init__ (self, block_id, previous_hash, timestamp, node_id, challenge, proof_of_work, energy_seconds, average_voltage):
        self.block_data = {
            "block_id": block_id,
            "previous_hash": previous_hash,
            "timestamp": timestamp,
            "node_id": node_id,
            "challenge": challenge,
            "proof_of_work": proof_of_work,
            "energy_seconds": energy_seconds,
            "average_voltage": average_voltage
        }
        self.hash = None

class BioChainService:
    def __init__ (self, port, production_ratio):
        self.setupChainStorage ()
        print ("BioChain service initiated")

        self.port = port

        self.executing = False
        self.last_hash = None

        self.open_challenge = None
        self.production_ratio = production_ratio

    def setupChainStorage (self):
        # load existing chain from storage
        self.chain_storage = sqlite3.connect ("bio-chain.db")
        self.sql = self.chain_storage.cursor ()

        self.sql.execute ("SELECT count (name) FROM sqlite_master WHERE type='table' AND name='blocks';")
        if self.sql.fetchone () [0]==0:
            self.initChainStorage ()

    def initChainStorage (self):
        sql_query = "CREATE TABLE blocks (block_id INTEGER PRIMARY KEY, previous_hash TEXT NOT NULL, timestamp TEXT NOT NULL, node_id TEXT NOT NULL, challenge TEXT NOT NULL, proof_of_energy TEXT NOT NULL, block_hash TEXT, energy_seconds INTEGER NOT NULL, average_voltage DECIMAL (5, 2) NOT NULL)"
        self.sql.execute (sql_query)

        timestamp = datetime.datetime.now ()
        phrase = "This blockchain is a proof of oxygen created using electricity from a cyanobacterial biophotovoltaic cell."
        genesis_block = BioChainBlock (0, phrase, timestamp, 'cryptogenesis bio-chain', 'CH', 'POW', 'ES', 'AV')

        self.writeBlock (genesis_block)
        self.chain_storage.commit ()

        print ("[bio-chain service: created new bio-chain]")

    def writeBlock (self, block):
        block_data = block.block_data
        block_hash = self.hashBlock (block_data)

        sql_query = "INSERT INTO blocks VALUES ({0}, '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}')".format (block_data ["block_id"], block_data ["previous_hash"], block_data ["timestamp"], block_data ["node_id"], block_data ["challenge"], block_data ["proof_of_work"], block_hash, block_data ["energy_seconds"], block_data ["average_voltage"])
        self.sql.execute (sql_query)

    def readLastBlock (self):
        sql_query = "SELECT * FROM blocks ORDER BY block_id DESC LIMIT 1;"
        rows = self.sql.execute (sql_query).fetchall () [0]

        block = BioChainBlock (rows [0], rows [1], rows [2], rows [3], rows [4], rows [5], rows [7], rows [8])
        block.hash = rows [6]
        return block

    def addBlock (self, node_id, challenge, proof_of_work, energy_seconds, average_voltage):
        last_block = self.readLastBlock ()
        last_data = last_block.block_data
        last_hash = last_block.hash

        block_id = last_data ["block_id"] + 1
        timestamp = datetime.datetime.now ()
        new_block = BioChainBlock (block_id, last_hash, timestamp, node_id, challenge, proof_of_work, energy_seconds, average_voltage)

        self.writeBlock (new_block)
        self.chain_storage.commit ()

    def hashBlock (self, block_data):
        return hashlib.sha256 (str (block_data).encode ()).hexdigest ()

    def execute (self):
        print ("[bio-chain service: active]")

        self.executing = True
        self.waiting = False

        while self.executing:
            # check if comms have arrived
            if self.port.in_waiting>0:
                input = self.port.readline ().decode ('ascii').rstrip ('\r\n')
                print ("INPUT: {0}". format (input))

                # parser
                if "CHR:" in input:
                    challenge_response = input [4:input.index ("|")]
                    average_voltage = input [input.index ("|")+1:]

                    print ("RESPONSE: {0}".format (challenge_response))
                    print ("Voltage: {0}".format (average_voltage))
                    if self.closeChallenge (self.open_challenge, challenge_response):
                        self.waiting = False

                        node_id = self.open_challenge [0]
                        challenge = self.open_challenge [2]
                        proof_of_work = self.open_challenge [3]
                        energy_seconds = self.production_ratio

                        self.addBlock (node_id, challenge, proof_of_work, energy_seconds, average_voltage)
                        self.open_challenge = None

                if "NOP:" in input:
                    # spark sequence initiated!
                    # get node_id
                    node_id = input [4:]
                    print ("\nspark ignited!! {0}:".format (node_id))

                    # add challenge
                    self.open_challenge = self.openChallenge (node_id)

                input = ""

            # management
            if self.open_challenge!=None:
                challenge_time = self.open_challenge [1]
                self.current_time = datetime.datetime.now ()-challenge_time
                if self.current_time.total_seconds ()>=self.production_ratio and not self.waiting:
                    response_query = "RQ:0"
                    self.port.write (response_query.encode ())
                    self.waiting = True


    def openChallenge (self, node_id):
        # start challenge - pick a random uuid
        challenge = str (uuid.uuid4 ())
        answer = hashlib.sha256 (challenge.encode ()).hexdigest ()
        begin_timestamp = datetime.datetime.now ()

        # deliver challenge
        challenge_string = "CH:"+challenge
        print ("CHallenge_string: "+challenge_string)
        self.port.write (challenge_string.encode ())

        open_challenge = (node_id, begin_timestamp, challenge, answer)
        return open_challenge

    def closeChallenge (self, challenge, response):
        if response==challenge [3]:
            # VALID!
            print ("VALID answer!! to {0}".format (challenge [2]))

            acknowledgement_string = "ACK:"
            self.port.write (acknowledgement_string.encode ())

            return True
        else:
            print ("...dropped")

            acknowledgement_string = "DROP:"
            self.port.write (acknowledgement_string.encode ())
            return False

# main execute
if __name__ == "__main__":
    port = serial.Serial (port_id, port_rate)
    port.flush ()

    biochain_service = BioChainService (port, token_rate)
    biochain_service.execute ()
