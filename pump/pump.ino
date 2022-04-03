// ConstantSpeed.pde
// -*- mode: C++ -*-
//
// Shows how to run AccelStepper in the simplest,
// fixed speed mode with no accelerations
/// \author  Mike McCauley (mikem@airspayce.com)
// Copyright (C) 2009 Mike McCauley
// $Id: ConstantSpeed.pde,v 1.1 2011/01/05 01:51:01 mikem Exp mikem $

#include <AccelStepper.h>
#include <Wire.h>

AccelStepper stepper(AccelStepper::DRIVER, 3, 2); // Defaults to AccelStepper::FULL4WIRE (4 pins) on 2, 3, 4, 5

int channels[8] = {4, 5, 6, 7, 8, 9, 10, 11};

int steps_per_rev = 400;
float revs = 5;

int currentChannel = 255;
byte currentDir = 0x00;
int currentStepsPerML = 0;
int dispenseVal = 0;
long dispenseSteps = 0;
int last_ramp = 0;
bool dispenseRun = false;

void setup()
{  
//  Serial.begin(115200);
//  while(!Serial){
//    ;
//  }
//  Serial.println("Pump Controller init");
  Wire.begin(8);
//  Serial.println("Joined i2c bus at channel 8");
  for(int i = 0; i < 8; i++) {
    pinMode(channels[i], OUTPUT);
    digitalWrite(channels[i], LOW);
  }

  Wire.onReceive(messageReceive);
  Wire.onRequest(requestEvent);
  
    stepper.setMaxSpeed(steps_per_rev * revs);
    stepper.setSpeed(steps_per_rev * revs);
//    stepper.setSpeed(1600);
//  Serial.println(stepper.speed());
}

void requestEvent() {
  if (dispenseRun){
    Wire.write(byte(0x01));
  } else {
    Wire.write(byte(0x00));
  }
  int currentOut = abs(((stepper.currentPosition() / (float)currentStepsPerML) * dispenseVal) / dispenseVal);
  Wire.write(highByte(currentOut));
  Wire.write(lowByte(currentOut));
}

void messageReceive(int numBytes)
{
//  Serial.print("Received message of length: ");
//  Serial.println(numBytes);
  // message structure: byte[0] = channel(0-7), byte[1] = direction(0x00 STOP, 0x01 FWD, 0x02 REV), byte[2-3] = steps/ml, byte[4-5] = dispense value
  if(numBytes != 7) {
    while(Wire.available()){
      Wire.read();
    }
//    Serial.println();
    return;
  }
  byte tempSteps[2] = {0x00, 0x00};
  byte tempDispense[2] = {0x00, 0x00};
  byte tempChannel = 0x00;
  byte tempDir = 0x00;
  while(Wire.available()){
    Wire.read(); // throw out register
    tempChannel = Wire.read();
    tempDir = Wire.read();
    tempSteps[0] = Wire.read();
    tempSteps[1] = Wire.read();

    tempDispense[0] = Wire.read();
    tempDispense[1] = Wire.read();
  }
  currentChannel = tempChannel;
  currentDir = tempDir;
  currentStepsPerML = byteCombine(tempSteps[0], tempSteps[1]);
  dispenseVal = byteCombine(tempDispense[0], tempDispense[1]);

  if (currentDir == 0x00) {
    pumpStop();
  } else {
    pumpStart();
  }
}

void pumpStop()
{
//  Serial.println("Pump stop called\n");
//  Serial.print("Channel to stop: ");
//  Serial.println(currentChannel);
//  Serial.println();
  currentChannel = 255;
  dispenseRun = false;
  for(int i = 0; i < 8; i++) {
    digitalWrite(channels[i], HIGH);
  }
}

void pumpStart()
{
//  Serial.println("Pump start called\n");
//  Serial.print("Channel to start: ");
//  Serial.println(currentChannel);
//  Serial.print("Direction: ");
//  Serial.println(currentDir);
//  Serial.print("Cal val: ");
//  Serial.println(currentStepsPerML);
//  Serial.print("Dispense: ");
//  Serial.println(dispenseVal);
//  Serial.println();
  dispenseSteps = (long)currentStepsPerML * (long)dispenseVal;
//  Serial.print(dispenseSteps);
//  Serial.println(" steps to dispense");
  stepper.setCurrentPosition(0);
  for(int i = 0; i < 8; i++) {
    if(i == currentChannel) {
      digitalWrite(channels[i], LOW);
    } else {
      digitalWrite(channels[i], HIGH);
    }
  }
  last_ramp = 0;
  if(currentDir == 0x02){
    stepper.moveTo(-dispenseSteps);
    stepper.setSpeed(-200);
  } else {
    stepper.moveTo(dispenseSteps);
    stepper.setSpeed(200);    
  }
  dispenseRun = true;
}

int byteCombine(byte high, byte low)
{
  int combined;
  combined = high;
  combined = combined<<8;
  combined |= low;

  return combined;
}

void ramp(){
  float revs_per = (steps_per_rev * revs);
  float current_speed = stepper.speed();
  if (current_speed == revs_per){
    return;
  }
  if ((stepper.currentPosition() - last_ramp) > 30) {
      last_ramp = stepper.currentPosition();
      float new_speed = current_speed * 1.1;
      if (new_speed > revs_per) {
        new_speed = revs_per;
      }
//      Serial.print("Ramp up: ");
//      Serial.println(new_speed);
      stepper.setSpeed(new_speed);
  }
}

void loop(){
  if (currentChannel == 255){
    return;
  }

  if(dispenseRun){
    ramp();
//    Serial.println(stepper.speed());
    stepper.runSpeedToPosition();
//    if((stepper.currentPosition() % 500) == 0){
//      Serial.print("Channel: ");
//      Serial.print(currentChannel);
//      Serial.print(" Pin num: ");
//      Serial.print(channels[currentChannel]);
//      Serial.print(" Out: ");
//      Serial.print(stepper.currentPosition());
//      Serial.print("/");
//      Serial.print(dispenseSteps);
//      Serial.print(" steps - ");
//      Serial.print(((stepper.currentPosition() / (float)currentStepsPerML) * dispenseVal) / dispenseVal);
//      Serial.print("/");
//      Serial.print(dispenseVal);
//      Serial.print(" - speed: ");
//      Serial.println(stepper.speed());
//    }
    if(abs(stepper.currentPosition()) >= dispenseSteps) {
      pumpStop();
    }
  }
}
