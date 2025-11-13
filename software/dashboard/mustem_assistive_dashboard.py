"""
VISUALIZADOR MUSICAL TERAPÊUTICO
Tecnologia Assistiva para Pessoas com Deficiência Auditiva
Traduz música em experiências visuais ricas e compreensíveis
"""

import pygame
import numpy as np
import math
import time
import sys
import wave
from collections import deque

# Configurações otimizadas
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
FPS = 60
CHUNK_SIZE = 1024
SAMPLE_RATE = 44100

class TherapeuticColors:
    """Sistema de cores cientificamente otimizado baseado na tabela de frequências musicais"""
    
    # Tabela científica de bandas de frequência com cores correspondentes
    FREQUENCY_BANDS_TABLE = [
        # (min_freq, max_freq, center_freq, color_name, rgb_color)
        (20, 60, 40, 'Deep Red', (200, 30, 60)),           # Sub-bass
        (60, 80, 70, 'Orange', (255, 100, 30)),            # Bass (low)
        (80, 110, 95, 'Yellow', (255, 200, 30)),           # Bass (mid)
        (110, 165, 135, 'Yellow-Green', (200, 255, 50)),   # Bass (upper)
        (165, 360, 250, 'Green', (100, 255, 100)),         # Low-Mid
        (360, 630, 500, 'Cyan', (50, 255, 255)),           # Mid (Low)
        (630, 960, 800, 'Light-Blue', (100, 150, 255)),    # Mid (Upper)
        (960, 2400, 1500, 'Dark-Blue', (50, 80, 200)),     # High-Mid
        (2400, 20000, 6000, 'Purple-Magenta', (180, 50, 255)),  # Treble/Shine
    ]
    
    EMOTION_COLORS = {
        'calm': (100, 150, 255),
        'energetic': (255, 150, 50),
        'melancholic': (150, 100, 200),
        'joyful': (255, 220, 100)
    }
    
    @staticmethod
    def frequency_to_color(freq_band_index, intensity=1.0):
        """Retorna cor para uma banda de frequência específica (0-8) baseado na tabela científica"""
        if freq_band_index >= len(TherapeuticColors.FREQUENCY_BANDS_TABLE):
            freq_band_index = len(TherapeuticColors.FREQUENCY_BANDS_TABLE) - 1
        
        band = TherapeuticColors.FREQUENCY_BANDS_TABLE[freq_band_index]
        r, g, b = band[4]  # RGB color
        return (int(r * intensity), int(g * intensity), int(b * intensity))
    
    @staticmethod
    def blend_colors(color1, color2, ratio):
        r1, g1, b1 = color1
        r2, g2, b2 = color2
        return (
            int(r1 * (1 - ratio) + r2 * ratio),
            int(g1 * (1 - ratio) + g2 * ratio),
            int(b1 * (1 - ratio) + b2 * ratio)
        )
    
    @staticmethod
    def with_alpha(color, alpha):
        r, g, b = color[:3]
        return (
            max(0, min(255, int(r * alpha))),
            max(0, min(255, int(g * alpha))),
            max(0, min(255, int(b * alpha)))
        )

# Constante Dourada (para Phyllotaxis)
GOLDEN_ANGLE = 2.39996323  # 137.5° em radianos

class PhyllotaxisVisualizer:
    """Visualizador de espiral baseada na proporção áurea (Phyllotaxis) - A MANDALA!"""
    
    def __init__(self, center_x, center_y):
        self.center_x = center_x
        self.center_y = center_y
        self.phase = 0.0
        self.rotation_speed = 0.0
        self.point_count = 0
        self.max_points = 300
        self.points = []
        self.last_clear_time = time.time()
    
    def update(self, spectrum, identity, beat_detected, dt):
        """Atualiza a espiral baseada no espectro de frequências"""
        if len(spectrum) == 0:
            return
        
        # Energia total do espectro
        total_energy = np.sum(spectrum)
        if total_energy < 0.01:
            return
        
        # Frequência dominante (banda com mais energia)
        dominant_band = np.argmax(spectrum)
        
        # Velocidade de rotação baseada na energia e frequência
        energy_factor = np.clip(total_energy * 2, 0.1, 2.0)
        self.rotation_speed = 0.02 + energy_factor * 0.03
        self.phase += self.rotation_speed
        
        # Raio modulado pela energia RMS
        base_radius = 80.0
        rms = np.sqrt(np.mean(spectrum ** 2))
        amplitude_modulation = rms * 50.0
        radius = base_radius + amplitude_modulation
        radius = np.clip(radius, 40.0, 150.0)
        
        # Expansão por batida
        beat_strength = identity.get('energy_level', 0) if beat_detected else 0
        if beat_detected and beat_strength > 0.3:
            beat_expansion = beat_strength * 25.0
            radius += beat_expansion
        
        # Cor baseada na banda dominante
        base_color = TherapeuticColors.frequency_to_color(dominant_band, 0.9)
        
        # Desenhar pontos da espiral (Phyllotaxis)
        points_per_frame = 6
        
        for i in range(points_per_frame):
            angle = self.point_count * GOLDEN_ANGLE + self.phase
            dist = np.sqrt(self.point_count) * 4.0  # Espiral para fora
            
            if dist > radius:
                self.point_count = 0  # Reset
                dist = 0
            
            x = self.center_x + dist * np.cos(angle)
            y = self.center_y + dist * np.sin(angle)
            
            # Fade baseado na distância do centro
            fade_factor = 1.0 - (dist / radius)
            fade_factor = np.clip(fade_factor, 0.2, 1.0)
            
            # Misturar cores baseado no espectro
            if len(spectrum) > 3:
                # Usar múltiplas bandas para criar variação de cor
                secondary_band = (dominant_band + 2) % len(spectrum)
                secondary_color = TherapeuticColors.frequency_to_color(secondary_band, 0.7)
                # Interpolar entre cores
                color_mix = 0.3 + 0.4 * np.sin(self.point_count * 0.1)
                point_color = TherapeuticColors.blend_colors(base_color, secondary_color, color_mix)
            else:
                point_color = base_color
            
            point_color = TherapeuticColors.with_alpha(point_color, fade_factor)
            point_size = 1 + rms * 4
            
            self.points.append({
                'x': x, 'y': y,
                'color': point_color,
                'size': point_size,
                'life': 2.5,
                'angle': angle
            })
            
            self.point_count += 1
        
        # Atualizar pontos existentes
        for point in self.points[:]:
            point['life'] -= dt
            if point['life'] <= 0:
                self.points.remove(point)
        
        # Limpar periodicamente
        if time.time() - self.last_clear_time > 6.0:
            self.points = []
            self.point_count = 0
            self.last_clear_time = time.time()
    
    def draw(self, screen):
        """Desenha os pontos da espiral"""
        for i, point in enumerate(self.points):
            size = max(1, int(point['size']))
            pygame.draw.circle(screen, point['color'], (int(point['x']), int(point['y'])), size)
            
            # Conectar alguns pontos para criar efeito de teia/mandala
            if i > 0 and i % 7 == 0:
                prev = self.points[i-1]
                fade_color = TherapeuticColors.with_alpha(point['color'], 0.2)
                pygame.draw.line(screen, fade_color, 
                               (int(prev['x']), int(prev['y'])),
                               (int(point['x']), int(point['y'])), 1)

class MusicalIdentityExtractor:
    """Extrai características musicais únicas para criar identidade visual"""
    
    def __init__(self):
        self.tempo_history = deque(maxlen=100)
        self.energy_history = deque(maxlen=200)
        self.spectral_centroid_history = deque(maxlen=100)
        
        self.avg_tempo = 120
        self.avg_energy = 0.3
        self.spectral_signature = np.zeros(12)
        self.rhythm_pattern = []
        self.harmonic_profile = np.zeros(7)
        self.genre_indicators = {
            'percussive': 0.0,
            'melodic': 0.0,
            'harmonic': 0.0,
            'rhythmic': 0.0
        }
    
    def analyze(self, spectrum, beat_detected, onset_strength):
        """Analisa e acumula características musicais"""
        if len(spectrum) == 0:
            return
        
        freqs = np.arange(len(spectrum))
        if np.sum(spectrum) > 0:
            centroid = np.sum(freqs * spectrum) / np.sum(spectrum)
            self.spectral_centroid_history.append(centroid / len(spectrum))
        
        energy = np.sum(spectrum ** 2)
        self.energy_history.append(energy)
        
        for i in range(12):
            start = int(i * len(spectrum) / 12)
            end = int((i + 1) * len(spectrum) / 12)
            band_energy = np.mean(spectrum[start:end])
            self.spectral_signature[i] = self.spectral_signature[i] * 0.98 + band_energy * 0.02
        
        for i in range(7):
            start = int(i * len(spectrum) / 7)
            end = int((i + 1) * len(spectrum) / 7)
            self.harmonic_profile[i] = self.harmonic_profile[i] * 0.95 + np.mean(spectrum[start:end]) * 0.05
        
        if beat_detected:
            self.tempo_history.append(time.time())
        
        # PERCUSSIVE: Detecta bateria através de múltiplos indicadores
        if len(self.energy_history) > 10:
            recent_energy = list(self.energy_history)[-10:]
            
            # 1. Variância de energia (mudanças súbitas)
            variance = np.var(recent_energy)
            
            # 2. Energia nos graves (20-165Hz = primeiras 3 bandas)
            bass_energy = 0.0
            if len(spectrum) >= 3:
                bass_energy = np.mean(spectrum[:3])  # Deep Bass + Bass mid + Bass upper
            
            # 3. Transientes (picos súbitos)
            transient_strength = 0.0
            if len(recent_energy) >= 3:
                current = recent_energy[-1]
                previous_avg = np.mean(recent_energy[-3:-1])
                if current > previous_avg * 1.3:  # Pico súbito
                    transient_strength = min(1.0, (current - previous_avg) / (previous_avg + 0.01))
            
            # Combina os 3 indicadores com pesos
            percussive_signal = (
                variance * 0.3 +           # Variância de energia
                bass_energy * 0.4 +        # Energia nos graves (bateria vive aqui!)
                transient_strength * 0.3   # Picos súbitos (ataques de bateria)
            )
            
            # Suavização MUITO mais rápida para responder à bateria
            self.genre_indicators['percussive'] = self.genre_indicators['percussive'] * 0.85 + percussive_signal * 0.15
            self.genre_indicators['melodic'] = self.genre_indicators['melodic'] * 0.99 + (1 - variance) * 0.01
        
        if np.max(spectrum) > 0:
            harmonic_richness = np.std(spectrum) / (np.mean(spectrum) + 1e-10)
            self.genre_indicators['harmonic'] = self.genre_indicators['harmonic'] * 0.98 + harmonic_richness * 0.02
        
        self.genre_indicators['rhythmic'] = self.genre_indicators['rhythmic'] * 0.97 + onset_strength * 0.03
        
        if len(self.tempo_history) > 3:
            recent_beats = list(self.tempo_history)[-4:]
            intervals = [recent_beats[i] - recent_beats[i-1] for i in range(1, len(recent_beats))]
            if intervals:
                avg_interval = np.mean(intervals)
                if avg_interval > 0:
                    bpm = 60.0 / avg_interval
                    if 40 < bpm < 200:
                        self.avg_tempo = self.avg_tempo * 0.9 + bpm * 0.1
        
        if len(self.energy_history) > 0:
            self.avg_energy = self.avg_energy * 0.98 + np.mean(list(self.energy_history)[-20:]) * 0.02
    
    def get_visual_identity(self):
        return {
            'spectral_signature': self.spectral_signature.copy(),
            'harmonic_profile': self.harmonic_profile.copy(),
            'tempo': self.avg_tempo,
            'energy_level': self.avg_energy,
            'genre_indicators': self.genre_indicators.copy(),
            'brightness': np.mean(self.spectral_centroid_history) if self.spectral_centroid_history else 0.5
        }

class EnhancedAudioAnalyzer:
    """Analisador avançado com múltiplas características musicais"""
    
    def __init__(self, audio_file):
        self.load_audio(audio_file)
        self.chunk_size = CHUNK_SIZE
        self.audio_start_time = None
        
        self.num_bands = 8  # 8 bandas (Sub-bass+Bass mesclados)
        self.spectrum = np.zeros(self.num_bands)
        self.smooth_spectrum = np.zeros(self.num_bands)
        
        self.beat_history = deque(maxlen=50)
        self.onset_envelope = deque(maxlen=20)
        self.last_beat_time = 0
        
        self.identity_extractor = MusicalIdentityExtractor()
        self.current_features = {}
        
        pygame.mixer.pre_init(frequency=SAMPLE_RATE, size=-16, channels=1, buffer=512)
        pygame.mixer.init()
    
    def load_audio(self, filename):
        with wave.open(filename, 'rb') as wav:
            frames = wav.readframes(-1)
            self.sample_rate = wav.getframerate()
            channels = wav.getnchannels()
            
            if wav.getsampwidth() == 2:
                audio_data = np.frombuffer(frames, dtype=np.int16)
            else:
                audio_data = np.frombuffer(frames, dtype=np.float32)
            
            if channels == 2:
                audio_data = audio_data[::2]
            
            self.audio_data = audio_data.astype(np.float32)
            if np.max(np.abs(self.audio_data)) > 0:
                self.audio_data /= np.max(np.abs(self.audio_data))
        
        pygame.mixer.music.load(filename)
    
    def start_playback(self):
        try:
            pygame.mixer.music.play()
            self.audio_start_time = time.time()
        except Exception as e:
            print(f"Erro ao iniciar áudio: {e}")
    
    def get_current_time(self):
        if self.audio_start_time is None:
            return 0
        return time.time() - self.audio_start_time
    
    def get_current_chunk(self):
        current_time = self.get_current_time()
        sample_pos = int(current_time * self.sample_rate)
        
        if sample_pos + self.chunk_size >= len(self.audio_data):
            return np.zeros(self.chunk_size)
        
        chunk = self.audio_data[sample_pos:sample_pos + self.chunk_size]
        return chunk * np.hanning(len(chunk))
    
    def detect_beat(self, chunk):
        energy = np.sum(chunk ** 2)
        self.onset_envelope.append(energy)
        
        if len(self.onset_envelope) < 10:
            return False, 0.0
        
        recent = list(self.onset_envelope)
        avg_energy = np.mean(recent[:-1])
        current_energy = recent[-1]
        
        threshold = avg_energy * 1.5
        onset_strength = max(0, (current_energy - avg_energy) / (avg_energy + 1e-10))
        
        current_time = time.time()
        if current_energy > threshold and (current_time - self.last_beat_time) > 0.2:
            self.last_beat_time = current_time
            return True, onset_strength
        
        return False, onset_strength
    
    def analyze(self):
        chunk = self.get_current_chunk()
        
        if len(chunk) == 0 or np.max(np.abs(chunk)) < 1e-6:
            return self.get_silent_state()
        
        fft = np.fft.rfft(chunk)
        magnitude = np.abs(fft)
        freqs = np.fft.rfftfreq(len(chunk), 1.0/self.sample_rate)
        
        # Bandas de frequência baseadas na tabela científica
        # MESCLADO: Sub-bass + Bass (low) em uma banda única mais larga!
        freq_bands = [
            (20, 80),      # Sub-bass + Bass (low) MESCLADOS - Deep Red/Orange
            (80, 110),     # Bass (mid) - Yellow
            (110, 165),    # Bass (upper) - Yellow-Green
            (165, 360),    # Low-Mid - Green
            (360, 630),    # Mid (Low) - Cyan
            (630, 960),    # Mid (Upper) - Light-Blue
            (960, 2400),   # High-Mid - Dark-Blue
            (2400, 20000)  # Treble/Shine - Purple-Magenta
        ]
        
        new_spectrum = np.zeros(self.num_bands)
        for i, (low_freq, high_freq) in enumerate(freq_bands):
            idx_low = np.searchsorted(freqs, low_freq)
            idx_high = np.searchsorted(freqs, high_freq)
            
            if idx_high > idx_low:
                band_energy = np.sqrt(np.mean(magnitude[idx_low:idx_high] ** 2))
                new_spectrum[i] = band_energy
        
        # Aplicar boost progressivo - MAIOR BOOST PARA GRAVES!
        # Primeira banda (20-80Hz mesclada) recebe boost MÁXIMO
        freq_boost = np.array([3.0, 2.2, 1.9, 1.7, 1.5, 1.7, 2.0, 2.8])
        new_spectrum = new_spectrum * freq_boost
        
        # Compressão não-linear REDUZIDA para graves (para não suprimir demais)
        compression_curve = np.array([0.70, 0.68, 0.68, 0.66, 0.68, 0.72, 0.75, 0.80])
        new_spectrum = np.power(new_spectrum, compression_curve)
        
        # Normalizar
        max_val = np.max(new_spectrum)
        if max_val > 0:
            new_spectrum = new_spectrum / max_val
        
        # Suavização adaptativa - MENOS suavização nos graves para resposta mais rápida!
        # Primeira banda (Sub-bass+Bass mesclados) precisa responder MUITO rápido aos kicks
        alpha = np.array([0.50, 0.40, 0.35, 0.32, 0.35, 0.42, 0.50, 0.60])
        self.spectrum = self.spectrum * (1 - alpha) + new_spectrum * alpha
        
        smooth_alpha = 0.5
        self.smooth_spectrum = self.smooth_spectrum * (1 - smooth_alpha) + self.spectrum * smooth_alpha
        
        beat_detected, onset_strength = self.detect_beat(chunk)
        self.identity_extractor.analyze(self.spectrum, beat_detected, onset_strength)
        
        total_energy = np.sum(self.spectrum)
        spectral_flux = np.sum(np.abs(np.diff(self.spectrum)))
        
        self.current_features = {
            'spectrum': self.smooth_spectrum.copy(),
            'raw_spectrum': self.spectrum.copy(),
            'beat_detected': beat_detected,
            'onset_strength': onset_strength,
            'total_energy': total_energy,
            'spectral_flux': spectral_flux,
            'time': self.get_current_time(),
            'identity': self.identity_extractor.get_visual_identity()
        }
        
        return self.current_features
    
    def get_silent_state(self):
        return {
            'spectrum': np.zeros(self.num_bands),
            'raw_spectrum': np.zeros(self.num_bands),
            'beat_detected': False,
            'onset_strength': 0.0,
            'total_energy': 0.0,
            'spectral_flux': 0.0,
            'time': self.get_current_time(),
            'identity': self.identity_extractor.get_visual_identity()
        }

class FrequencyBars:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.num_bars = 8  # 8 bandas (Sub-bass+Bass mesclados)
        self.bar_values = np.zeros(self.num_bars)
        self.peak_values = np.zeros(self.num_bars)
        self.peak_decay = np.zeros(self.num_bars)
        # Labels com Sub-bass+Bass MESCLADOS
        self.labels = [
            'Deep Bass',     # 20-80 Hz (MESCLADO!)
            'Bass (mid)',    # 80-110 Hz
            'Bass (upper)',  # 110-165 Hz
            'Low-Mid',       # 165-360 Hz
            'Mid (Low)',     # 360-630 Hz
            'Mid (Upper)',   # 630-960 Hz
            'High-Mid',      # 960-2400 Hz
            'Treble'         # 2400+ Hz (Shine)
        ]
    
    def update(self, spectrum, dt):
        target_values = spectrum[:self.num_bars]
        self.bar_values = self.bar_values * 0.7 + target_values * 0.3
        
        for i in range(self.num_bars):
            if self.bar_values[i] > self.peak_values[i]:
                self.peak_values[i] = self.bar_values[i]
                self.peak_decay[i] = 0
            else:
                self.peak_decay[i] += dt
                if self.peak_decay[i] > 0.1:
                    self.peak_values[i] -= dt * 0.5
                    self.peak_values[i] = max(0, self.peak_values[i])
    
    def draw(self, screen, font):
        bar_width = self.width / self.num_bars
        
        for i in range(self.num_bars):
            x = self.x + i * bar_width * 1.05  # Reduzido de 1.2 para 1.05 para caber 9 barras
            bar_height = self.bar_values[i] * self.height
            
            # Usar cor da tabela científica
            color = TherapeuticColors.frequency_to_color(i, 0.9)
            
            # Barra principal
            pygame.draw.rect(screen, color, (x + 2, self.y + self.height - bar_height, bar_width - 4, bar_height))
            
            # Borda branca
            pygame.draw.rect(screen, (255, 255, 255), (x + 2, self.y + self.height - bar_height, bar_width - 4, bar_height), 2)
            
            # Indicador de pico
            peak_y = self.y + self.height - self.peak_values[i] * self.height
            pygame.draw.line(screen, (255, 255, 255), (x + 2, peak_y), (x + bar_width - 2, peak_y), 3)
            
            # Label (nome da banda)
            label_surface = font.render(self.labels[i], True, (200, 200, 200))
            label_rect = label_surface.get_rect(center=(x + bar_width/2, self.y + self.height + 15))
            screen.blit(label_surface, label_rect)

class CircularSpectrum:
    def __init__(self, center_x, center_y, radius):
        self.center_x = center_x
        self.center_y = center_y
        self.base_radius = radius
        self.particles = []
        self.history_points = deque(maxlen=120)
        self.rotation = 0
        self.dna_spiral = []
        self.harmonic_rings = []
        self.emotion_particles = []
    
    def update(self, spectrum, identity, beat_detected, dt):
        self.rotation += dt * 0.5
        
        if len(spectrum) > 0:
            avg_energy = np.mean(spectrum)
            self.history_points.append({'spectrum': spectrum.copy(), 'time': time.time(), 'energy': avg_energy, 'beat': beat_detected})
        
        if len(spectrum) > 3:
            angle = self.rotation * 2
            radius = self.base_radius + 30
            modulation = spectrum[0] * 20
            x = self.center_x + (radius + modulation) * math.cos(angle)
            y = self.center_y + (radius + modulation) * math.sin(angle)
            
            self.dna_spiral.append({'x': x, 'y': y, 'color': TherapeuticColors.frequency_to_color(0, spectrum[0]), 'life': 3.0, 'size': 2 + spectrum[0] * 3})
            if len(self.dna_spiral) > 200:
                self.dna_spiral.pop(0)
        
        for point in self.dna_spiral[:]:
            point['life'] -= dt
            if point['life'] <= 0:
                self.dna_spiral.remove(point)
        
        if identity['genre_indicators']['harmonic'] > 0.3 and len(self.harmonic_rings) < 5:
            self.harmonic_rings.append({'radius': 10, 'max_radius': 150, 'color': TherapeuticColors.EMOTION_COLORS['calm'], 'life': 2.0})
        
        for ring in self.harmonic_rings[:]:
            ring['radius'] += dt * 60
            ring['life'] -= dt * 0.5
            if ring['life'] <= 0 or ring['radius'] > ring['max_radius']:
                self.harmonic_rings.remove(ring)
        
        tempo = identity['tempo']
        energy = identity['energy_level']
        
        if energy > 0.6 and tempo > 120:
            emotion = 'energetic'
        elif energy < 0.3 and tempo < 100:
            emotion = 'calm'
        elif identity['brightness'] < 0.4:
            emotion = 'melancholic'
        else:
            emotion = 'joyful'
        
        if len(self.emotion_particles) < 30 and np.random.random() > 0.7:
            angle = np.random.random() * 2 * np.pi
            distance = 40 + np.random.random() * 60
            self.emotion_particles.append({
                'angle': angle, 'distance': distance, 'orbit_speed': 0.5 + np.random.random() * 1.5,
                'color': TherapeuticColors.EMOTION_COLORS[emotion], 'life': 2.0 + np.random.random() * 2.0,
                'size': 2 + np.random.random() * 4
            })
        
        for particle in self.emotion_particles[:]:
            particle['angle'] += particle['orbit_speed'] * dt
            particle['distance'] += dt * 5
            particle['life'] -= dt * 0.3
            if particle['life'] <= 0:
                self.emotion_particles.remove(particle)
        
        if beat_detected and len(self.particles) < 50:
            for i in range(3):
                angle = np.random.random() * 2 * np.pi
                speed = 50 + np.random.random() * 100
                self.particles.append({
                    'x': self.center_x, 'y': self.center_y,
                    'vx': math.cos(angle) * speed, 'vy': math.sin(angle) * speed,
                    'life': 1.0, 'color': TherapeuticColors.frequency_to_color(int(np.random.random() * 7), 1.0)
                })
        
        for particle in self.particles[:]:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['life'] -= dt * 0.8
            particle['vy'] += 100 * dt
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, screen, spectrum):
        if len(spectrum) == 0:
            return
        
        if len(self.dna_spiral) > 1:
            for i in range(len(self.dna_spiral) - 1):
                p1, p2 = self.dna_spiral[i], self.dna_spiral[i + 1]
                if p1['life'] > 0 and p2['life'] > 0:
                    alpha = min(p1['life'], p2['life']) / 3.0
                    color = TherapeuticColors.with_alpha(p1['color'], alpha)
                    x1, y1 = max(0, min(SCREEN_WIDTH, int(p1['x']))), max(0, min(SCREEN_HEIGHT, int(p1['y'])))
                    x2, y2 = max(0, min(SCREEN_WIDTH, int(p2['x']))), max(0, min(SCREEN_HEIGHT, int(p2['y'])))
                    pygame.draw.line(screen, color, (x1, y1), (x2, y2), 2)
        
        for ring in self.harmonic_rings:
            if ring['life'] > 0:
                alpha = ring['life'] / 2.0
                color = TherapeuticColors.with_alpha(ring['color'], alpha * 0.6)
                pygame.draw.circle(screen, color, (self.center_x, self.center_y), int(ring['radius']), 3)
        
        for particle in self.emotion_particles:
            if particle['life'] > 0:
                x = self.center_x + particle['distance'] * math.cos(particle['angle'])
                y = self.center_y + particle['distance'] * math.sin(particle['angle'])
                alpha = min(1.0, particle['life'] / 2.0)
                color = TherapeuticColors.with_alpha(particle['color'], alpha)
                size = max(1, int(particle['size'] * alpha))
                x_pos, y_pos = max(0, min(SCREEN_WIDTH, int(x))), max(0, min(SCREEN_HEIGHT, int(y)))
                pygame.draw.circle(screen, color, (x_pos, y_pos), size)
                
                if alpha > 0.3:
                    line_color = TherapeuticColors.with_alpha(particle['color'], alpha * 0.3)
                    pygame.draw.line(screen, line_color, (self.center_x, self.center_y), (x_pos, y_pos), 1)
        
        points = []
        for i in range(len(spectrum)):
            angle = (i / len(spectrum)) * 2 * math.pi + self.rotation
            energy = spectrum[i]
            radius = self.base_radius + energy * 150
            x = self.center_x + radius * math.cos(angle)
            y = self.center_y + radius * math.sin(angle)
            points.append((int(x), int(y)))
        
        if len(points) > 2:
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.polygon(s, (100, 150, 255, 40), points)
            screen.blit(s, (0, 0))
            
            for i in range(len(points)):
                start, end = points[i], points[(i + 1) % len(points)]
                color = TherapeuticColors.frequency_to_color(i, 0.8)
                pygame.draw.line(screen, color, start, end, 3)
        
        for i, point in enumerate(points):
            color = TherapeuticColors.frequency_to_color(i, 1.0)
            size = 3 + int(spectrum[i] * 8)
            halo_color = TherapeuticColors.with_alpha(color, 0.3)
            pygame.draw.circle(screen, halo_color, point, size + 3)
            pygame.draw.circle(screen, color, point, size)
            pygame.draw.circle(screen, (255, 255, 255), point, max(1, size // 2))
        
        for particle in self.particles:
            if particle['life'] > 0:
                color = TherapeuticColors.with_alpha(particle['color'], particle['life'])
                size = max(1, int(particle['life'] * 5))
                x, y = max(0, min(SCREEN_WIDTH, int(particle['x']))), max(0, min(SCREEN_HEIGHT, int(particle['y'])))
                pygame.draw.circle(screen, color, (x, y), size)

class WaveformHistory:
    def __init__(self, x, y, width, height):
        self.x, self.y, self.width, self.height = x, y, width, height
        self.history = deque(maxlen=200)
        self.color_history = deque(maxlen=200)
    
    def update(self, spectrum, identity):
        if len(spectrum) > 0:
            avg_energy = np.mean(spectrum)
            self.history.append(avg_energy)
            
            tempo, energy = identity['tempo'], identity['energy_level']
            if energy > 0.6 and tempo > 120:
                color = TherapeuticColors.EMOTION_COLORS['energetic']
            elif energy < 0.3 and tempo < 100:
                color = TherapeuticColors.EMOTION_COLORS['calm']
            elif identity['brightness'] < 0.4:
                color = TherapeuticColors.EMOTION_COLORS['melancholic']
            else:
                color = TherapeuticColors.EMOTION_COLORS['joyful']
            self.color_history.append(color)
    
    def draw(self, screen):
        if len(self.history) < 2:
            return
        
        center_y = self.y + self.height // 2
        pygame.draw.line(screen, (80, 80, 80), (self.x, center_y), (self.x + self.width, center_y), 1)
        
        points_top, points_bottom = [], []
        for i, (energy, color) in enumerate(zip(self.history, self.color_history)):
            x = self.x + (i / len(self.history)) * self.width
            wave_height = energy * self.height * 0.4
            points_top.append((int(x), int(center_y - wave_height)))
            points_bottom.append((int(x), int(center_y + wave_height)))
        
        if len(points_top) > 1:
            for i in range(len(points_top) - 1):
                color = self.color_history[i]
                alpha = 0.3 + (i / len(points_top)) * 0.7
                draw_color = TherapeuticColors.with_alpha(color, alpha)
                pygame.draw.line(screen, draw_color, points_top[i], points_top[i + 1], 2)
                pygame.draw.line(screen, draw_color, points_bottom[i], points_bottom[i + 1], 2)
        
        if len(points_top) > 2:
            s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            all_points = points_top + points_bottom[::-1]
            if len(all_points) > 2:
                pygame.draw.polygon(s, (100, 150, 255, 30), all_points)
                screen.blit(s, (self.x, self.y))

class EmotionIndicator:
    def __init__(self, x, y, size):
        self.x, self.y, self.size = x, y, size
        self.current_emotion = 'calm'
        self.emotion_strength = 0.0
        self.pulse = 0.0
    
    def update(self, identity, beat_detected, dt):
        tempo, energy, brightness = identity['tempo'], identity['energy_level'], identity['brightness']
        
        if energy > 0.6 and tempo > 120:
            self.current_emotion, self.emotion_strength = 'energetic', min(1.0, energy * 1.5)
        elif energy < 0.3 and tempo < 100:
            self.current_emotion, self.emotion_strength = 'calm', max(0.3, 1.0 - energy)
        elif brightness < 0.4:
            self.current_emotion, self.emotion_strength = 'melancholic', max(0.4, 1.0 - brightness)
        else:
            self.current_emotion, self.emotion_strength = 'joyful', min(1.0, brightness + energy * 0.5)
        
        self.pulse = 1.0 if beat_detected else self.pulse * 0.9
    
    def draw(self, screen, font):
        color = TherapeuticColors.EMOTION_COLORS[self.current_emotion]
        pulse_size = self.size + self.pulse * 15
        
        halo_color = TherapeuticColors.with_alpha(color, 0.3)
        pygame.draw.circle(screen, halo_color, (self.x, self.y), int(pulse_size + 10))
        pygame.draw.circle(screen, color, (self.x, self.y), int(pulse_size))
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), int(pulse_size), 3)
        
        inner_size = int(pulse_size * self.emotion_strength)
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), inner_size)
        
        emotion_labels = {'calm': 'Calm', 'energetic': 'Energetic', 'melancholic': 'Melancholic', 'joyful': 'Joyful'}
        text = emotion_labels[self.current_emotion]
        label_surface = font.render(text, True, (255, 255, 255))
        label_rect = label_surface.get_rect(center=(self.x, self.y + self.size + 25))
        screen.blit(label_surface, label_rect)

class RhythmVisualizer:
    def __init__(self, x, y, width, height):
        self.x, self.y, self.width, self.height = x, y, width, height
        self.beat_markers = deque(maxlen=16)
        self.tempo_display = 120
    
    def update(self, identity, beat_detected, dt):
        self.tempo_display = self.tempo_display * 0.95 + identity['tempo'] * 0.05
        
        if beat_detected:
            self.beat_markers.append({'time': time.time(), 'life': 1.0, 'intensity': identity['energy_level']})
        
        for marker in list(self.beat_markers):
            marker['life'] -= dt * 2
            if marker['life'] <= 0:
                self.beat_markers.remove(marker)
    
    def draw(self, screen, font):
        title = font.render('RYTHM', True, (200, 200, 200))
        screen.blit(title, (self.x, self.y - 30))
        
        bpm_text = f'{int(self.tempo_display)} BPM'
        bpm_surface = font.render(bpm_text, True, (255, 255, 255))
        screen.blit(bpm_surface, (self.x, self.y))
        
        if len(self.beat_markers) > 0:
            beat_width = self.width / 16
            for i, marker in enumerate(self.beat_markers):
                x = self.x + i * beat_width
                height = marker['life'] * self.height
                intensity = marker['intensity']
                color = TherapeuticColors.frequency_to_color(1, intensity)
                alpha_color = TherapeuticColors.with_alpha(color, marker['life'])
                pygame.draw.rect(screen, alpha_color, (x, self.y + 40, beat_width - 2, height))

class MusicalDNAVisualizer:
    def __init__(self, x, y, width, height):
        self.x, self.y, self.width, self.height = x, y, width, height
        self.strands = []
        self.time_offset = 0
    
    def update(self, identity, dt):
        self.time_offset += dt
        spectral_sig = identity['spectral_signature']
        
        if len(self.strands) < 100:
            self.strands.append({'position': len(self.strands), 'frequencies': spectral_sig.copy(), 'time': self.time_offset})
        
        if len(self.strands) > 100:
            self.strands.pop(0)
    
    def draw(self, screen):
        if len(self.strands) < 2:
            return
        
        for i in range(len(self.strands) - 1):
            progress = i / len(self.strands)
            x = self.x + progress * self.width
            strand = self.strands[i]
            
            for helix in range(2):
                phase = helix * math.pi
                y1 = self.y + self.height/2 + math.sin(progress * 4 * math.pi + phase) * 30
                y2 = self.y + self.height/2 + math.sin((progress + 0.01) * 4 * math.pi + phase) * 30
                freq_idx = np.argmax(strand['frequencies'])
                color = TherapeuticColors.frequency_to_color(freq_idx, 0.8)
                x_next = self.x + (progress + 0.01) * self.width
                pygame.draw.line(screen, color, (int(x), int(y1)), (int(x_next), int(y2)), 2)
            
            if i % 5 == 0:
                y1 = self.y + self.height/2 + math.sin(progress * 4 * math.pi) * 30
                y2 = self.y + self.height/2 + math.sin(progress * 4 * math.pi + math.pi) * 30
                pygame.draw.line(screen, (150, 150, 150), (int(x), int(y1)), (int(x), int(y2)), 1)

class TherapeuticMusicVisualizer:
    def __init__(self, audio_file):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('MUSTEM Auditory Decoder')
        self.clock = pygame.time.Clock()
        
        self.title_font = pygame.font.Font(None, 48)
        self.large_font = pygame.font.Font(None, 36)
        self.medium_font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 20)
        
        self.analyzer = EnhancedAudioAnalyzer(audio_file)
        
        self.frequency_bars = FrequencyBars(50, 100, 600, 250)  # Largura aumentada de 500 para 600 para 9 bandas
        self.circular_spectrum = CircularSpectrum(1050, 300, 80)
        self.phyllotaxis = PhyllotaxisVisualizer(1050, 300)  # MANDALA! Mesma posição do circular
        self.waveform = WaveformHistory(50, 420, 900, 120)
        self.emotion_indicator = EmotionIndicator(1050, 550, 40)
        self.rhythm_viz = RhythmVisualizer(50, 600, 300, 100)
        self.dna_viz = MusicalDNAVisualizer(400, 600, 550, 100)
        
        self.running = True
        self.paused = False
        self.last_time = time.time()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                    if self.paused:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
    
    def draw_interface(self, features):
        title = self.title_font.render('MUSTEM Auditory Decoder', True, (255, 255, 255))
        self.screen.blit(title, (50, 20))
        
        subtitle = self.small_font.render(' Assistive Technology for People with Hearing Impairment', True, (180, 180, 180))
        self.screen.blit(subtitle, (50, 65))
        
        identity = features['identity']
        info_y = 400
        tempo_text = f"Time: {int(identity['tempo'])} BPM"
        tempo_surface = self.medium_font.render(tempo_text, True, (200, 200, 200))
        self.screen.blit(tempo_surface, (600, info_y))
        
        energy_text = f"Energy: {int(identity['energy_level'] * 100)}%"
        energy_surface = self.medium_font.render(energy_text, True, (200, 200, 200))
        self.screen.blit(energy_surface, (800, info_y))
        
        genre_y = 570
        genre_title = self.small_font.render('Characteristics:', True, (180, 180, 180))
        self.screen.blit(genre_title, (1100, genre_y))
        
        indicators = identity['genre_indicators']
        genres = [('Percussive', indicators['percussive']), ('Melodic', indicators['melodic']),
                  ('Harmonic', indicators['harmonic']), ('Rhythmic', indicators['rhythmic'])]
        
        for i, (name, value) in enumerate(genres):
            y = genre_y + 25 + i * 25
            bar_width = int(value * 100)
            pygame.draw.rect(self.screen, (80, 80, 80), (1100, y, 200, 15))
            pygame.draw.rect(self.screen, (100, 200, 255), (1100, y, bar_width, 15))
            label = self.small_font.render(name, True, (200, 200, 200))
            self.screen.blit(label, (1310, y - 2))
        
        if self.paused:
            pause_text = self.large_font.render('PAUSADO - Pressione ESPAÇO', True, (255, 200, 100))
            text_rect = pause_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - 40))
            self.screen.blit(pause_text, text_rect)
        else:
            instructions = self.small_font.render('SPACE: Pause | ESC: Exit', True, (150, 150, 150))
            text_rect = instructions.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - 30))
            self.screen.blit(instructions, text_rect)
    
    def run(self):
        self.analyzer.start_playback()
        
        while self.running:
            current_time = time.time()
            dt = current_time - self.last_time
            self.last_time = current_time
            
            self.handle_events()
            
            if not self.paused:
                features = self.analyzer.analyze()
                
                self.frequency_bars.update(features['spectrum'], dt)
                self.circular_spectrum.update(features['spectrum'], features['identity'], features['beat_detected'], dt)
                self.phyllotaxis.update(features['spectrum'], features['identity'], features['beat_detected'], dt)  # MANDALA!
                self.waveform.update(features['spectrum'], features['identity'])
                self.emotion_indicator.update(features['identity'], features['beat_detected'], dt)
                self.rhythm_viz.update(features['identity'], features['beat_detected'], dt)
                self.dna_viz.update(features['identity'], dt)
                
                self.screen.fill((20, 20, 30))
                
                self.frequency_bars.draw(self.screen, self.small_font)
                self.circular_spectrum.draw(self.screen, features['spectrum'])
                self.phyllotaxis.draw(self.screen)  # MANDALA! Desenha por cima do circular
                self.waveform.draw(self.screen)
                self.emotion_indicator.draw(self.screen, self.medium_font)
                self.rhythm_viz.draw(self.screen, self.small_font)
                self.dna_viz.draw(self.screen)
                
                self.draw_interface(features)
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

def main():
    import os
    from tkinter import Tk, filedialog
    
    audio_file = None
    
    # Se um arquivo foi passado como argumento, usa ele
    if len(sys.argv) >= 2:
        audio_file = sys.argv[1]
    else:
        # Tenta usar um arquivo padrão da pasta musics
        default_audio = os.path.join(os.path.dirname(__file__), 'musics', 'piano.wav')
        
        if os.path.exists(default_audio):
            print(f"Nenhum arquivo especificado. Usando arquivo padrão: {default_audio}")
            print("\nVocê pode:")
            print("1. Usar este arquivo padrão (pressione ENTER)")
            print("2. Escolher outro arquivo (digite 'c' e pressione ENTER)")
            print("3. Sair (digite 's' e pressione ENTER)")
            
            choice = input("\nEscolha: ").strip().lower()
            
            if choice == 's':
                print("Saindo...")
                sys.exit(0)
            elif choice == 'c':
                # Abre diálogo para escolher arquivo
                root = Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                audio_file = filedialog.askopenfilename(
                    title="Escolha um arquivo de áudio",
                    filetypes=[("Arquivos WAV", "*.wav"), ("Todos os arquivos", "*.*")],
                    initialdir=os.path.join(os.path.dirname(__file__), 'musics')
                )
                root.destroy()
                
                if not audio_file:
                    print("Nenhum arquivo selecionado. Saindo...")
                    sys.exit(0)
            else:
                # Usar o arquivo padrão
                audio_file = default_audio
        else:
            # Se não houver arquivo padrão, abre o diálogo
            print("Escolha um arquivo de áudio WAV para visualizar:")
            root = Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            audio_file = filedialog.askopenfilename(
                title="Escolha um arquivo de áudio",
                filetypes=[("Arquivos WAV", "*.wav"), ("Todos os arquivos", "*.*")]
            )
            root.destroy()
            
            if not audio_file:
                print("Nenhum arquivo selecionado. Saindo...")
                sys.exit(0)
    
    if not os.path.exists(audio_file):
        print(f"Erro: Arquivo '{audio_file}' não encontrado.")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("VISUALIZADOR MUSICAL TERAPÊUTICO")
    print("Tecnologia Assistiva para Pessoas com Deficiência Auditiva")
    print("="*60)
    print(f"\nCarregando: {os.path.basename(audio_file)}")
    print("\nControles:")
    print("  ESPAÇO - Pausar/Retomar")
    print("  ESC    - Sair")
    print("="*60 + "\n")
    
    try:
        visualizer = TherapeuticMusicVisualizer(audio_file)
        visualizer.run()
    except Exception as e:
        print(f"\nErro ao executar visualizador: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()