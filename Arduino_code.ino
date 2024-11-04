#include <Servo.h>

Servo fingers[5];
String inp;
int i1 = 0, i2 = 0;
int val;
int angles[] = {0, 0, 0, 0, 0};

void setup() {
  // put your setup code here, to run once:
  fingers[0].attach(5);
  fingers[1].attach(6);
  fingers[2].attach(9);
  fingers[3].attach(10);
  fingers[4].attach(11);

  Serial.begin(9600);
  Serial.setTimeout(30);
}

void loop() {
  // put your main code here, to run repeatedly:
  while(!Serial.available());
  inp = Serial.readStringUntil('\n');
  inp.trim();

  i1 = 0;
  i2 = 0;
  
  if(inp.startsWith("servo")) {

    for(int i = 0; i < 4; i++) {
      i1 = inp.indexOf(':', i2);
      i2 = inp.indexOf('&', i1);

      // Serial.print(i1);
      // Serial.print('\t');
      // Serial.println(i2);

      val = inp.substring(i1+1, i2).toInt();
      angles[i] = val;

      Serial.print(inp.substring(i1+1, i2));
      Serial.print('\t');
    }

    i1 = inp.lastIndexOf(':');
    angles[4] = inp.substring(i1+1).toInt();
    Serial.println(inp.substring(i1+1));

    for(int i = 0; i < 5; i++) {
      fingers[i].write(angles[i]);
      Serial.print(angles[i]);
      Serial.print('\t');
    }
    Serial.println();
  }

}



// servo1:10&servo2:25&servo3:90&servo4:170&servo5:135












