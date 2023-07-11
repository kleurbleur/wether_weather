import netP5.*;
import oscP5.*;

OscP5 oscp5;

color bg;


void oscEvent(OscMessage theMessage){

// Print the address and typetag of the message to the console
//println("OSC Message received! The address pattern is " + theMessage.addrPattern() + ". The typetag is: " + theMessage.typetag());

  if ( theMessage.checkAddrPattern("/saturation") == true ) 
  {
    println("Your attention is at: " + theMessage.get(0).intValue()); 
  }

}

void setup()
{
  size(400,400);
  noStroke();
  colorMode(HSB, 360, 100, 100);
  bg = color(0, 0, 100);
  
  oscp5 = new OscP5(this, 7771);
}

void draw()
{
  background(bg); 
}
