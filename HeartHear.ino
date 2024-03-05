#include <Wire.h>
#include "MAX30105.h"
#include "heartRate.h"
#include <math.h>
#include <PulseSensorPlayground.h> // Includes the PulseSensorPlayground Library.
#include "spo2_algorithm.h"

// variables and constants for ECG chip
PulseSensorPlayground pulseSensor;

int saved_bpm_value_ecg = 0;

// variables and constants for MAX30102
MAX30105 particleSensor;

const byte RATE_SIZE = 4; // Increase this for more averaging. 4 is good.
byte rates[RATE_SIZE];    // Array of heart rates
byte rateSpot = 0;
long lastBeat = 0; // Time at which the last beat occurred

float beatsPerMinute;
int beatAvg;

// variables and constants for EOG
int data_index = 0;
float signal = 0;

unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 50;

unsigned long last_minute_start_time = 0;
unsigned int blink_count = 0;
bool drowsy = false;

void setup()
{
  Serial.begin(115200);
  // Serial.println("Initializing...");

  // Configure the PulseSensor object, by assigning our variables to it.
  pulseSensor.analogInput(1); // ECG connected to A1 port
  pulseSensor.setThreshold(550);

  // Double-check the "pulseSensor" object was created and "began" seeing a signal.
  if (pulseSensor.begin())
  {
    // Serial.println("We created a pulseSensor Object !"); // This prints one time at Arduino power-up,  or on Arduino reset.
  }

  // Setup input pin for EOG (A0)
  pinMode(A0, INPUT);

  // Initialize last_minute_start_time to current time
  last_minute_start_time = millis();

  // Initialize MAX30102 sensor
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST))
  {
    // Serial.println("MAX30102 was not found. Please check wiring/power. ");
    // while (1)
    //   ;
  }
  // Serial.println("Place your index finger on the sensor with steady pressure.");

  particleSensor.setup();                    // Configure sensor with default settings
  particleSensor.setPulseAmplitudeRed(0x0A); // Turn Red LED to low to indicate sensor is running
  particleSensor.setPulseAmplitudeGreen(0);  // Turn off Green LED
}

void loop()
{

  // Calculate elapsed time
  unsigned long present_time = millis();

  // Sample
  float sensor_value = analogRead(A0);
  float signal = EOGFilter(sensor_value) / 5.12;

  // Check if a blink is detected, which occurs when eog sensor is >= 0.5
  if (signal >= 0.5 && present_time - last_minute_start_time > 1000)
  {
    blink_count++;
  }

  // Check if a minute has passed
  if (present_time - last_minute_start_time > 60000)
  {
    // Check if the blink count is below the threshold, which is currently 6  blinks per minute
    drowsy = (blink_count <= 6);

    // Reset blink count and update last_minute_start_time
    blink_count = 0;
    last_minute_start_time = present_time;
  }

  // output eog data to serial
  Serial.print(signal);
  Serial.print(" ");
  Serial.print(drowsy);
  Serial.print(" ");

  // MAX30102 get data
  long irValue = particleSensor.getIR();
  long redValue = particleSensor.getRed();

  if (checkForBeat(irValue) == true)
  {
    // We sensed a beat!
    long delta = millis() - lastBeat;
    lastBeat = millis();

    beatsPerMinute = 60 / (delta / 1000.0);

    if (beatsPerMinute < 255 && beatsPerMinute > 20)
    {
      rates[rateSpot++] = (byte)beatsPerMinute; // Store this reading in the array
      rateSpot %= RATE_SIZE;                    // Wrap variable

      // Take average of readings
      beatAvg = 0;
      for (byte x = 0; x < RATE_SIZE; x++)
        beatAvg += rates[x];
      beatAvg /= RATE_SIZE;
    }
  }

  Serial.print(irValue);
  Serial.print(" ");
  Serial.print(redValue);
  Serial.print(" ");
  Serial.print(beatAvg);
  Serial.print(" ");

  // Gather ECG Data
  if (pulseSensor.sawStartOfBeat())
  {
    int myBPM = pulseSensor.getBeatsPerMinute();
    saved_bpm_value_ecg = myBPM;
  };

  // Serial.print(" ");
  // Serial.println(saved_bpm_value_ecg);

  Serial.println();

  delay(10);
}

float lowpass_filter(float input, float prev_output, float alpha)
{
  return alpha * input + (1 - alpha) * prev_output;
}

float highpass_filter(float input, float prev_input, float prev_output, float alpha)
{
  return alpha * prev_output + alpha * (input - prev_input);
}

float notch_filter(float input, float prev_output, float prev_prev_output, float alpha)
{
  return 2 * prev_output - prev_prev_output + alpha * (input - 2 * prev_output + prev_prev_output);
}

float EOGFilter(float input)
{
  static float prev_output_lowpass = 0.0;
  static float prev_input_highpass = 0.0;
  static float prev_output_highpass = 0.0;
  static float prev_output_notch = 0.0;
  static float prev_prev_output_notch = 0.0;

  // Constants for filter coefficients
  const float alpha_lowpass = 0.0111111; // 2Hz cutoff
  const float alpha_highpass = 0.678;    // 10Hz cutoff
  const float alpha_notch = 0.9375;      // 60Hz notch

  // Apply low-pass filter
  float lowpass_output = lowpass_filter(input, prev_output_lowpass, alpha_lowpass);

  // Apply high-pass filter
  float highpass_output = highpass_filter(lowpass_output, prev_input_highpass, prev_output_highpass, alpha_highpass);

  // Apply notch filter
  float notch_output = notch_filter(highpass_output, prev_output_notch, prev_prev_output_notch, alpha_notch);

  // Update previous values
  prev_output_lowpass = lowpass_output;
  prev_input_highpass = lowpass_output;
  prev_output_highpass = highpass_output;
  prev_prev_output_notch = prev_output_notch;
  prev_output_notch = notch_output;

  return notch_output;
}
