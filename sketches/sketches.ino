#include <FastLED.h>
#define LED_PIN 15
#define NUM_LEDS 1
CRGB leds[NUM_LEDS];

void rgb_led(int r, int g, int b)
{
  leds[0] = CRGB(r, g, b);
  FastLED.show();
}

void setup() 
{
  FastLED.addLeds<NEOPIXEL, LED_PIN>(leds, NUM_LEDS);
  FastLED.clear();
  FastLED.show();
  delay(10);
}

void loop() 
{
  rgb_led(255, 0, 0);
  delay(1000);
  rgb_led(0, 0, 0);
  delay(1000);
}



