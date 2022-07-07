// bio-chain-collector.ino - a POE/W client for organic resources harvesting
// code by 220 for MP, IV & JG | 2022

#include <Crypto.h>
#include <SHA256.h>
#include <string.h>

#define HASH_SIZE 32

SHA256 sha;

uint8_t hash [HASH_SIZE];

#define pin_voltage A0

String node_id = "0b1b7a78-2a13-4029-ac6b-d6bdbad6e96";
String input = "";

String challenge_response;
int voltage_input;
int voltage_average;

boolean waiting = false;

void setup() {
  Serial.setTimeout (35);
  Serial.begin (115200);
  Serial.flush ();

  pinMode (pin_voltage, INPUT);

  delay (250);
  requestChallenge ();
}
void requestChallenge () {
  // requests new operation and identifies by using node_id
  Serial.print ("NOP:"+node_id);
  Serial.print ('\n');

  waiting = true;
}

void loop() {
  if (Serial.available ()>0) {
    input = Serial.readStringUntil ('\n');
  }
  if (input!="") {
    if (input.indexOf ("CH:")!=-1) {
      // got challenge
      input = input.substring (3);
      solveChallenge (input);
      voltage_average = 0;
      waiting = true;
    } else
    if (input.indexOf ("RQ:0")!=-1) {
      // got challenge response query
      voltage_average/= 4;
      Serial.print ("CHR:"+challenge_response+"|"+voltage_average);
      Serial.print ('\n');
      challenge_response = "";
      waiting = false;
    } else
    if (input.indexOf ("ACK:")!=-1 || input.indexOf ("DROP:")!=-1) {
      requestChallenge ();
    }
    input = "";
  }
  if (waiting) {
    voltage_average+= analogRead (pin_voltage);
    voltage_average/= 2;
  }
}
void solveChallenge (String challenge) {
  // hashes challenge using SHA256 - POE/W
  sha.reset ();
  sha.update (challenge.c_str (), challenge.length ());
  sha.finalize (hash, HASH_SIZE);

  // sends answer back to blockchain
  String pair;
  challenge_response = "";
  for (int i=0; i<sizeof (hash); i++) {
    pair = String (hash [i], HEX);
    if (pair.length ()<2) pair = "0"+pair;
    challenge_response+= pair;
  }
}
