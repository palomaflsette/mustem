// #include <MCUFRIEND_kbv.h>
// #include <Adafruit_GFX.h>
// #include <arduinoFFT.h>

// MCUFRIEND_kbv tft;

// // ============================================================================
// // PARÂMETROS CIENTÍFICOS FUNDAMENTADOS
// // ============================================================================

// // Audio Sampling (baseado em Teorema de Nyquist)
// #define SAMPLING_FREQ 4000              // 10kHz sample rate
// #define FFT_SAMPLES 512                  // 128-point FFT
// #define SAMPLE_PERIOD_US (1000000UL / SAMPLING_FREQ)  // 100 µs

// // Screen
// #define SCREEN_WIDTH 320
// #define SCREEN_HEIGHT 240
// #define ELETRETO_PIN A6

// #ifndef log2
//   #define log2(x) (log(x) / 0.69314718056)
// #endif

// // Psychoacoustic Frequency Bands (Fletcher-Munson + Bark scale)
// struct FrequencyBands {
//   float SUBBASS_LOW = 20.0;
//   float SUBBASS_HIGH = 60.0;
//   float BASS_LOW = 60.0;
//   float BASS_HIGH = 250.0;
//   float LOWMID_LOW = 250.0;
//   float LOWMID_HIGH = 500.0;
//   float MID_LOW = 500.0;
//   float MID_HIGH = 2000.0;
//   float HIGHMID_LOW = 2000.0;
//   float HIGHMID_HIGH = 4000.0;
//   float TREBLE_LOW = 4000.0;
//   float TREBLE_HIGH = 8000.0;
// };

// FrequencyBands FREQ_BANDS;

// // Stevens Power Law for haptic mapping
// const float STEVENS_EXPONENT = 0.67;

// // Beat detection parameters (based on literature)
// const float ONSET_THRESHOLD_MULTIPLIER = 1.5;     // k*sigma above mean
// const unsigned long MIN_ONSET_INTERVAL_MS = 150;  // 400 BPM max

// // Silence detection
// float SILENCE_ENERGY_THRESHOLD = 50.0;      // Calibrated for electret mic
// const unsigned long SILENCE_TIMEOUT_MS = 2000;


// bool thresholdCalibrated = false;
// float ambientNoiseLevel = 0.0;

// // ============================================================================
// // FFT BUFFERS AND INSTANCE
// // ============================================================================

// float vReal[FFT_SAMPLES];
// float vImag[FFT_SAMPLES];
// ArduinoFFT<float> FFT(vReal, vImag, FFT_SAMPLES, SAMPLING_FREQ);

// // ============================================================================
// // DATA STRUCTURES
// // ============================================================================

// struct AudioAnalysis {
//   float dominantFreq;
//   float peakMagnitude;
//   float totalEnergy;
//   float rms;
//   unsigned long lastUpdate;
//   bool isActive;
// };

// struct SpectrumData {
//   float bands[6];           // 6 psycoacoustic bands
//   float smoothedBands[6];
//   float smoothingFactor;    // IIR filter coefficient
//   unsigned long lastUpdate;
  
//   SpectrumData() : smoothingFactor(0.3) {
//     for (int i = 0; i < 6; i++) {
//       bands[i] = 0.0;
//       smoothedBands[i] = 0.0;
//     }
//     lastUpdate = 0;
//   }
// };

// struct BeatDetector {
//   float energyHistory[16];
//   int historyIndex;
//   float currentStrength;
//   unsigned long lastOnset;
//   unsigned long lastAnalysis;
  
//   BeatDetector() : historyIndex(0), currentStrength(0.0), 
//                    lastOnset(0), lastAnalysis(0) {
//     for (int i = 0; i < 16; i++) {
//       energyHistory[i] = 0.0;
//     }
//   }
  
//   bool detectOnset(float currentEnergy, unsigned long currentTime) {
//     // Calculate mean
//     float mean = 0.0;
//     for (int i = 0; i < 16; i++) {
//       mean += energyHistory[i];
//     }
//     mean /= 16.0;
    
//     // Calculate standard deviation
//     float variance = 0.0;
//     for (int i = 0; i < 16; i++) {
//       float diff = energyHistory[i] - mean;
//       variance += diff * diff;
//     }
//     float stdDev = sqrt(variance / 16.0);
    
//     // Adaptive threshold
//     float threshold = mean + ONSET_THRESHOLD_MULTIPLIER * stdDev;
    
//     // Detect onset
//     bool isOnset = false;
//     if (currentEnergy > threshold && 
//         (currentTime - lastOnset) > MIN_ONSET_INTERVAL_MS) {
//       isOnset = true;
//       currentStrength = min(1.0, (currentEnergy - mean) / (stdDev + 0.1));
//       lastOnset = currentTime;
//     } else {
//       currentStrength *= 0.85; // Exponential decay
//     }
    
//     // Update history
//     energyHistory[historyIndex] = currentEnergy;
//     historyIndex = (historyIndex + 1) % 16;
    
//     return isOnset;
//   }
// };

// struct WindingVisualizer {
//   float phase;
//   float rotationSpeed;
//   int pointCount;
//   unsigned long lastUpdate;
//   unsigned long lastClear;
  
//   // Phyllotaxis parameters (Golden Ratio spiral)
//   const float GOLDEN_ANGLE = 2.39996323; // 137.5° in radians
//   const int MAX_POINTS = 200;
  
//   WindingVisualizer() : phase(0.0), rotationSpeed(0.0), pointCount(0),
//                         lastUpdate(0), lastClear(0) {}
// };

// // Global instances
// AudioAnalysis audio;
// SpectrumData spectrum;
// BeatDetector beatDetect;
// WindingVisualizer winding;

// // Silence state
// bool isInSilence = false;
// unsigned long lastAudioDetectedTime = 0;

// // Timing intervals (empirically optimized for balance)
// const unsigned long FFT_INTERVAL_MS = 50;         // 20 Hz (FFT is expensive)
// const unsigned long SPECTRUM_UPDATE_MS = 100;     // 10 Hz
// const unsigned long WINDING_UPDATE_MS = 40;       // 25 Hz
// const unsigned long BEAT_DETECT_MS = 100;         // 10 Hz
// const unsigned long WINDING_CLEAR_MS = 8000;      // 8 seconds

// // ============================================================================
// // SETUP
// // ============================================================================


// // ============================================================================
// // AUTO-CALIBRATION
// // ============================================================================

// void calibrateSilenceThreshold() {
//   Serial.println("\n=== CALIBRANDO THRESHOLD DE SILÊNCIO ===");
//   Serial.println("Mantenha o ambiente SILENCIOSO por 3 segundos...");
  
//   tft.fillScreen(0x0000);
//   tft.setTextSize(2);
//   tft.setTextColor(0xFFE0); // Yellow
//   tft.setCursor(30, 100);
//   tft.print("Calibrando...");
//   tft.setCursor(20, 130);
//   tft.print("Mantenha silencio");
  
//   delay(1000); // Dar tempo para estabilizar
  
//   // Coletar amostras de ruído ambiente
//   const int NUM_SAMPLES = 30;
//   float noiseSamples[NUM_SAMPLES];
  
//   for (int i = 0; i < NUM_SAMPLES; i++) {
//     // Fazer FFT simples
//     unsigned long startTime = micros();
    
//     for (int j = 0; j < FFT_SAMPLES; j++) {
//       vReal[j] = analogRead(ELETRETO_PIN);
//       vImag[j] = 0.0;
//       while (micros() - startTime < (j + 1) * SAMPLE_PERIOD_US) {}
//     }
    
//     // Remove DC offset
//     float dcOffset = 0.0;
//     for (int j = 0; j < FFT_SAMPLES; j++) {
//       dcOffset += vReal[j];
//     }
//     dcOffset /= FFT_SAMPLES;
    
//     for (int j = 0; j < FFT_SAMPLES; j++) {
//       vReal[j] -= dcOffset;
//     }
    
//     // FFT
//     FFT.windowing(FFTWindow::Hamming, FFTDirection::Forward);
//     FFT.compute(FFTDirection::Forward);
//     FFT.complexToMagnitude();

//     // ===== FILTRO DE FAIXA: remove DC e infrassom residual, corta >4 kHz =====
//     float freqResolution = (float)SAMPLING_FREQ / FFT_SAMPLES;  // 4000/256 ≈ 15.625 Hz
//     vReal[0] = 0.0;   // DC
//     vReal[1] = 0.0;   // ~15.6 Hz (ajuda a estabilizar silêncio)
//     int minBin = 2;   // começa a procurar pico a partir daqui

//     int maxBin = (int)(4000.0 / freqResolution);  // low-pass em 4 kHz
//     if (maxBin > (FFT_SAMPLES/2)) maxBin = FFT_SAMPLES/2;
//     for (int i = maxBin; i < FFT_SAMPLES/2; i++) vReal[i] = 0.0;

    
//     // Calcular energia
//     float energy = 0.0;
//     for (int j = 1; j < FFT_SAMPLES / 2; j++) {
//       energy += vReal[j];
//     }
    
//     noiseSamples[i] = energy;
    
//     // Progresso visual
//     if (i % 10 == 0) {
//       tft.fillRect(50 + i * 7, 160, 5, 10, 0x07E0); // Green bar
//     }
    
//     delay(100);
//   }
  
//   // Calcular estatísticas do ruído
//   float mean = 0.0;
//   for (int i = 0; i < NUM_SAMPLES; i++) {
//     mean += noiseSamples[i];
//   }
//   mean /= NUM_SAMPLES;
  
//   float variance = 0.0;
//   for (int i = 0; i < NUM_SAMPLES; i++) {
//     float diff = noiseSamples[i] - mean;
//     variance += diff * diff;
//   }
//   float stdDev = sqrt(variance / NUM_SAMPLES);
  
//   // Threshold = média + 3*sigma (99.7% de confiança)
//   ambientNoiseLevel = mean;
//   SILENCE_ENERGY_THRESHOLD = mean + 3.0 * stdDev;
  
//   // Garantir mínimo
//   if (SILENCE_ENERGY_THRESHOLD < 50.0) {
//     SILENCE_ENERGY_THRESHOLD = 50.0;
//   }
  
//   thresholdCalibrated = true;
  
//   Serial.print("Ruído ambiente (média): ");
//   Serial.println(mean, 1);
//   Serial.print("Desvio padrão: ");
//   Serial.println(stdDev, 1);
//   Serial.print("THRESHOLD definido em: ");
//   Serial.println(SILENCE_ENERGY_THRESHOLD, 1);
  
//   // Mostrar resultado
//   tft.fillScreen(0x0000);
//   tft.setTextSize(2);
//   tft.setTextColor(0x07E0); // Green
//   tft.setCursor(40, 90);
//   tft.print("Calibrado!");
  
//   tft.setTextSize(1);
//   tft.setTextColor(0xFFFF);
//   tft.setCursor(30, 130);
//   tft.print("Threshold: ");
//   tft.print((int)SILENCE_ENERGY_THRESHOLD);
  
//   tft.setCursor(30, 150);
//   tft.print("Ruido medio: ");
//   tft.print((int)ambientNoiseLevel);
  
//   delay(2000);
//   tft.fillScreen(0x0000);
  
//   Serial.println("=== CALIBRAÇÃO CONCLUÍDA ===\n");
// }

// void setup() {
//   Serial.begin(115200);
  
//   // Initialize TFT
//   uint16_t ID = tft.readID();
//   if (ID == 0xD3D3) ID = 0x9481;
//   tft.begin(ID);
//   tft.setRotation(1);
//   tft.fillScreen(0x0000);
  
//   // Configure ADC for maximum speed
//   analogReference(DEFAULT);
  
//   // Initialize structures
//   audio.lastUpdate = 0;
//   audio.isActive = false;
  
//   // Welcome screen
//   showWelcomeScreen();
  
//   // *** CALIBRAÇÃO AUTOMÁTICA ***
//   calibrateSilenceThreshold();
  
//   Serial.println("MUSTEM - Scientifically Grounded Audio Visualization");
//   Serial.println("FFT Resolution: " + String(SAMPLING_FREQ / FFT_SAMPLES) + " Hz");
// }

// // ============================================================================
// // AUDIO ANALYSIS FUNCTIONS
// // ============================================================================

// // ============================================================================
// // AUDIO ANALYSIS FUNCTIONS
// // ============================================================================

// void performFFTAnalysis(unsigned long currentTime) {
//   // ===== 1) Coleta de amostras =====
//   unsigned long startTime = micros();
//   for (int i = 0; i < FFT_SAMPLES; i++) {
//     vReal[i] = analogRead(ELETRETO_PIN);
//     vImag[i] = 0.0f;
//     // tentativa de espaçamento uniforme (ideal: ADC free-running + ISR)
//     while (micros() - startTime < (unsigned long)((i + 1) * SAMPLE_PERIOD_US)) { }
//   }

//   // ===== 2) Remoção de DC =====
//   float dcOffset = 0.0f;
//   for (int i = 0; i < FFT_SAMPLES; i++) dcOffset += vReal[i];
//   dcOffset /= (float)FFT_SAMPLES;
//   for (int i = 0; i < FFT_SAMPLES; i++) vReal[i] -= dcOffset;

//   // ===== 3) FFT =====
//   FFT.windowing(FFTWindow::Hamming, FFTDirection::Forward);
//   FFT.compute(FFTDirection::Forward);
//   FFT.complexToMagnitude();

//   // ===== 4) Preparação espectral (faixa útil, piso, pico) =====
//   float freqResolution = (float)SAMPLING_FREQ / (float)FFT_SAMPLES; // ≈15.625 Hz (com 4 kHz / 256)
//   vReal[0] = 0.0f;   // remove DC
//   vReal[1] = 0.0f;   // reduz drift/infragraves
//   int minBin = 2;

//   int maxBin = (int)(4000.0f / freqResolution);
//   if (maxBin > FFT_SAMPLES / 2) maxBin = FFT_SAMPLES / 2;

//   // Piso espectral (média e sigma nos bins úteis)
//   float mean = 0.0f, var = 0.0f;
//   int cnt = 0;
//   for (int i = minBin; i < maxBin; i++) { mean += vReal[i]; cnt++; }
//   if (cnt <= 0) cnt = 1;
//   mean /= (float)cnt;
//   for (int i = minBin; i < maxBin; i++) { float d = vReal[i] - mean; var += d * d; }
//   float sigma = sqrtf(var / (float)cnt);

//   // Pico bruto (com leve suavização nos graves)
//   float peakMag = 0.0f;
//   int   peakBin = minBin;
//   for (int i = minBin + 1; i < maxBin - 1; i++) {
//     float m = vReal[i];
//     float f = i * freqResolution;
//     if (f < 400.0f) {
//       m = 0.25f * vReal[i - 1] + 0.5f * vReal[i] + 0.25f * vReal[i + 1];
//     }
//     if (m > peakMag) { peakMag = m; peakBin = i; }
//   }

//   // Aceita pico só se acima do piso por k·σ
//   const float SPEC_K = 3.0f;
//   bool hasPeak = (peakMag > mean + SPEC_K * sigma);

//   static bool  freqInit = false;
//   static float smoothedFreq = 0.0f;

//   if (!hasPeak) {
//     // Nada confiável ⇒ estado de silêncio
//     audio.isActive = false;
//     audio.peakMagnitude = 0.0f;
//     audio.totalEnergy = 0.0f;
//     audio.rms = 0.0f;
//     audio.dominantFreq = 0.0f;
//     audio.lastUpdate = currentTime;
//     return;
//   }

//   // ===== 5) Interpolação parabólica do pico =====
//   float detectedFreq = peakBin * freqResolution;
//   float a = vReal[peakBin - 1], b = vReal[peakBin], c = vReal[peakBin + 1];
//   if (b > a && b > c) {
//     float p = 0.5f * (a - c) / (a - 2.0f * b + c);
//     detectedFreq = (peakBin + p) * freqResolution;
//   }

//   // ===== 6) Suavização temporal da frequência =====
//   if (!freqInit) { smoothedFreq = detectedFreq; freqInit = true; }
//   const float FREQ_SMOOTHING = 0.30f;
//   smoothedFreq = FREQ_SMOOTHING * detectedFreq + (1.0f - FREQ_SMOOTHING) * smoothedFreq;
//   float newFreq = constrain(smoothedFreq, 30.0f, 4000.0f);

//   // ===== 7) Energia/RMS =====
//   audio.totalEnergy = 0.0f;
//   for (int i = minBin; i < maxBin; i++) audio.totalEnergy += vReal[i];
//   audio.rms = sqrtf(audio.totalEnergy / (float)(maxBin - minBin));
//   audio.peakMagnitude = peakMag;

//   // ===== 8) Gating de atividade (com seu threshold calibrado) =====
//   float frequencyFactor = (newFreq < 150.0f) ? 1.5f : ((newFreq > 2000.0f) ? 1.2f : 1.0f);
//   float activationThreshold   = SILENCE_ENERGY_THRESHOLD * frequencyFactor * 1.3f;
//   float deactivationThreshold = SILENCE_ENERGY_THRESHOLD * frequencyFactor * 0.7f;

//   static bool wasActive = false;
//   static int consecutiveSilentFrames = 0, consecutiveActiveFrames = 0;

//   bool currentlyHasEnergy = (audio.totalEnergy > activationThreshold);

//   if (currentlyHasEnergy) {
//     consecutiveActiveFrames++; consecutiveSilentFrames = 0;
//     if (consecutiveActiveFrames >= 2) { audio.isActive = true; wasActive = true; }
//   } else if (audio.totalEnergy < deactivationThreshold) {
//     consecutiveSilentFrames++; consecutiveActiveFrames = 0;
//     if (consecutiveSilentFrames >= 5) { audio.isActive = false; wasActive = false; }
//   } else {
//     if (wasActive) audio.isActive = true;
//   }

//   if (audio.isActive) {
//     audio.dominantFreq = newFreq;
//     lastAudioDetectedTime = currentTime;
//   } else {
//     audio.dominantFreq = 0.0f; // não exibir “freq” em silêncio
//   }

//   audio.lastUpdate = currentTime;

//   // ===== 9) DEBUG (1 Hz) =====
//   static unsigned long lastDebug = 0;
//   if (currentTime - lastDebug > 1000) {
//     if (audio.isActive && audio.dominantFreq > 0.0f) {
//       Serial.print("Freq: "); Serial.print((int)audio.dominantFreq); Serial.print(" Hz");
//     } else {
//       Serial.print("Freq: --");
//     }
//     Serial.print(" | Mag: ");    Serial.print((int)audio.peakMagnitude);
//     Serial.print(" | Energy: "); Serial.print((int)audio.totalEnergy);
//     Serial.print(" | Active: "); Serial.println(audio.isActive ? "YES" : "NO");
//     lastDebug = currentTime;
//   }
// }


// void updateSpectrumBands(unsigned long currentTime) {
//   if (!audio.isActive) return;
  
//   // Map FFT bins to psychoacoustic frequency bands
//   float freqResolution = (float)SAMPLING_FREQ / FFT_SAMPLES;  // 78.125 Hz
  
//   // Clear bands
//   for (int i = 0; i < 6; i++) {
//     spectrum.bands[i] = 0.0;
//   }
  
//   // Accumulate magnitudes for each band
//   for (int i = 1; i < FFT_SAMPLES / 2; i++) {
//     float binFreq = i * freqResolution;
//     float magnitude = vReal[i];
    
//     // Assign to appropriate band
//     if (binFreq >= FREQ_BANDS.SUBBASS_LOW && binFreq < FREQ_BANDS.SUBBASS_HIGH) {
//       spectrum.bands[0] += magnitude;
//     }
//     else if (binFreq >= FREQ_BANDS.BASS_LOW && binFreq < FREQ_BANDS.BASS_HIGH) {
//       spectrum.bands[1] += magnitude;
//     }
//     else if (binFreq >= FREQ_BANDS.LOWMID_LOW && binFreq < FREQ_BANDS.LOWMID_HIGH) {
//       spectrum.bands[2] += magnitude;
//     }
//     else if (binFreq >= FREQ_BANDS.MID_LOW && binFreq < FREQ_BANDS.MID_HIGH) {
//       spectrum.bands[3] += magnitude;
//     }
//     else if (binFreq >= FREQ_BANDS.HIGHMID_LOW && binFreq < FREQ_BANDS.HIGHMID_HIGH) {
//       spectrum.bands[4] += magnitude;
//     }
//     else if (binFreq >= FREQ_BANDS.TREBLE_LOW && binFreq < FREQ_BANDS.TREBLE_HIGH) {
//       spectrum.bands[5] += magnitude;
//     }
//   }
  
//   // Normalize by number of bins in each band
//   int binCounts[6] = {
//     (FREQ_BANDS.SUBBASS_HIGH - FREQ_BANDS.SUBBASS_LOW) / freqResolution,
//     (FREQ_BANDS.BASS_HIGH - FREQ_BANDS.BASS_LOW) / freqResolution,
//     (FREQ_BANDS.LOWMID_HIGH - FREQ_BANDS.LOWMID_LOW) / freqResolution,
//     (FREQ_BANDS.MID_HIGH - FREQ_BANDS.MID_LOW) / freqResolution,
//     (FREQ_BANDS.HIGHMID_HIGH - FREQ_BANDS.HIGHMID_LOW) / freqResolution,
//     (FREQ_BANDS.TREBLE_HIGH - FREQ_BANDS.TREBLE_LOW) / freqResolution
//   };
  
//   for (int i = 0; i < 6; i++) {
//     if (binCounts[i] > 0) {
//       spectrum.bands[i] /= binCounts[i];
//     }
    
//     // Apply IIR smoothing filter
//     spectrum.smoothedBands[i] = spectrum.smoothingFactor * spectrum.bands[i] + 
//                                  (1.0 - spectrum.smoothingFactor) * spectrum.smoothedBands[i];
    
//     // Normalize to [0, 1]
//     spectrum.smoothedBands[i] = constrain(spectrum.smoothedBands[i] / 100.0, 0.0, 1.0);
//   }
  
//   spectrum.lastUpdate = currentTime;
// }

// // ============================================================================
// // SCIENTIFIC MAPPING FUNCTIONS
// // ============================================================================

// // Frequency to Color (Logarithmic Musical Mapping)
// // Frequency to Color (Logarithmic Musical Mapping)
// uint16_t frequencyToColorLogarithmic(float freq) {
//   const float A1 = 55.0;      // Nota mais grave de referência
//   const float A7 = 3520.0;    // Nota mais aguda de referência
//   const float SEMITONES_PER_OCTAVE = 12.0;
//   const float HUE_RANGE = 360.0;  // ← MUDOU DE 300 PARA 360 (círculo completo)
  
//   // Limitar à faixa válida (7 oitavas: A1 a A7)
//   freq = constrain(freq, A1, A7);
  
//   // Calcular posição logarítmica
//   float semitonesFromA1 = SEMITONES_PER_OCTAVE * log2(freq / A1);
  
//   // Normalizar para [0, 1] dentro de 7 oitavas (84 semitons)
//   float normalizedPosition = semitonesFromA1 / 84.0;
//   normalizedPosition = constrain(normalizedPosition, 0.0, 1.0);
  
//   // Mapear para matiz (hue) com offset para começar no vermelho
//   float hue = normalizedPosition * HUE_RANGE;
  
//   // Ajustar saturação e valor baseado na energia (para mais vivacidade)
//   float saturation = 0.95; // Alta saturação
//   float value = 0.90;      // Brilho alto
  
//   return hsvToRgb565(hue, saturation, value);
// }

// // HSV to RGB565 conversion
// uint16_t hsvToRgb565(float h, float s, float v) {
//   float c = v * s;
//   float x = c * (1.0 - fabs(fmod(h / 60.0, 2.0) - 1.0));
//   float m = v - c;
  
//   float r, g, b;
//   int hi = (int)(h / 60.0) % 6;
  
//   switch(hi) {
//     case 0: r = c; g = x; b = 0; break;
//     case 1: r = x; g = c; b = 0; break;
//     case 2: r = 0; g = c; b = x; break;
//     case 3: r = 0; g = x; b = c; break;
//     case 4: r = x; g = 0; b = c; break;
//     case 5: r = c; g = 0; b = x; break;
//     default: r = 0; g = 0; b = 0; break;
//   }
  
//   uint8_t red = (uint8_t)((r + m) * 255);
//   uint8_t green = (uint8_t)((g + m) * 255);
//   uint8_t blue = (uint8_t)((b + m) * 255);
  
//   return tft.color565(red, green, blue);
// }

// // Amplitude to Haptic Intensity (Stevens Power Law)
// int amplitudeToHapticPWM(float amplitude) {
//   amplitude = constrain(amplitude, 0, 1023);
//   float normalized = amplitude / 1023.0;
  
//   float perceived = pow(normalized, STEVENS_EXPONENT);
  
//   const int MIN_PWM = 30;   // Motor activation threshold
//   const int MAX_PWM = 255;
  
//   int pwmValue = MIN_PWM + perceived * (MAX_PWM - MIN_PWM);
//   return constrain(pwmValue, 0, 255);
// }

// // Utility: Dim color by factor
// uint16_t dimColor(uint16_t color, float factor) {
//   int r = ((color >> 11) & 0x1F) * factor;
//   int g = ((color >> 5) & 0x3F) * factor;
//   int b = (color & 0x1F) * factor;
//   return tft.color565(r << 3, g << 2, b << 3);
// }

// // ============================================================================
// // VISUALIZATION: PHYLLOTAXIS WINDING
// // ============================================================================

// void updateWindingVisualization(unsigned long currentTime) {
//   if (!audio.isActive) return;
  
//   const float centerX = SCREEN_WIDTH / 2.0;
//   const float centerY = SCREEN_HEIGHT / 2.0;
  
//   // Rotation speed based on frequency (normalized by A440)
//   float freqRatio = audio.dominantFreq / 440.0;
//   winding.rotationSpeed = freqRatio * 0.05; // Empirically tuned for visual appeal
//   winding.phase += winding.rotationSpeed;
  
//   // Radius modulated by RMS amplitude
//   float baseRadius = 40.0;
//   float amplitudeModulation = audio.rms / 50.0; // Normalize RMS
//   float radius = baseRadius + amplitudeModulation * 25.0;
//   radius = constrain(radius, 20.0, 80.0);
  
//   // Beat effect (expansion)
//   if (beatDetect.currentStrength > 0.3) {
//     float beatExpansion = beatDetect.currentStrength * 15.0;
//     radius += beatExpansion;
//   }
  
//   // Color based on dominant frequency
//   uint16_t baseColor = frequencyToColorLogarithmic(audio.dominantFreq);
  
//   // Draw phyllotaxis spiral points
//   const int POINTS_PER_FRAME = 12;
  
//   for (int i = 0; i < POINTS_PER_FRAME; i++) {
//     float angle = winding.pointCount * winding.GOLDEN_ANGLE + winding.phase;
//     float dist = sqrt(winding.pointCount) * 3.0; // Spiral outward
    
//     if (dist > radius) {
//       winding.pointCount = 0; // Reset spiral
//       dist = 0;
//     }
    
//     float x = centerX + dist * cos(angle);
//     float y = centerY + dist * sin(angle);
    
//     x = constrain(x, 0, SCREEN_WIDTH - 1);
//     y = constrain(y, 0, SCREEN_HEIGHT - 1);
    
//     // Fade based on distance from center
//     float fadeFactor = 1.0 - (dist / radius);
//     fadeFactor = constrain(fadeFactor, 0.3, 1.0);
    
//     uint16_t pointColor = dimColor(baseColor, fadeFactor);
    
//     // Draw point (slightly larger for visibility)
//     tft.fillCircle(x, y, 1, pointColor);
    
//     // Connect to previous point occasionally (create web effect)
//     if (winding.pointCount > 0 && winding.pointCount % 5 == 0) {
//       static float lastX = x, lastY = y;
//       tft.drawLine(lastX, lastY, x, y, dimColor(pointColor, 0.5));
//       lastX = x;
//       lastY = y;
//     }
    
//     winding.pointCount++;
//   }
  
//   winding.lastUpdate = currentTime;
// }

// void clearWindingGradually() {
//   // Clear central area with slight blur effect
//   const int clearRadius = 100;
//   const float centerX = SCREEN_WIDTH / 2.0;
//   const float centerY = SCREEN_HEIGHT / 2.0;
  
//   tft.fillCircle(centerX, centerY, clearRadius, 0x0000);
  
//   winding.pointCount = 0;
//   winding.phase = 0.0;
//   winding.lastClear = millis();
// }

// // ============================================================================
// // VISUALIZATION: SPECTRUM ANALYZER
// // ============================================================================

// void drawSpectrumAnalyzer(unsigned long currentTime) {
//   if (!audio.isActive) return;
  
//   const int SPECTRUM_X = SCREEN_WIDTH - 50;
//   const int SPECTRUM_WIDTH = 45;
//   const int SPECTRUM_HEIGHT = SCREEN_HEIGHT - 60;
//   const int SPECTRUM_Y_START = 10;
//   const int BAR_WIDTH = SPECTRUM_WIDTH / 6;
//   const int BAR_SPACING = 1;
  
//   for (int i = 0; i < 6; i++) {
//     int x = SPECTRUM_X + i * (BAR_WIDTH + BAR_SPACING);
    
//     // Calculate bar height
//     float magnitude = spectrum.smoothedBands[i];
//     int barHeight = magnitude * SPECTRUM_HEIGHT;
//     barHeight = constrain(barHeight, 0, SPECTRUM_HEIGHT);
    
//     // Clear previous bar
//     tft.fillRect(x, SPECTRUM_Y_START, BAR_WIDTH, SPECTRUM_HEIGHT, 0x0000);
    
//     // Draw new bar if there's signal
//     if (barHeight > 2) {
//       // Color represents frequency band
//       float bandCenterFreq;
//       if (i == 0) bandCenterFreq = (FREQ_BANDS.SUBBASS_LOW + FREQ_BANDS.SUBBASS_HIGH) / 2;
//       else if (i == 1) bandCenterFreq = (FREQ_BANDS.BASS_LOW + FREQ_BANDS.BASS_HIGH) / 2;
//       else if (i == 2) bandCenterFreq = (FREQ_BANDS.LOWMID_LOW + FREQ_BANDS.LOWMID_HIGH) / 2;
//       else if (i == 3) bandCenterFreq = (FREQ_BANDS.MID_LOW + FREQ_BANDS.MID_HIGH) / 2;
//       else if (i == 4) bandCenterFreq = (FREQ_BANDS.HIGHMID_LOW + FREQ_BANDS.HIGHMID_HIGH) / 2;
//       else bandCenterFreq = (FREQ_BANDS.TREBLE_LOW + FREQ_BANDS.TREBLE_HIGH) / 2;
      
//       uint16_t barColor = frequencyToColorLogarithmic(bandCenterFreq);
      
//       // Draw gradient bar (darker at bottom)
//       for (int y = 0; y < barHeight; y++) {
//         float gradientFactor = 0.3 + 0.7 * (float)y / barHeight;
//         uint16_t gradColor = dimColor(barColor, gradientFactor);
//         tft.drawFastHLine(x, SPECTRUM_Y_START + SPECTRUM_HEIGHT - y, BAR_WIDTH, gradColor);
//       }
      
//       // Peak indicator (bright line at top)
//       uint16_t peakColor = hsvToRgb565(i * 50, 0.9, 1.0); // Bright color
//       tft.drawFastHLine(x, SPECTRUM_Y_START + SPECTRUM_HEIGHT - barHeight, BAR_WIDTH, peakColor);
      
//       // Beat pulse effect
//       if (beatDetect.currentStrength > 0.3) {
//         int pulseWidth = beatDetect.currentStrength * 3;
//         tft.drawRect(x - pulseWidth, SPECTRUM_Y_START + SPECTRUM_HEIGHT - barHeight - pulseWidth, 
//                      BAR_WIDTH + 2*pulseWidth, barHeight + 2*pulseWidth, peakColor);
//       }
//     }
//   }
// }

// // ============================================================================
// // VISUALIZATION: WAVEFORM
// // ============================================================================

// void drawWaveform(unsigned long currentTime) {
//   if (!audio.isActive) return;
  
//   const int WAVE_Y_BASE = SCREEN_HEIGHT - 35;
//   const int WAVE_HEIGHT = 25;
  
//   // Clear wave area
//   tft.fillRect(0, WAVE_Y_BASE - WAVE_HEIGHT, SCREEN_WIDTH, WAVE_HEIGHT * 2, 0x0000);
  
//   // Calculate wave parameters
//   float waveFrequency = map(audio.dominantFreq, 100.0, 2000.0, 20.0, 80.0);
//   waveFrequency = constrain(waveFrequency, 20.0, 80.0);
  
//   float amplitude = (audio.rms / 50.0) * WAVE_HEIGHT;
//   amplitude = constrain(amplitude, 2.0, WAVE_HEIGHT);
  
//   // Beat modulation
//   if (beatDetect.currentStrength > 0.3) {
//     amplitude *= (1.0 + beatDetect.currentStrength * 0.5);
//   }
  
//   // Phase advancement
//   static float wavePhase = 0.0;
//   wavePhase += (audio.dominantFreq / 440.0) * 0.1;
//   if (wavePhase > TWO_PI) wavePhase -= TWO_PI;
  
//   // Color based on frequency
//   uint16_t waveColor = frequencyToColorLogarithmic(audio.dominantFreq);
  
//   // Draw wave
//   int lastY = WAVE_Y_BASE;
//   for (int x = 0; x < SCREEN_WIDTH; x += 2) {
//     float angle = TWO_PI * x / waveFrequency + wavePhase;
//     int y = WAVE_Y_BASE + amplitude * sin(angle);
//     y = constrain(y, WAVE_Y_BASE - WAVE_HEIGHT, WAVE_Y_BASE + WAVE_HEIGHT);
    
//     // Draw line segment
//     if (x > 0) {
//       tft.drawLine(x - 2, lastY, x, y, waveColor);
//     }
    
//     lastY = y;
//   }
// }

// // ============================================================================
// // VISUALIZATION: BEAT INDICATOR
// // ============================================================================

// void drawBeatIndicator(unsigned long currentTime) {
//   const int INDICATOR_X = 15;
//   const int INDICATOR_Y = SCREEN_HEIGHT - 25;
//   const int INDICATOR_RADIUS = 8;
  
//   // Clear area
//   tft.fillCircle(INDICATOR_X, INDICATOR_Y, INDICATOR_RADIUS + 2, 0x0000);
  
//   if (beatDetect.currentStrength > 0.1) {
//     // Pulsing circle
//     int radius = INDICATOR_RADIUS * (0.5 + beatDetect.currentStrength * 0.5);
    
//     // Color intensity based on strength
//     uint8_t intensity = 128 + beatDetect.currentStrength * 127;
//     uint16_t color = tft.color565(intensity, intensity / 2, intensity / 2); // Reddish
    
//     tft.fillCircle(INDICATOR_X, INDICATOR_Y, radius, color);
    
//     // Outer ring
//     if (beatDetect.currentStrength > 0.5) {
//       int ringRadius = INDICATOR_RADIUS + beatDetect.currentStrength * 5;
//       tft.drawCircle(INDICATOR_X, INDICATOR_Y, ringRadius, color);
//     }
//   }
// }


// // ============================================================================
// // MAIN LOOP
// // ============================================================================

// void loop() {
//   unsigned long currentTime = millis();
  
//   // -------------------------------------------------------------------------
//   // 1. AUDIO ANALYSIS (FFT) - Highest priority, fixed interval
//   // -------------------------------------------------------------------------
//   if (currentTime - audio.lastUpdate >= FFT_INTERVAL_MS) {
//     performFFTAnalysis(currentTime);
//   }
  
//   // -------------------------------------------------------------------------
//   // 2. CHECK SILENCE STATE
//   // -------------------------------------------------------------------------
//   checkSilenceState(currentTime);
  
//   if (isInSilence) {
//     updateSilenceAnimation(currentTime);
//     return; // Skip visualizations in silence
//   }
  
//   // -------------------------------------------------------------------------
//   // 3. SPECTRUM BAND ANALYSIS
//   // -------------------------------------------------------------------------
//   if (audio.isActive && currentTime - spectrum.lastUpdate >= SPECTRUM_UPDATE_MS) {
//     updateSpectrumBands(currentTime);
//   }
  
//   // -------------------------------------------------------------------------
//   // 4. BEAT DETECTION
//   // -------------------------------------------------------------------------
//   if (audio.isActive && currentTime - beatDetect.lastAnalysis >= BEAT_DETECT_MS) {
//     beatDetect.detectOnset(audio.totalEnergy, currentTime);
//     beatDetect.lastAnalysis = currentTime;
//   }
  
//   // -------------------------------------------------------------------------
//   // 5. VISUAL UPDATES (when audio is active)
//   // -------------------------------------------------------------------------
//   if (audio.isActive) {
//     // Winding spiral
//     if (currentTime - winding.lastUpdate >= WINDING_UPDATE_MS) {
//       updateWindingVisualization(currentTime);
//     }
    
//     // Spectrum analyzer
//     if (currentTime - spectrum.lastUpdate >= SPECTRUM_UPDATE_MS) {
//       drawSpectrumAnalyzer(currentTime);
//     }
    
//     // Waveform (less frequent for performance)
//     static unsigned long lastWaveUpdate = 0;
//     if (currentTime - lastWaveUpdate >= 50) { // 20 Hz
//       drawWaveform(currentTime);
//       lastWaveUpdate = currentTime;
//     }
    
//     // Beat indicator
//     drawBeatIndicator(currentTime);
    
//     // Periodic winding clear
//     if (currentTime - winding.lastClear >= WINDING_CLEAR_MS) {
//       clearWindingGradually();
//     }
//   }

//   static unsigned long lastDebug = 0;
//   if (millis() - lastDebug > 500) {
//     tft.fillRect(0, 0, 180, 35, 0x0000);
//     tft.setTextSize(1);
//     tft.setTextColor(0xFFFF);
    
//     // Linha 1: Energia
//     tft.setCursor(5, 5);
//     tft.print("E:");
//     tft.print((int)audio.totalEnergy);
//     tft.print(" T:");
//     tft.print((int)SILENCE_ENERGY_THRESHOLD);
    
//     // Linha 2: Frequência detectada
//     tft.setCursor(5, 18);
//     tft.setTextColor(audio.isActive ? 0x07E0 : 0xF800);
//     if (audio.isActive) {
//       tft.print("FREQ: ");
//       tft.print((int)audio.dominantFreq);
//       tft.print(" Hz");
//     } else {
//       tft.print("SILENT");
//     }
    
//     // Linha 3: Cor atual (para debug)
//     tft.setCursor(5, 28);
//     uint16_t currentColor = frequencyToColorLogarithmic(audio.dominantFreq);
//     tft.fillRect(80, 28, 20, 6, currentColor);
//     tft.setTextColor(0xFFFF);
//     tft.print("Color:");
    
//     lastDebug = millis();
//   }
// }

// // ============================================================================
// // SILENCE STATE MANAGEMENT
// // ============================================================================

// void checkSilenceState(unsigned long currentTime) {
//   // Entering silence
//   if (!isInSilence && (currentTime - lastAudioDetectedTime) > SILENCE_TIMEOUT_MS) {
//     isInSilence = true;
//     Serial.println("Entering silence mode");
    
//     // Clear screen gradually
//     tft.fillScreen(0x0000);
//     showSilenceMessage();
//   }
  
//   // Exiting silence
//   if (isInSilence && audio.isActive) {
//     isInSilence = false;
//     Serial.println("Exiting silence mode - audio detected");
    
//     // Clear silence message
//     tft.fillScreen(0x0000);
    
//     // Reset visualization states
//     winding.pointCount = 0;
//     winding.phase = 0.0;
//     winding.lastClear = currentTime;
//   }
// }

// // ============================================================================
// // SILENCE ANIMATION
// // ============================================================================

// // Silence messages
// const char* silenceMessages[] = {
//   "~ Listening ~",
//   "Silence...",
//   "Waiting...",
//   "~ ~ ~",
//   "Quiet",
//   "Still..."
// };
// const int NUM_SILENCE_MESSAGES = 6;

// int currentSilenceMessageIndex = 0;
// float silenceAnimPhase = 0.0;
// unsigned long lastSilenceAnimUpdate = 0;

// void showSilenceMessage() {
//   currentSilenceMessageIndex = (millis() / 1000) % NUM_SILENCE_MESSAGES;
  
//   tft.setTextSize(3);
//   String message = silenceMessages[currentSilenceMessageIndex];
  
//   int textWidth = message.length() * 18;
//   int textX = (SCREEN_WIDTH - textWidth) / 2;
//   int textY = SCREEN_HEIGHT / 2 - 10;
  
//   tft.setTextColor(0x7BEF); // Cyan
//   tft.setCursor(textX, textY);
//   tft.print(message);
// }

// void updateSilenceAnimation(unsigned long currentTime) {
//   // Update animation at 5 Hz
//   if (currentTime - lastSilenceAnimUpdate < 200) return;
//   lastSilenceAnimUpdate = currentTime;
  
//   silenceAnimPhase += 0.2;
//   if (silenceAnimPhase > TWO_PI) silenceAnimPhase -= TWO_PI;
  
//   // Pulsing text color
//   float brightness = 0.5 + 0.5 * sin(silenceAnimPhase);
//   uint8_t colorVal = 128 + brightness * 127;
//   uint16_t textColor = tft.color565(colorVal/2, colorVal, colorVal); // Cyan-ish
  
//   // Redraw message
//   String message = silenceMessages[currentSilenceMessageIndex];
//   int textWidth = message.length() * 18;
//   int textX = (SCREEN_WIDTH - textWidth) / 2;
//   int textY = SCREEN_HEIGHT / 2 - 10;
  
//   // Clear text area
//   tft.fillRect(textX - 5, textY - 5, textWidth + 10, 30, 0x0000);
  
//   // Draw pulsing text
//   tft.setTextSize(3);
//   tft.setTextColor(textColor);
//   tft.setCursor(textX, textY);
//   tft.print(message);
  
//   // Decorative dots
//   for (int i = 0; i < 3; i++) {
//     float angle = silenceAnimPhase + i * TWO_PI / 3.0;
//     int dotX = SCREEN_WIDTH / 2 + 60 * cos(angle);
//     int dotY = SCREEN_HEIGHT / 2 + 40 * sin(angle);
    
//     uint16_t dotColor = hsvToRgb565(i * 120, 0.8, brightness);
//     tft.fillCircle(dotX, dotY, 3, dotColor);
//   }
// }

// // ============================================================================
// // UTILITY FUNCTIONS
// // ============================================================================

// void showWelcomeScreen() {
//   tft.fillScreen(0x0000);
  
//   // Title
//   tft.setTextSize(4);
//   tft.setTextColor(0xF81F); // Magenta
//   tft.setCursor(50, 40);
//   tft.print("MUSTEM");
  
//   // Subtitle
//   tft.setTextSize(2);
//   tft.setTextColor(0x07FF); // Cyan
//   tft.setCursor(25, 90);
//   tft.print("Scientific Music Vision");
  
//   // Technical specs
//   tft.setTextSize(1);
//   tft.setTextColor(0x07E0); // Green
  
//   tft.setCursor(40, 120);
//   tft.print("FFT-based Audio Analysis");
  
//   tft.setCursor(35, 135);
//   tft.print("Psychoacoustic Freq. Mapping");
  
//   tft.setCursor(45, 150);
//   tft.print("10kHz Sample Rate | 128-FFT");
  
//   tft.setCursor(60, 165);
//   tft.print("78.125 Hz Resolution");
  
//   // Accessibility notice
//   tft.setTextColor(0xFFE0); // Yellow
//   tft.setCursor(55, 190);
//   tft.print("For Hearing Accessibility");
  
//   // Divider
//   tft.drawLine(30, 210, SCREEN_WIDTH - 30, 210, 0x07E0);
  
//   // Footer
//   tft.setTextColor(0x7BEF); // Light blue
//   tft.setCursor(90, 220);
//   tft.print("Initializing...");
  
//   delay(3000);
//   tft.fillScreen(0x0000);
// }

// // ============================================================================
// // DEBUG OVERLAY (Optional - enable with #define)
// // ============================================================================

// #define ENABLE_DEBUG_OVERLAY false

// void drawDebugOverlay() {
//   if (!ENABLE_DEBUG_OVERLAY) return;
  
//   tft.fillRect(0, 0, SCREEN_WIDTH, 15, 0x0000);
  
//   tft.setTextSize(1);
//   tft.setTextColor(0xFFFF);
//   tft.setCursor(5, 5);
  
//   tft.print("F:");
//   tft.print((int)audio.dominantFreq);
//   tft.print("Hz ");
  
//   tft.print("E:");
//   tft.print((int)audio.totalEnergy);
//   tft.print(" ");
  
//   tft.print("RMS:");
//   tft.print((int)audio.rms);
//   tft.print(" ");
  
//   if (beatDetect.currentStrength > 0.3) {
//     tft.print("BEAT!");
//   }
// }

// // Call in main loop:
// // if (ENABLE_DEBUG_OVERLAY) drawDebugOverlay();

#include <MCUFRIEND_kbv.h>
#include <Adafruit_GFX.h>
#include <arduinoFFT.h>

MCUFRIEND_kbv tft;

// ============================================================================
// PARÂMETROS CIENTÍFICOS FUNDAMENTADOS
// ============================================================================

// Audio Sampling (baseado em Teorema de Nyquist)
#define SAMPLING_FREQ 4000              // 10kHz sample rate
#define FFT_SAMPLES 512                  // 128-point FFT
#define SAMPLE_PERIOD_US (1000000UL / SAMPLING_FREQ)  // 100 µs

// Screen
#define SCREEN_WIDTH 320
#define SCREEN_HEIGHT 240
#define ELETRETO_PIN A6

#ifndef log2
  #define log2(x) (log(x) / 0.69314718056)
#endif

// Psychoacoustic Frequency Bands (Fletcher-Munson + Bark scale)
struct FrequencyBands {
  float SUBBASS_LOW = 20.0;
  float SUBBASS_HIGH = 60.0;
  float BASS_LOW = 60.0;
  float BASS_HIGH = 250.0;
  float LOWMID_LOW = 250.0;
  float LOWMID_HIGH = 500.0;
  float MID_LOW = 500.0;
  float MID_HIGH = 2000.0;
  float HIGHMID_LOW = 2000.0;
  float HIGHMID_HIGH = 4000.0;
  float TREBLE_LOW = 4000.0;
  float TREBLE_HIGH = 8000.0;
};

FrequencyBands FREQ_BANDS;

// Stevens Power Law for haptic mapping
const float STEVENS_EXPONENT = 0.67;

// Beat detection parameters (based on literature)
const float ONSET_THRESHOLD_MULTIPLIER = 1.5;     // k*sigma above mean
const unsigned long MIN_ONSET_INTERVAL_MS = 150;  // 400 BPM max

// Silence detection
float SILENCE_ENERGY_THRESHOLD = 100.0;      // Calibrated for electret mic
const unsigned long SILENCE_TIMEOUT_MS = 2000;


bool thresholdCalibrated = false;
float ambientNoiseLevel = 0.0;

// ============================================================================
// FFT BUFFERS AND INSTANCE
// ============================================================================

float vReal[FFT_SAMPLES];
float vImag[FFT_SAMPLES];
ArduinoFFT<float> FFT(vReal, vImag, FFT_SAMPLES, SAMPLING_FREQ);

// ============================================================================
// DATA STRUCTURES
// ============================================================================

struct AudioAnalysis {
  float dominantFreq;
  float peakMagnitude;
  float totalEnergy;
  float rms;
  unsigned long lastUpdate;
  bool isActive;
};

struct SpectrumData {
  float bands[6];           // 6 psycoacoustic bands
  float smoothedBands[6];
  float smoothingFactor;    // IIR filter coefficient
  unsigned long lastUpdate;
  
  SpectrumData() : smoothingFactor(0.3) {
    for (int i = 0; i < 6; i++) {
      bands[i] = 0.0;
      smoothedBands[i] = 0.0;
    }
    lastUpdate = 0;
  }
};

struct BeatDetector {
  float energyHistory[16];
  int historyIndex;
  float currentStrength;
  unsigned long lastOnset;
  unsigned long lastAnalysis;
  
  BeatDetector() : historyIndex(0), currentStrength(0.0), 
                   lastOnset(0), lastAnalysis(0) {
    for (int i = 0; i < 16; i++) {
      energyHistory[i] = 0.0;
    }
  }
  
  bool detectOnset(float currentEnergy, unsigned long currentTime) {
    // Calculate mean
    float mean = 0.0;
    for (int i = 0; i < 16; i++) {
      mean += energyHistory[i];
    }
    mean /= 16.0;
    
    // Calculate standard deviation
    float variance = 0.0;
    for (int i = 0; i < 16; i++) {
      float diff = energyHistory[i] - mean;
      variance += diff * diff;
    }
    float stdDev = sqrt(variance / 16.0);
    
    // Adaptive threshold
    float threshold = mean + ONSET_THRESHOLD_MULTIPLIER * stdDev;
    
    // Detect onset
    bool isOnset = false;
    if (currentEnergy > threshold && 
        (currentTime - lastOnset) > MIN_ONSET_INTERVAL_MS) {
      isOnset = true;
      currentStrength = min(1.0, (currentEnergy - mean) / (stdDev + 0.1));
      lastOnset = currentTime;
    } else {
      currentStrength *= 0.85; // Exponential decay
    }
    
    // Update history
    energyHistory[historyIndex] = currentEnergy;
    historyIndex = (historyIndex + 1) % 16;
    
    return isOnset;
  }
};

struct WindingVisualizer {
  float phase;
  float rotationSpeed;
  int pointCount;
  unsigned long lastUpdate;
  unsigned long lastClear;
  
  // Phyllotaxis parameters (Golden Ratio spiral)
  const float GOLDEN_ANGLE = 2.39996323; // 137.5° in radians
  const int MAX_POINTS = 200;
  
  WindingVisualizer() : phase(0.0), rotationSpeed(0.0), pointCount(0),
                        lastUpdate(0), lastClear(0) {}
};

// Global instances
AudioAnalysis audio;
SpectrumData spectrum;
BeatDetector beatDetect;
WindingVisualizer winding;

// Silence state
bool isInSilence = false;
unsigned long lastAudioDetectedTime = 0;

// Timing intervals (empirically optimized for balance)
const unsigned long FFT_INTERVAL_MS = 50;         // 20 Hz (FFT is expensive)
const unsigned long SPECTRUM_UPDATE_MS = 100;     // 10 Hz
const unsigned long WINDING_UPDATE_MS = 40;       // 25 Hz
const unsigned long BEAT_DETECT_MS = 100;         // 10 Hz
const unsigned long WINDING_CLEAR_MS = 15000;     // 15 seconds (increased from 8s for longer display)

// ============================================================================
// SETUP
// ============================================================================


// ============================================================================
// AUTO-CALIBRATION
// ============================================================================

void calibrateSilenceThreshold() {
  Serial.println("\n=== CALIBRANDO THRESHOLD DE SILÊNCIO ===");
  Serial.println("Mantenha o ambiente SILENCIOSO por 3 segundos...");
  
  tft.fillScreen(0x0000);
  tft.setTextSize(2);
  tft.setTextColor(0xFFE0); // Yellow
  tft.setCursor(30, 100);
  tft.print("Calibrando...");
  tft.setCursor(20, 130);
  tft.print("Mantenha silencio");
  
  delay(1000); // Dar tempo para estabilizar
  
  // Coletar amostras de ruído ambiente
  const int NUM_SAMPLES = 30;
  float noiseSamples[NUM_SAMPLES];
  
  for (int i = 0; i < NUM_SAMPLES; i++) {
    // Fazer FFT simples
    unsigned long startTime = micros();
    
    for (int j = 0; j < FFT_SAMPLES; j++) {
      vReal[j] = analogRead(ELETRETO_PIN);
      vImag[j] = 0.0;
      while (micros() - startTime < (j + 1) * SAMPLE_PERIOD_US) {}
    }
    
    // Remove DC offset
    float dcOffset = 0.0;
    for (int j = 0; j < FFT_SAMPLES; j++) {
      dcOffset += vReal[j];
    }
    dcOffset /= FFT_SAMPLES;
    
    for (int j = 0; j < FFT_SAMPLES; j++) {
      vReal[j] -= dcOffset;
    }
    
    // FFT
    FFT.windowing(FFTWindow::Hamming, FFTDirection::Forward);
    FFT.compute(FFTDirection::Forward);
    FFT.complexToMagnitude();

    // ===== FILTRO DE FAIXA: remove DC e infrassom residual, corta >4 kHz =====
    float freqResolution = (float)SAMPLING_FREQ / FFT_SAMPLES;  // 4000/256 ≈ 15.625 Hz
    vReal[0] = 0.0;   // DC
    vReal[1] = 0.0;   // ~15.6 Hz (ajuda a estabilizar silêncio)
    int minBin = 2;   // começa a procurar pico a partir daqui

    int maxBin = (int)(4000.0 / freqResolution);  // low-pass em 4 kHz
    if (maxBin > (FFT_SAMPLES/2)) maxBin = FFT_SAMPLES/2;
    for (int i = maxBin; i < FFT_SAMPLES/2; i++) vReal[i] = 0.0;

    
    // Calcular energia
    float energy = 0.0;
    for (int j = 1; j < FFT_SAMPLES / 2; j++) {
      energy += vReal[j];
    }
    
    noiseSamples[i] = energy;
    
    // Progresso visual
    if (i % 10 == 0) {
      tft.fillRect(50 + i * 7, 160, 5, 10, 0x07E0); // Green bar
    }
    
    delay(100);
  }
  
  // Calcular estatísticas do ruído
  float mean = 0.0;
  for (int i = 0; i < NUM_SAMPLES; i++) {
    mean += noiseSamples[i];
  }
  mean /= NUM_SAMPLES;
  
  float variance = 0.0;
  for (int i = 0; i < NUM_SAMPLES; i++) {
    float diff = noiseSamples[i] - mean;
    variance += diff * diff;
  }
  float stdDev = sqrt(variance / NUM_SAMPLES);
  
  // Threshold = média + 3*sigma (99.7% de confiança)
  ambientNoiseLevel = mean;
  SILENCE_ENERGY_THRESHOLD = mean + 3.0 * stdDev;
  
  // Garantir mínimo
  if (SILENCE_ENERGY_THRESHOLD < 50.0) {
    SILENCE_ENERGY_THRESHOLD = 50.0;
  }
  
  thresholdCalibrated = true;
  
  Serial.print("Ruído ambiente (média): ");
  Serial.println(mean, 1);
  Serial.print("Desvio padrão: ");
  Serial.println(stdDev, 1);
  Serial.print("THRESHOLD definido em: ");
  Serial.println(SILENCE_ENERGY_THRESHOLD, 1);
  
  // Mostrar resultado
  tft.fillScreen(0x0000);
  tft.setTextSize(2);
  tft.setTextColor(0x07E0); // Green
  tft.setCursor(40, 90);
  tft.print("Calibrado!");
  
  tft.setTextSize(1);
  tft.setTextColor(0xFFFF);
  tft.setCursor(30, 130);
  tft.print("Threshold: ");
  tft.print((int)SILENCE_ENERGY_THRESHOLD);
  
  tft.setCursor(30, 150);
  tft.print("Ruido medio: ");
  tft.print((int)ambientNoiseLevel);
  
  delay(2000);
  tft.fillScreen(0x0000);
  
  Serial.println("=== CALIBRAÇÃO CONCLUÍDA ===\n");
}

void setup() {
  Serial.begin(115200);
  
  // Initialize TFT
  uint16_t ID = tft.readID();
  if (ID == 0xD3D3) ID = 0x9481;
  tft.begin(ID);
  tft.setRotation(1);
  tft.fillScreen(0x0000);
  
  // Configure ADC for maximum speed
  analogReference(DEFAULT);
  
  // Initialize structures
  audio.lastUpdate = 0;
  audio.isActive = false;
  
  // Welcome screen
  showWelcomeScreen();
  
  // *** CALIBRAÇÃO AUTOMÁTICA ***
  calibrateSilenceThreshold();
  
  Serial.println("MUSTEM - Scientifically Grounded Audio Visualization");
  Serial.println("FFT Resolution: " + String(SAMPLING_FREQ / FFT_SAMPLES) + " Hz");
}

// ============================================================================
// AUDIO ANALYSIS FUNCTIONS
// ============================================================================

// ============================================================================
// AUDIO ANALYSIS FUNCTIONS
// ============================================================================

void performFFTAnalysis(unsigned long currentTime) {
  // ===== 1) Coleta de amostras =====
  unsigned long startTime = micros();
  for (int i = 0; i < FFT_SAMPLES; i++) {
    vReal[i] = analogRead(ELETRETO_PIN);
    vImag[i] = 0.0f;
    // tentativa de espaçamento uniforme (ideal: ADC free-running + ISR)
    while (micros() - startTime < (unsigned long)((i + 1) * SAMPLE_PERIOD_US)) { }
  }

  // ===== 2) Remoção de DC =====
  float dcOffset = 0.0f;
  for (int i = 0; i < FFT_SAMPLES; i++) dcOffset += vReal[i];
  dcOffset /= (float)FFT_SAMPLES;
  for (int i = 0; i < FFT_SAMPLES; i++) vReal[i] -= dcOffset;

  // ===== 3) FFT =====
  FFT.windowing(FFTWindow::Hamming, FFTDirection::Forward);
  FFT.compute(FFTDirection::Forward);
  FFT.complexToMagnitude();

  // ===== 4) Preparação espectral (faixa útil, piso, pico) =====
  float freqResolution = (float)SAMPLING_FREQ / (float)FFT_SAMPLES; // ≈15.625 Hz (com 4 kHz / 256)
  vReal[0] = 0.0f;   // remove DC
  vReal[1] = 0.0f;   // reduz drift/infragraves
  int minBin = 2;

  int maxBin = (int)(4000.0f / freqResolution);
  if (maxBin > FFT_SAMPLES / 2) maxBin = FFT_SAMPLES / 2;

  // Piso espectral (média e sigma nos bins úteis)
  float mean = 0.0f, var = 0.0f;
  int cnt = 0;
  for (int i = minBin; i < maxBin; i++) { mean += vReal[i]; cnt++; }
  if (cnt <= 0) cnt = 1;
  mean /= (float)cnt;
  for (int i = minBin; i < maxBin; i++) { float d = vReal[i] - mean; var += d * d; }
  float sigma = sqrtf(var / (float)cnt);

  // Pico bruto (com leve suavização nos graves)
  float peakMag = 0.0f;
  int   peakBin = minBin;
  for (int i = minBin + 1; i < maxBin - 1; i++) {
    float m = vReal[i];
    float f = i * freqResolution;
    if (f < 400.0f) {
      m = 0.25f * vReal[i - 1] + 0.5f * vReal[i] + 0.25f * vReal[i + 1];
    }
    if (m > peakMag) { peakMag = m; peakBin = i; }
  }

  // Aceita pico só se acima do piso por k·σ
  const float SPEC_K = 3.0f;
  bool hasPeak = (peakMag > mean + SPEC_K * sigma);

  static bool  freqInit = false;
  static float smoothedFreq = 0.0f;

  if (!hasPeak) {
    // Nada confiável ⇒ estado de silêncio
    audio.isActive = false;
    audio.peakMagnitude = 0.0f;
    audio.totalEnergy = 0.0f;
    audio.rms = 0.0f;
    audio.dominantFreq = 0.0f;
    audio.lastUpdate = currentTime;
    return;
  }

  // ===== 5) Interpolação parabólica do pico =====
  float detectedFreq = peakBin * freqResolution;
  float a = vReal[peakBin - 1], b = vReal[peakBin], c = vReal[peakBin + 1];
  if (b > a && b > c) {
    float p = 0.5f * (a - c) / (a - 2.0f * b + c);
    detectedFreq = (peakBin + p) * freqResolution;
  }

  // ===== 6) Suavização temporal da frequência =====
  if (!freqInit) { smoothedFreq = detectedFreq; freqInit = true; }
  const float FREQ_SMOOTHING = 0.30f;
  smoothedFreq = FREQ_SMOOTHING * detectedFreq + (1.0f - FREQ_SMOOTHING) * smoothedFreq;
  float newFreq = constrain(smoothedFreq, 30.0f, 4000.0f);

  // ===== 7) Energia/RMS =====
  audio.totalEnergy = 0.0f;
  for (int i = minBin; i < maxBin; i++) audio.totalEnergy += vReal[i];
  audio.rms = sqrtf(audio.totalEnergy / (float)(maxBin - minBin));
  audio.peakMagnitude = peakMag;

  // ===== 8) Gating de atividade (AJUSTADO para maior sensibilidade) =====
  float frequencyFactor = (newFreq < 150.0f) ? 1.3f : ((newFreq > 2000.0f) ? 1.1f : 1.0f);
  float activationThreshold   = SILENCE_ENERGY_THRESHOLD * frequencyFactor * 1.0f;  // Reduced from 1.3
  float deactivationThreshold = SILENCE_ENERGY_THRESHOLD * frequencyFactor * 0.5f;  // Reduced from 0.7

  static bool wasActive = false;
  static int consecutiveSilentFrames = 0, consecutiveActiveFrames = 0;

  bool currentlyHasEnergy = (audio.totalEnergy > activationThreshold);

  if (currentlyHasEnergy) {
    consecutiveActiveFrames++; consecutiveSilentFrames = 0;
    if (consecutiveActiveFrames >= 1) { audio.isActive = true; wasActive = true; } // Changed from >= 2
  } else if (audio.totalEnergy < deactivationThreshold) {
    consecutiveSilentFrames++; consecutiveActiveFrames = 0;
    if (consecutiveSilentFrames >= 8) { audio.isActive = false; wasActive = false; } // Increased from 5 to 8
  } else {
    if (wasActive) audio.isActive = true;
  }

  if (audio.isActive) {
    audio.dominantFreq = newFreq;
    lastAudioDetectedTime = currentTime;
  } else {
    audio.dominantFreq = 0.0f; // não exibir “freq” em silêncio
  }

  audio.lastUpdate = currentTime;

  // ===== 9) DEBUG (1 Hz) =====
  static unsigned long lastDebug = 0;
  if (currentTime - lastDebug > 1000) {
    if (audio.isActive && audio.dominantFreq > 0.0f) {
      Serial.print("Freq: "); Serial.print((int)audio.dominantFreq); Serial.print(" Hz");
    } else {
      Serial.print("Freq: --");
    }
    Serial.print(" | Mag: ");    Serial.print((int)audio.peakMagnitude);
    Serial.print(" | Energy: "); Serial.print((int)audio.totalEnergy);
    Serial.print(" | Active: "); Serial.println(audio.isActive ? "YES" : "NO");
    lastDebug = currentTime;
  }
}


void updateSpectrumBands(unsigned long currentTime) {
  if (!audio.isActive) return;
  
  // Map FFT bins to psychoacoustic frequency bands
  float freqResolution = (float)SAMPLING_FREQ / FFT_SAMPLES;  // 78.125 Hz
  
  // Clear bands
  for (int i = 0; i < 6; i++) {
    spectrum.bands[i] = 0.0;
  }
  
  // Accumulate magnitudes for each band
  for (int i = 1; i < FFT_SAMPLES / 2; i++) {
    float binFreq = i * freqResolution;
    float magnitude = vReal[i];
    
    // Assign to appropriate band
    if (binFreq >= FREQ_BANDS.SUBBASS_LOW && binFreq < FREQ_BANDS.SUBBASS_HIGH) {
      spectrum.bands[0] += magnitude;
    }
    else if (binFreq >= FREQ_BANDS.BASS_LOW && binFreq < FREQ_BANDS.BASS_HIGH) {
      spectrum.bands[1] += magnitude;
    }
    else if (binFreq >= FREQ_BANDS.LOWMID_LOW && binFreq < FREQ_BANDS.LOWMID_HIGH) {
      spectrum.bands[2] += magnitude;
    }
    else if (binFreq >= FREQ_BANDS.MID_LOW && binFreq < FREQ_BANDS.MID_HIGH) {
      spectrum.bands[3] += magnitude;
    }
    else if (binFreq >= FREQ_BANDS.HIGHMID_LOW && binFreq < FREQ_BANDS.HIGHMID_HIGH) {
      spectrum.bands[4] += magnitude;
    }
    else if (binFreq >= FREQ_BANDS.TREBLE_LOW && binFreq < FREQ_BANDS.TREBLE_HIGH) {
      spectrum.bands[5] += magnitude;
    }
  }
  
  // Normalize by number of bins in each band
  int binCounts[6] = {
    (FREQ_BANDS.SUBBASS_HIGH - FREQ_BANDS.SUBBASS_LOW) / freqResolution,
    (FREQ_BANDS.BASS_HIGH - FREQ_BANDS.BASS_LOW) / freqResolution,
    (FREQ_BANDS.LOWMID_HIGH - FREQ_BANDS.LOWMID_LOW) / freqResolution,
    (FREQ_BANDS.MID_HIGH - FREQ_BANDS.MID_LOW) / freqResolution,
    (FREQ_BANDS.HIGHMID_HIGH - FREQ_BANDS.HIGHMID_LOW) / freqResolution,
    (FREQ_BANDS.TREBLE_HIGH - FREQ_BANDS.TREBLE_LOW) / freqResolution
  };
  
  for (int i = 0; i < 6; i++) {
    if (binCounts[i] > 0) {
      spectrum.bands[i] /= binCounts[i];
    }
    
    // Apply IIR smoothing filter
    spectrum.smoothedBands[i] = spectrum.smoothingFactor * spectrum.bands[i] + 
                                 (1.0 - spectrum.smoothingFactor) * spectrum.smoothedBands[i];
    
    // Normalize to [0, 1]
    spectrum.smoothedBands[i] = constrain(spectrum.smoothedBands[i] / 100.0, 0.0, 1.0);
  }
  
  spectrum.lastUpdate = currentTime;
}

// ============================================================================
// SCIENTIFIC MAPPING FUNCTIONS
// ============================================================================

// Frequency to Color (Logarithmic Musical Mapping)
// Paper section 3.4: Log-frequency mapping aligned with 12-tone equal temperament
// Preserves octave equivalence and harmonic visual relationships
uint16_t frequencyToColorLogarithmic(float freq) {
  const float A1 = 55.0;      // Reference note A1
  const float A7 = 3520.0;    // Upper bound (7 octaves)
  const float SEMITONES_PER_OCTAVE = 12.0;
  const float HUE_RANGE = 360.0;  // Full color wheel
  
  // Constrain to valid range (7 octaves: A1 to A7)
  freq = constrain(freq, A1, A7);
  
  // Calculate logarithmic position: s = 12 × log₂(f / fref)
  float semitonesFromA1 = SEMITONES_PER_OCTAVE * log2(freq / A1);
  
  // Normalize to [0, 1] within 7 octaves (84 semitones)
  float normalizedPosition = semitonesFromA1 / 84.0;
  normalizedPosition = constrain(normalizedPosition, 0.0, 1.0);
  
  // Map to hue: hue ≈ (s mod 84)/84 × 360°
  // This ensures octaves occupy similar hue families
  float hue = normalizedPosition * HUE_RANGE;
  
  // High saturation and value for visibility on RGB565 TFT
  float saturation = 0.95; // High saturation
  float value = 0.90;      // High brightness
  
  return hsvToRgb565(hue, saturation, value);
}

// HSV to RGB565 conversion
uint16_t hsvToRgb565(float h, float s, float v) {
  float c = v * s;
  float x = c * (1.0 - fabs(fmod(h / 60.0, 2.0) - 1.0));
  float m = v - c;
  
  float r, g, b;
  int hi = (int)(h / 60.0) % 6;
  
  switch(hi) {
    case 0: r = c; g = x; b = 0; break;
    case 1: r = x; g = c; b = 0; break;
    case 2: r = 0; g = c; b = x; break;
    case 3: r = 0; g = x; b = c; break;
    case 4: r = x; g = 0; b = c; break;
    case 5: r = c; g = 0; b = x; break;
    default: r = 0; g = 0; b = 0; break;
  }
  
  uint8_t red = (uint8_t)((r + m) * 255);
  uint8_t green = (uint8_t)((g + m) * 255);
  uint8_t blue = (uint8_t)((b + m) * 255);
  
  return tft.color565(red, green, blue);
}

// Amplitude to Haptic Intensity (Stevens Power Law)
// Paper section 3.3: Vibrotactile intensity follows Stevens' Power Law
// I = S^n where n=0.67 models logarithmic perception of vibration
int amplitudeToHapticPWM(float amplitude) {
  amplitude = constrain(amplitude, 0, 1023);
  float normalized = amplitude / 1023.0;
  
  // Apply Stevens' Power Law for perceptual vibrotactile scaling
  float perceived = pow(normalized, STEVENS_EXPONENT); // n = 0.67
  
  const int MIN_PWM = 30;   // Motor activation threshold
  const int MAX_PWM = 255;  // Maximum safe PWM
  
  int pwmValue = MIN_PWM + perceived * (MAX_PWM - MIN_PWM);
  return constrain(pwmValue, 0, 255);
}

// Utility: Dim color by factor
uint16_t dimColor(uint16_t color, float factor) {
  int r = ((color >> 11) & 0x1F) * factor;
  int g = ((color >> 5) & 0x3F) * factor;
  int b = (color & 0x1F) * factor;
  return tft.color565(r << 3, g << 2, b << 3);
}

// ============================================================================
// VISUALIZATION: PHYLLOTAXIS WINDING
// ============================================================================

void updateWindingVisualization(unsigned long currentTime) {
  if (!audio.isActive) return;
  
  const float centerX = SCREEN_WIDTH / 2.0;
  const float centerY = SCREEN_HEIGHT / 2.0;
  
  // Rotation speed modulation by frequency (INCREASED for more dramatic effect)
  // Paper section 3.4: ω(t) = (f_detected / 440) × k
  // High frequencies → fast rotation (energetic visual)
  float freqRatio = audio.dominantFreq / 440.0;
  winding.rotationSpeed = freqRatio * 0.15; // k = 0.15 (3x faster for visibility)
  winding.phase += winding.rotationSpeed;
  
  // Radius modulation by RMS amplitude (EXPANDED range for dramatic visual)
  // Paper section 3.4: R_spiral = R_base + (RMS / 50) × 25 [constrained]
  float baseRadius = 60.0; // Increased from 40 to 60 (50% bigger base)
  float amplitudeModulation = audio.rms / 30.0; // More sensitive to amplitude
  float radius = baseRadius + amplitudeModulation * 50.0; // 2x expansion range
  radius = constrain(radius, 40.0, 110.0); // Larger constraint (was 20-80)
  
  // Beat-driven expansion (more dramatic)
  if (beatDetect.currentStrength > 0.3) {
    float beatExpansion = beatDetect.currentStrength * 20.0; // Increased from 15
    radius += beatExpansion;
  }
  
  // Color from logarithmic frequency mapping
  uint16_t baseColor = frequencyToColorLogarithmic(audio.dominantFreq);
  
  // Draw phyllotaxis spiral points (MORE POINTS for denser spiral)
  // Paper section 3.4: Golden Ratio phyllotaxis (φ ≈ 137.5°)
  const int POINTS_PER_FRAME = 15; // Increased from 12 to 15 (25% more dense)
  
  for (int i = 0; i < POINTS_PER_FRAME; i++) {
    // θ[n] = n × φ + ω(t)   [angular position]
    float angle = winding.pointCount * winding.GOLDEN_ANGLE + winding.phase;
    
    // r[n] = c × √n   [Fermat's spiral - ADJUSTED scaling for larger display]
    float dist = sqrt(winding.pointCount) * 4.5; // Increased from 3.0 to 4.5 (50% larger)
    
    if (dist > radius) {
      winding.pointCount = 0; // Reset spiral periodically
      dist = 0;
    }
    
    float x = centerX + dist * cos(angle);
    float y = centerY + dist * sin(angle);
    
    x = constrain(x, 0, SCREEN_WIDTH - 1);
    y = constrain(y, 0, SCREEN_HEIGHT - 1);
    
    // Fade based on distance from center (organic aesthetic)
    float fadeFactor = 1.0 - (dist / radius);
    fadeFactor = constrain(fadeFactor, 0.4, 1.0); // Slightly brighter minimum (0.3→0.4)
    
    uint16_t pointColor = dimColor(baseColor, fadeFactor);
    
    // Draw point (SLIGHTLY LARGER for better visibility)
    tft.fillCircle(x, y, 2, pointColor); // Increased from 1 to 2 pixels
    
    // Connect every 4th point instead of 5th (MORE connections)
    if (winding.pointCount > 0 && winding.pointCount % 4 == 0) {
      static float lastX = x, lastY = y;
      tft.drawLine(lastX, lastY, x, y, dimColor(pointColor, 0.6)); // Brighter lines (0.5→0.6)
      lastX = x;
      lastY = y;
    }
    
    winding.pointCount++;
  }
  
  winding.lastUpdate = currentTime;
}

void clearWindingGradually() {
  // Gradual fade instead of hard reset - keeps some context
  const int clearRadius = 120; // Slightly larger clear area
  const float centerX = SCREEN_WIDTH / 2.0;
  const float centerY = SCREEN_HEIGHT / 2.0;
  
  // Only clear center, allowing outer spiral to remain briefly
  tft.fillCircle(centerX, centerY, clearRadius, 0x0000);
  
  // Don't reset count to 0 - let it continue from smaller radius
  // This creates smooth transitions instead of jarring resets
  if (winding.pointCount > 50) {
    winding.pointCount = winding.pointCount / 2; // Halve instead of reset
  }
  winding.lastClear = millis();
}

// ============================================================================
// VISUALIZATION: SPECTRUM ANALYZER
// ============================================================================

void drawSpectrumAnalyzer(unsigned long currentTime) {
  if (!audio.isActive) return;
  
  const int SPECTRUM_X = SCREEN_WIDTH - 50;
  const int SPECTRUM_WIDTH = 45;
  const int SPECTRUM_HEIGHT = SCREEN_HEIGHT - 60;
  const int SPECTRUM_Y_START = 10;
  const int BAR_WIDTH = SPECTRUM_WIDTH / 6;
  const int BAR_SPACING = 1;
  
  for (int i = 0; i < 6; i++) {
    int x = SPECTRUM_X + i * (BAR_WIDTH + BAR_SPACING);
    
    // Calculate bar height
    float magnitude = spectrum.smoothedBands[i];
    int barHeight = magnitude * SPECTRUM_HEIGHT;
    barHeight = constrain(barHeight, 0, SPECTRUM_HEIGHT);
    
    // Clear previous bar
    tft.fillRect(x, SPECTRUM_Y_START, BAR_WIDTH, SPECTRUM_HEIGHT, 0x0000);
    
    // Draw new bar if there's signal
    if (barHeight > 2) {
      // Color represents frequency band
      float bandCenterFreq;
      if (i == 0) bandCenterFreq = (FREQ_BANDS.SUBBASS_LOW + FREQ_BANDS.SUBBASS_HIGH) / 2;
      else if (i == 1) bandCenterFreq = (FREQ_BANDS.BASS_LOW + FREQ_BANDS.BASS_HIGH) / 2;
      else if (i == 2) bandCenterFreq = (FREQ_BANDS.LOWMID_LOW + FREQ_BANDS.LOWMID_HIGH) / 2;
      else if (i == 3) bandCenterFreq = (FREQ_BANDS.MID_LOW + FREQ_BANDS.MID_HIGH) / 2;
      else if (i == 4) bandCenterFreq = (FREQ_BANDS.HIGHMID_LOW + FREQ_BANDS.HIGHMID_HIGH) / 2;
      else bandCenterFreq = (FREQ_BANDS.TREBLE_LOW + FREQ_BANDS.TREBLE_HIGH) / 2;
      
      uint16_t barColor = frequencyToColorLogarithmic(bandCenterFreq);
      
      // Draw gradient bar (darker at bottom)
      for (int y = 0; y < barHeight; y++) {
        float gradientFactor = 0.3 + 0.7 * (float)y / barHeight;
        uint16_t gradColor = dimColor(barColor, gradientFactor);
        tft.drawFastHLine(x, SPECTRUM_Y_START + SPECTRUM_HEIGHT - y, BAR_WIDTH, gradColor);
      }
      
      // Peak indicator (bright line at top)
      uint16_t peakColor = hsvToRgb565(i * 50, 0.9, 1.0); // Bright color
      tft.drawFastHLine(x, SPECTRUM_Y_START + SPECTRUM_HEIGHT - barHeight, BAR_WIDTH, peakColor);
      
      // Beat pulse effect
      if (beatDetect.currentStrength > 0.3) {
        int pulseWidth = beatDetect.currentStrength * 3;
        tft.drawRect(x - pulseWidth, SPECTRUM_Y_START + SPECTRUM_HEIGHT - barHeight - pulseWidth, 
                     BAR_WIDTH + 2*pulseWidth, barHeight + 2*pulseWidth, peakColor);
      }
    }
  }
}

// ============================================================================
// VISUALIZATION: WAVEFORM
// ============================================================================

void drawWaveform(unsigned long currentTime) {
  if (!audio.isActive) return;
  
  const int WAVE_Y_BASE = SCREEN_HEIGHT - 35;
  const int WAVE_HEIGHT = 25;
  
  // Clear wave area
  tft.fillRect(0, WAVE_Y_BASE - WAVE_HEIGHT, SCREEN_WIDTH, WAVE_HEIGHT * 2, 0x0000);
  
  // Calculate wave parameters
  float waveFrequency = map(audio.dominantFreq, 100.0, 2000.0, 20.0, 80.0);
  waveFrequency = constrain(waveFrequency, 20.0, 80.0);
  
  float amplitude = (audio.rms / 50.0) * WAVE_HEIGHT;
  amplitude = constrain(amplitude, 2.0, WAVE_HEIGHT);
  
  // Beat modulation
  if (beatDetect.currentStrength > 0.3) {
    amplitude *= (1.0 + beatDetect.currentStrength * 0.5);
  }
  
  // Phase advancement
  static float wavePhase = 0.0;
  wavePhase += (audio.dominantFreq / 440.0) * 0.1;
  if (wavePhase > TWO_PI) wavePhase -= TWO_PI;
  
  // Color based on frequency
  uint16_t waveColor = frequencyToColorLogarithmic(audio.dominantFreq);
  
  // Draw wave
  int lastY = WAVE_Y_BASE;
  for (int x = 0; x < SCREEN_WIDTH; x += 2) {
    float angle = TWO_PI * x / waveFrequency + wavePhase;
    int y = WAVE_Y_BASE + amplitude * sin(angle);
    y = constrain(y, WAVE_Y_BASE - WAVE_HEIGHT, WAVE_Y_BASE + WAVE_HEIGHT);
    
    // Draw line segment
    if (x > 0) {
      tft.drawLine(x - 2, lastY, x, y, waveColor);
    }
    
    lastY = y;
  }
}

// ============================================================================
// VISUALIZATION: BEAT INDICATOR
// ============================================================================

void drawBeatIndicator(unsigned long currentTime) {
  const int INDICATOR_X = 15;
  const int INDICATOR_Y = SCREEN_HEIGHT - 25;
  const int INDICATOR_RADIUS = 8;
  
  // Clear area
  tft.fillCircle(INDICATOR_X, INDICATOR_Y, INDICATOR_RADIUS + 2, 0x0000);
  
  if (beatDetect.currentStrength > 0.1) {
    // Apply Stevens' Power Law (n=0.67) for perceptual scaling
    // Paper section 3.4: "expansion magnitude proportional to beat strength 
    // (Stevens' exponent n=0.67 for perceptual scaling)"
    float stevensScaled = pow(beatDetect.currentStrength, STEVENS_EXPONENT);
    
    // Pulsing circle with perceptual compression
    int radius = INDICATOR_RADIUS * (0.5 + stevensScaled * 0.5);
    
    // Color intensity based on perceptually-scaled strength
    uint8_t intensity = 128 + stevensScaled * 127;
    uint16_t color = tft.color565(intensity, intensity / 2, intensity / 2); // Reddish
    
    tft.fillCircle(INDICATOR_X, INDICATOR_Y, radius, color);
    
    // Outer ring with perceptual scaling
    if (beatDetect.currentStrength > 0.5) {
      int ringRadius = INDICATOR_RADIUS + stevensScaled * 5;
      tft.drawCircle(INDICATOR_X, INDICATOR_Y, ringRadius, color);
    }
  }
}


// ============================================================================
// MAIN LOOP
// ============================================================================

void loop() {
  unsigned long currentTime = millis();
  
  // -------------------------------------------------------------------------
  // 1. AUDIO ANALYSIS (FFT) - Highest priority, fixed interval
  // -------------------------------------------------------------------------
  if (currentTime - audio.lastUpdate >= FFT_INTERVAL_MS) {
    performFFTAnalysis(currentTime);
  }
  
  // -------------------------------------------------------------------------
  // 2. CHECK SILENCE STATE
  // -------------------------------------------------------------------------
  checkSilenceState(currentTime);
  
  if (isInSilence) {
    updateSilenceAnimation(currentTime);
    return; // Skip visualizations in silence
  }
  
  // -------------------------------------------------------------------------
  // 3. SPECTRUM BAND ANALYSIS
  // -------------------------------------------------------------------------
  if (audio.isActive && currentTime - spectrum.lastUpdate >= SPECTRUM_UPDATE_MS) {
    updateSpectrumBands(currentTime);
  }
  
  // -------------------------------------------------------------------------
  // 4. BEAT DETECTION
  // -------------------------------------------------------------------------
  if (audio.isActive && currentTime - beatDetect.lastAnalysis >= BEAT_DETECT_MS) {
    beatDetect.detectOnset(audio.totalEnergy, currentTime);
    beatDetect.lastAnalysis = currentTime;
  }
  
  // -------------------------------------------------------------------------
  // 5. VISUAL UPDATES (when audio is active)
  // -------------------------------------------------------------------------
  if (audio.isActive) {
    // Winding spiral
    if (currentTime - winding.lastUpdate >= WINDING_UPDATE_MS) {
      updateWindingVisualization(currentTime);
    }
    
    // Spectrum analyzer
    if (currentTime - spectrum.lastUpdate >= SPECTRUM_UPDATE_MS) {
      drawSpectrumAnalyzer(currentTime);
    }
    
    // Waveform (less frequent for performance)
    static unsigned long lastWaveUpdate = 0;
    if (currentTime - lastWaveUpdate >= 50) { // 20 Hz
      drawWaveform(currentTime);
      lastWaveUpdate = currentTime;
    }
    
    // Beat indicator
    drawBeatIndicator(currentTime);
    
    // Periodic winding clear
    if (currentTime - winding.lastClear >= WINDING_CLEAR_MS) {
      clearWindingGradually();
    }
  }

  static unsigned long lastDebug = 0;
  if (millis() - lastDebug > 500) {
    tft.fillRect(0, 0, 180, 35, 0x0000);
    tft.setTextSize(1);
    tft.setTextColor(0xFFFF);
    
    // Linha 1: Energia
    tft.setCursor(5, 5);
    tft.print("E:");
    tft.print((int)audio.totalEnergy);
    tft.print(" T:");
    tft.print((int)SILENCE_ENERGY_THRESHOLD);
    
    // Linha 2: Frequência detectada
    tft.setCursor(5, 18);
    tft.setTextColor(audio.isActive ? 0x07E0 : 0xF800);
    if (audio.isActive) {
      tft.print("FREQ: ");
      tft.print((int)audio.dominantFreq);
      tft.print(" Hz");
    } else {
      tft.print("SILENT");
    }
    
    // Linha 3: Cor atual (para debug)
    tft.setCursor(5, 28);
    uint16_t currentColor = frequencyToColorLogarithmic(audio.dominantFreq);
    tft.fillRect(80, 28, 20, 6, currentColor);
    tft.setTextColor(0xFFFF);
    tft.print("Color:");
    
    lastDebug = millis();
  }
}

// ============================================================================
// SILENCE STATE MANAGEMENT
// ============================================================================

void checkSilenceState(unsigned long currentTime) {
  // Entering silence
  if (!isInSilence && (currentTime - lastAudioDetectedTime) > SILENCE_TIMEOUT_MS) {
    isInSilence = true;
    Serial.println("Entering silence mode");
    
    // Clear screen gradually
    tft.fillScreen(0x0000);
    showSilenceMessage();
  }
  
  // Exiting silence
  if (isInSilence && audio.isActive) {
    isInSilence = false;
    Serial.println("Exiting silence mode - audio detected");
    
    // Clear silence message
    tft.fillScreen(0x0000);
    
    // Reset visualization states
    winding.pointCount = 0;
    winding.phase = 0.0;
    winding.lastClear = currentTime;
  }
}

// ============================================================================
// SILENCE ANIMATION
// ============================================================================

// Silence messages
const char* silenceMessages[] = {
  "~ Listening ~",
  "Silence...",
  "Waiting...",
  "~ ~ ~",
  "Quiet",
  "Still..."
};
const int NUM_SILENCE_MESSAGES = 6;

int currentSilenceMessageIndex = 0;
float silenceAnimPhase = 0.0;
unsigned long lastSilenceAnimUpdate = 0;

void showSilenceMessage() {
  currentSilenceMessageIndex = (millis() / 1000) % NUM_SILENCE_MESSAGES;
  
  tft.setTextSize(3);
  String message = silenceMessages[currentSilenceMessageIndex];
  
  int textWidth = message.length() * 18;
  int textX = (SCREEN_WIDTH - textWidth) / 2;
  int textY = SCREEN_HEIGHT / 2 - 10;
  
  tft.setTextColor(0x7BEF); // Cyan
  tft.setCursor(textX, textY);
  tft.print(message);
}

void updateSilenceAnimation(unsigned long currentTime) {
  // Update animation at 5 Hz
  if (currentTime - lastSilenceAnimUpdate < 200) return;
  lastSilenceAnimUpdate = currentTime;
  
  silenceAnimPhase += 0.2;
  if (silenceAnimPhase > TWO_PI) silenceAnimPhase -= TWO_PI;
  
  // Pulsing text color
  float brightness = 0.5 + 0.5 * sin(silenceAnimPhase);
  uint8_t colorVal = 128 + brightness * 127;
  uint16_t textColor = tft.color565(colorVal/2, colorVal, colorVal); // Cyan-ish
  
  // Redraw message
  String message = silenceMessages[currentSilenceMessageIndex];
  int textWidth = message.length() * 18;
  int textX = (SCREEN_WIDTH - textWidth) / 2;
  int textY = SCREEN_HEIGHT / 2 - 10;
  
  // Clear text area
  tft.fillRect(textX - 5, textY - 5, textWidth + 10, 30, 0x0000);
  
  // Draw pulsing text
  tft.setTextSize(3);
  tft.setTextColor(textColor);
  tft.setCursor(textX, textY);
  tft.print(message);
  
  // Decorative dots
  for (int i = 0; i < 3; i++) {
    float angle = silenceAnimPhase + i * TWO_PI / 3.0;
    int dotX = SCREEN_WIDTH / 2 + 60 * cos(angle);
    int dotY = SCREEN_HEIGHT / 2 + 40 * sin(angle);
    
    uint16_t dotColor = hsvToRgb565(i * 120, 0.8, brightness);
    tft.fillCircle(dotX, dotY, 3, dotColor);
  }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

void showWelcomeScreen() {
  tft.fillScreen(0x0000);
  
  // Title
  tft.setTextSize(4);
  tft.setTextColor(0xF81F); // Magenta
  tft.setCursor(50, 40);
  tft.print("MUSTEM");
  
  // Subtitle
  tft.setTextSize(2);
  tft.setTextColor(0x07FF); // Cyan
  tft.setCursor(25, 90);
  tft.print("Scientific Music Vision");
  
  // Technical specs
  tft.setTextSize(1);
  tft.setTextColor(0x07E0); // Green
  
  tft.setCursor(40, 120);
  tft.print("FFT-based Audio Analysis");
  
  tft.setCursor(35, 135);
  tft.print("Psychoacoustic Freq. Mapping");
  
  tft.setCursor(45, 150);
  tft.print("10kHz Sample Rate | 128-FFT");
  
  tft.setCursor(60, 165);
  tft.print("78.125 Hz Resolution");
  
  // Accessibility notice
  tft.setTextColor(0xFFE0); // Yellow
  tft.setCursor(55, 190);
  tft.print("For Hearing Accessibility");
  
  // Divider
  tft.drawLine(30, 210, SCREEN_WIDTH - 30, 210, 0x07E0);
  
  // Footer
  tft.setTextColor(0x7BEF); // Light blue
  tft.setCursor(90, 220);
  tft.print("Initializing...");
  
  delay(3000);
  tft.fillScreen(0x0000);
}

// ============================================================================
// DEBUG OVERLAY (Optional - enable with #define)
// ============================================================================

#define ENABLE_DEBUG_OVERLAY false

void drawDebugOverlay() {
  if (!ENABLE_DEBUG_OVERLAY) return;
  
  tft.fillRect(0, 0, SCREEN_WIDTH, 15, 0x0000);
  
  tft.setTextSize(1);
  tft.setTextColor(0xFFFF);
  tft.setCursor(5, 5);
  
  tft.print("F:");
  tft.print((int)audio.dominantFreq);
  tft.print("Hz ");
  
  tft.print("E:");
  tft.print((int)audio.totalEnergy);
  tft.print(" ");
  
  tft.print("RMS:");
  tft.print((int)audio.rms);
  tft.print(" ");
  
  if (beatDetect.currentStrength > 0.3) {
    tft.print("BEAT!");
  }
}

// Call in main loop:
// if (ENABLE_DEBUG_OVERLAY) drawDebugOverlay();