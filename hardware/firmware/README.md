# MUSTEM Firmware

## Overview

This directory contains Arduino firmware for both subsystems:
- **Tactile System** (Arduino UNO): 4-channel vibrotactile control
- **Visual System** (Arduino Mega): FFT analysis and TFT display

## Installation

### Tactile System

1. Open `tactile_system/tactile_system.ino` in Arduino IDE
2. Install required libraries: (none required, uses built-in)
3. Select **Board:** Arduino UNO
4. Select **Port:** [your port]
5. Click **Upload**

### Visual System

1. Open `visual_system/visual_display_fft.ino` in Arduino IDE
2. Install required libraries:
```
   Sketch → Include Library → Manage Libraries
   Search and install:
   - Adafruit GFX Library
   - Adafruit TFT LCD Library
   - arduinoFFT
```
3. Select **Board:** Arduino Mega 2560
4. Select **Port:** [your port]
5. Click **Upload**

## Configuration

See comments in each `.ino` file for parameter tuning.