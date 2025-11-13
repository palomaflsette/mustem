<div align="center">

# 🎵 MUSTEM
### Music - Multisensory Emotional Translation

**A scientifically-grounded dual-modality system for vibrotactile and visual translation of music as an assistive technology**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Arduino](https://img.shields.io/badge/Arduino-00979D?logo=Arduino&logoColor=white)](https://www.arduino.cc/)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Open Source](https://img.shields.io/badge/Open%20Source-%E2%9D%A4-red)](https://github.com/palomafsette/MUSTEM)

**[📖 Documentation](#-documentation) • [🚀 Quick Start](#-quick-start) • [🎥 Demos](#-video-demonstrations) • [📚 Research](#-research-paper) • [🤝 Contributing](#-contributing)**

</div>

---

## 📑 Table of Contents

- [Overview](#-overview)
- [The Central Question](#-the-central-question)
- [System Architecture](#-system-architecture)
  - [Hardware Components](#hardware-components)
  - [Dual-Modality Design](#dual-modality-design)
- [Scientific Foundations](#-scientific-foundations)
  - [Stevens' Power Law](#1-stevens-power-law-psychoacoustic-scaling)
  - [Logarithmic Frequency Mapping](#2-logarithmic-frequency-mapping)
  - [Golden Ratio Phyllotaxis](#3-golden-ratio-phyllotaxis)
- [Repository Structure](#-repository-structure)
- [Getting Started](#-getting-started)
  - [Hardware Setup](#hardware-setup)
  - [Firmware Installation](#firmware-installation)
  - [Software Installation](#software-installation)
- [Video Demonstrations](#-video-demonstrations)
- [Research Paper](#-research-paper)
- [Technical Details](#-technical-details)
- [Bill of Materials](#-bill-of-materials)
- [Contributing](#-contributing)
- [License](#-license)
- [Citation](#-citation)
- [Acknowledgments](#-acknowledgments)

---

## 🎯 Overview

**MUSTEM** (Music - Multisensory Emotional Translation) is an open-source assistive technology that makes music accessible to deaf and hard-of-hearing individuals through complementary dual-modality translation:

- **Vibrotactile (FEEL):** 4-channel spatial frequency mapping for rhythm and foundation
- **Visual (SEE):** Mathematical color and pattern generation for structure and details

### Why MUSTEM?

- **430+ million** people worldwide are deaf or hard-of-hearing (WHO, 2023)
- Music represents **cultural and emotional exclusion**, not just auditory inaccessibility
- Current solutions (amplification, visual-only, vibration-only) have significant limitations
- **No integrated dual-modality approach** exists with scientific grounding

### Key Features

**Scientifically-grounded** - Based on Stevens' Power Law, Fletcher-Munson curves, and golden ratio  
**Real-time processing** - <60ms latency on affordable hardware  
**Affordable** - <$50 USD in components  
**Open-source** - Hardware, firmware, and software freely available  
**Validated** - Pilot study (N=7) with positive preliminary results  

---

## The Central Question

> **"Can deaf people *truly* experience music emotionally through non-auditory modalities?"**


**Our answer:** Musical experience is **relative to individual sensory capacity**. A deaf person experiencing music through tactile and visual modalities is not having an "inferior" experience—they're having an **authentic experience through their perceptual reality**.

Read our complete philosophical framework: **[docs/PHILOSOPHICAL_FRAMEWORK.md](docs/PHILOS_FRAMEWORK.md)**

### Core Arguments:

1. **Musical emotion emerges from pattern processing**, not specific sensory modality
2. **Deaf individuals have adapted sensory systems** with enhanced tactile and visual capabilities
3. **Validity is user-determined**, not defined by hearing-centric assumptions

---

## 🏗️ System Architecture

### Hardware Components
```
┌─────────────┐
│  Ambient    │
│   Sound     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Electret   │
│ Microphone  │
└──────┬──────┘
       │
       ├──────────────────────┬─────────────────────┐
       │                      │                     │
       ▼                      ▼                     ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Arduino    │      │  Arduino    │      │   Python    │
│    UNO      │      │    Mega     │      │  Dashboard  │
│ (Tactile)   │      │  (Visual)   │      │ (Education) │
└──────┬──────┘      └──────┬──────┘      └─────────────┘
       │                     │
       ▼                     ▼
┌─────────────┐      ┌─────────────┐
│ 4× Motors   │      │ TFT LCD     │
│ (Wrists)    │      │  Display    │
└─────────────┘      └─────────────┘
```

### Dual-Modality Design

| Modality | Purpose | Hardware | Key Features |
|----------|---------|----------|--------------|
| **Vibrotactile** | Rhythm & Foundation | 4× ERM motors | - Psychoacoustic band separation<br>- Stevens' Law scaling (n=0.67)<br>- <60ms latency<br>- Spatial discrimination (40cm) |
| **Visual** | Structure & Details | TFT LCD 320×240 | - Log-frequency color mapping<br>- Golden angle phyllotaxis (137.5°)<br>- Real-time FFT processing<br>- Nature-inspired patterns |

---

## 🔬 Scientific Foundations

MUSTEM is grounded in three core scientific principles:

### 1. Stevens' Power Law (Psychoacoustic Scaling)
```
I = S^n

Where:
  I = perceived intensity
  S = stimulus magnitude
  n = 0.67 (vibrotactile exponent)
```

**Why it matters:** Human perception is non-linear. Stevens' Law models this, ensuring weak signals are perceivable and strong signals are comfortable.

**Application in MUSTEM:**
- Vibrotactile intensity: `PWM = (RMS_energy)^0.67 × 255`
- Visual brightness: `Brightness = (FFT_magnitude)^0.67`

---

### 2. Logarithmic Frequency Mapping
```
s = 12 × log₂(f / 55Hz)
hue = (s mod 84) / 84 × 360°

Where:
  f = frequency in Hz
  s = semitone number
  hue = color hue (0-360°)
```

**Why it matters:** Musical intervals are logarithmic (12-tone equal temperament). Logarithmic mapping preserves octave equivalence—notes an octave apart map to similar colors.

**Application in MUSTEM:**
| Frequency | Semitone | Color |
|-----------|----------|-------|
| 40 Hz | 0 | Deep Red |
| 440 Hz (A4) | 40 | Green |
| 880 Hz (A5) | 52 | Green (similar) |
| 6000 Hz | 83 | Purple-Magenta |

---

### 3. Golden Ratio Phyllotaxis
```
θ[n] = n × 137.5° + ω(t)
r[n] = c × √n

Where:
  θ = angle of nth point
  r = radius of nth point
  137.5° = golden angle (360° / φ²)
  φ = golden ratio ≈ 1.618
```

**Why it matters:** Phyllotaxis (found in sunflowers, pinecones, galaxies) maximizes packing efficiency while maintaining aesthetic beauty.

**Application in MUSTEM:**
- Each audio frame adds a new point at golden angle rotation
- Radius grows as √n for uniform density
- Creates organic, temporally-evolving spiral

---

## 📁 Repository Structure
```
MUSTEM/
├── hardware/
│   ├── firmware/
│   │   ├── tactile_system/          # Arduino UNO code
│   │   └── visual_system/           # Arduino Mega code
│   ├── 3d_models/                   # 3D-printable enclosure
│   ├── schematics/                  # Wiring diagrams
│   └── bill_of_materials.md
│
├── software/
│   ├── dashboard/                   # Educational interface
│   └── visualization/               # Artistic visualization
│
├── docs/
│   ├── PHILOSOPHICAL_FRAMEWORK.md   # Core arguments
│   ├── TECHNICAL_DETAILS.md         # Deep dive
│   ├── USER_GUIDE.md                # How to use
│   └── ASSEMBLY_GUIDE.md            # How to build
│
├── research/
│   ├── MUSTEM_EHB2025_slides.pdf    # Published paper
│   └── MUSTEM_EHB2025_slides.pdf    # Conference slides

```

---

## 🚀 Getting Started

### Prerequisites

**Hardware:**
- 1× Arduino Mega 2560
- 1× Arduino UNO
- 1× TFT LCD Shield 2.4" (320×240)
- 4× ERM vibration motors (3.3V)
- 1× Electret microphone
- Jumper wires, breadboard
- 3D printer (optional, for enclosure)

**Software:**
- Arduino IDE 1.8+
- Python 3.8+
- Git

---

### Hardware Setup

1. **Clone repository:**
```bash
git clone https://github.com/palomafsette/MUSTEM.git
cd MUSTEM
```

2. **3D print enclosure** (optional):
```bash
# Files in hardware/3d_models/
# Use 0.2mm layer height, 20% infill
```

3. **Wire components:**
   - Follow diagram: `hardware/schematics/system_wiring.png`
   - Full guide: `docs/ASSEMBLY_GUIDE.md`

---

### Firmware Installation

#### Tactile System (Arduino UNO):
```bash
cd hardware/firmware/tactile_system/
# Open tactile_system.ino in Arduino IDE
# Select: Tools → Board → Arduino UNO
# Select: Tools → Port → [your port]
# Upload
```

#### Visual System (Arduino Mega):
```bash
cd hardware/firmware/visual_system/
# Open visual_display_fft.ino in Arduino IDE
# Install required libraries:
#   - Adafruit GFX
#   - Adafruit TFT
#   - arduinoFFT
# Select: Tools → Board → Arduino Mega 2560
# Upload
```

**See:** `hardware/firmware/README.md` for detailed instructions

---

### Software Installation

#### Dashboard (Educational Interface):
```bash
cd software/dashboard/
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python mustem_assistive_dashboard.py
```

#### Artistic Visualization:
```bash
cd software/visualization/
pip install -r requirements.txt
python mustem_artistic_visualization.py [audio_file.wav]
```

**See:** `software/README.md` for usage details

---

## 🎥 Video Demonstrations

### Full System Demo
[![Full System Demo](media/demo_video_thumbnail.png)](https://youtube.com/your-video-link)
> Complete demonstration with "Uptown Funk" by Bruno Mars showing synchronized tactile, embedded visual, and dashboard outputs

### Individual Components
- [Vibrotactile System Demo](https://youtube.com/link)
- [LCD Display Demo](https://youtube.com/link)
- [Dashboard Interface Demo](https://youtube.com/link)
- [Artistic Visualization Demo](https://youtube.com/link)

**See:** `media/demo_videos/README.md` for more videos

---

## 📚 Research Paper

**Title:** MUSTEM: A Dual-Modality System for Vibrotactile and Visual Translation of Music as an Assistive Technology

**Published:** EHB 2025 - 13th International Conference on e-Health and Bioengineering  
**Award:** Strong Accept  
**Authors:** Paloma Sette, Maria Werneck, William Barbosa, Ana Loubacker

📄 **Read the paper:** [`research/paper/MUSTEM_EHB2025.pdf`](research/paper/MUSTEM_EHB2025.pdf)  
📊 **View slides:** [`research/presentation/MUSTEM_EHB2025_slides.pdf`](research/presentation/MUSTEM_EHB2025_slides.pdf)

---

## 🔧 Technical Details

### Vibrotactile System

**Signal Processing:**
- EMA envelope detection (α_attack=0.3, α_decay=0.1)
- Stevens' scaling: I = S^0.67
- PWM output: 30-255 (8-bit)
- Latency: <60ms (<100ms perceptual threshold)

**Frequency Bands:**
| Band | Range | Purpose | Wrist |
|------|-------|---------|-------|
| Kick | 20-80 Hz | Main beats | Left |
| Bass | 80-300 Hz | Foundation | Left |
| Voice | 300-2000 Hz | Melody | Right |
| Treble | 2k-8k Hz | Texture | Right |

**Perceptual Grounding:**
- Fletcher-Munson aligned bands
- Spatial discrimination: 40cm (>5cm JND)
- Just-noticeable difference: 3 PWM levels

---

### Visual System

**Frequency-to-Color Mapping:**
- 9 bands: sub-bass → treble
- Logarithmic spacing (12-tone equal temperament)
- Preserves octave equivalence

**Pattern Generation:**
- Golden angle: θ = 137.5°
- Fermat spiral: r = c√n
- Real-time FFT: 512-point, 4 kHz sampling

**Complete mapping:** `docs/TECHNICAL_DETAILS.md#visual-mapping`

---

## 💰 Bill of Materials

| Component | Qty | Price (USD) | Link |
|-----------|-----|-------------|------|
| Arduino Mega 2560 | 1 | $15 | [Link](https://store.arduino.cc) |
| Arduino UNO | 1 | $10 | [Link](https://store.arduino.cc) |
| TFT LCD Shield 2.4" | 1 | $12 | [Link](example.com) |
| ERM Vibration Motor 3.3V | 4 | $8 | [Link](example.com) |
| Electret Microphone | 1 | $2 | [Link](example.com) |
| Jumper Wires & Breadboard | 1 | $5 | [Link](example.com) |
| **TOTAL** | | **~$52** | |

**See:** `hardware/bill_of_materials.md` for complete list with supplier links

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

### Areas Where We Need Help:

- [ ] **Hardware:** Alternative motor configurations, better enclosure designs
- [ ] **Firmware:** Optimization for lower latency, additional frequency bands
- [ ] **Software:** Mobile app development, cloud music library
- [ ] **Research:** User studies, validation with deaf community
- [ ] **Documentation:** Translations, tutorials, assembly videos

---

## 📜 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file for details.

**TL;DR:** You can use, modify, and distribute this work freely, even commercially, as long as you include the original copyright notice.

---

## 📖 Citation

If you use MUSTEM in your research, please cite:
```bibtex
@inproceedings{sette2025mustem,
  title={MUSTEM: A Dual-Modality System for Vibrotactile and Visual Translation of Music as an Assistive Technology},
  author={Sette, Paloma and Werneck, Maria and Barbosa, William and Loubacker, Ana},
  booktitle={13th International Conference on e-Health and Bioengineering (EHB)},
  year={2025},
  organization={IEEE}
}
```

---

## 🙏 Acknowledgments

- **PUC-Rio** - Pontifícia Universidade Católica do Rio de Janeiro
- **EHB 2025** - International Conference on e-Health and Bioengineering
- **Deaf community** - For feedback and co-design input
- **Open-source contributors** - Arduino, Python, and maker communities

---

## 📧 Contact

**Paloma Sette** - Research Lead  
📧 Email: [your-email]  
🔗 LinkedIn: [your-linkedin]  
🐦 Twitter: [@your-handle]

**Project Link:** [https://github.com/palomafsette/MUSTEM](https://github.com/palomafsette/MUSTEM)

---

<div align="center">

**Making music universally accessible - not just hearing it differently, but experiencing it fully.**

🎵 430M+ potential beneficiaries worldwide 🌍

**[⭐ Star this repo](https://github.com/palomafsette/MUSTEM) • [🍴 Fork it](https://github.com/palomafsette/MUSTEM/fork) • [📣 Share it](https://twitter.com/intent/tweet?text=Check%20out%20MUSTEM)**

</div>