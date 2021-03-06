// Neopixel serial slave: receive commands from a serial via usb host.

// Based on:
// NeoPixel Ring simple sketch (c) 2013 Shae Erisson
// released under the GPLv3 license to match the rest of the AdaFruit NeoPixel library

#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
  #include <avr/power.h>
#endif

// Which pin on the Arduino is connected to the NeoPixels?
// On a Trinket or Gemma we suggest changing this to 1
#define PIN            2
#define PIN_SINGLE            3

// How many NeoPixels are attached to the Arduino?
#define NUMPIXELS      128  // I've got two 8x8 's

// When we setup the NeoPixel library, we tell it how many pixels, and which pin to use to send signals.
// Note that for older NeoPixel strips you might need to change the third parameter--see the strandtest
// example for more information on possible values.
Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel single_pixel = Adafruit_NeoPixel(3, PIN_SINGLE, NEO_GRB + NEO_KHZ800);

//int delayval = 100;
int i;   //idx for pixel
  
void setup() {
  // This is for Trinket 5V 16MHz, you can remove these three lines if you are not using a Trinket
#if defined (__AVR_ATtiny85__)
  if (F_CPU == 16000000) clock_prescale_set(clock_div_1);
#endif
  // End of trinket special code
  single_pixel.begin();
  pixels.begin(); // This initializes the NeoPixel library.
  single_pixel.setPixelColor(0, pixels.Color(5,0,0));
  single_pixel.setPixelColor(1, pixels.Color(4,2,0));
  single_pixel.setPixelColor(2, pixels.Color(0,5,0));
  single_pixel.show();
  pixels.setPixelColor(0, pixels.Color(5,0,0));  // initially let the user know that it all works
  pixels.show();
  Serial.begin(115200);
  i = 0;
}


void loop() {
    if (Serial.available() > 2) {
      pixels.setPixelColor(i, pixels.Color(Serial.read(), Serial.read(), Serial.read())); 
      i += 1;
      if (i >= NUMPIXELS) {
        i = 0;
        pixels.show();
      }
    }
}
