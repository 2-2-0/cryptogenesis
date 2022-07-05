// bio-chain-collector.ino - a POE/W system for organic data harvesting
// code by 220 for MP, IV & JG | 2022

#include <Crypto.h>
#include <SHA256.h>
#include <string.h>

#define HASH_SIZE 32

SHA256 sha;

uint8_t hash [HASH_SIZE];

String node_id = "0b1b7a78-2a13-4029-ac6b-d6bdbad6e96";

void setup() {
  Serial.setTimeout (20);
  Serial.begin (115200);
  Serial.flush ();
}

void loop() {
  spark ();
  delay (20);
}

void spark () {
  // requests new operation and identifies by using node_id
  Serial.print ("NOP:"+node_id);
  Serial.print ('\n');
  
  // receives challenge string (a uuid)
  String challenge_string = Serial.readStringUntil ('\n');
  if (challenge_string.indexOf ("CH:")!=-1) {
    // extract challenge
    challenge_string = challenge_string.substring (3);
   
    // hashes challenge using SHA256 - POE/W
    sha.reset ();
    sha.update (challenge_string.c_str (), challenge_string.length ());
    sha.finalize (hash, HASH_SIZE);


    // sends answer back to blockchain
    String pair;
    for (int i=0; i<sizeof (hash); i++) {
      pair = String (hash [i], HEX);
      if (pair.length ()<2) pair = "0"+pair;
      Serial.print (pair);
    }
    Serial.print ('\n');
  }
}
