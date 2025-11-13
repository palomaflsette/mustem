"""
VISUALIZADOR TERAPÊUTICO DELICADO - VERSÃO SUAVE
Experiência visual orgânica, fluida e profundamente relaxante
Focado na delicadeza, suavidade e movimento natural
"""

import pygame
import pygame.mixer
import numpy as np
import math
import time
import sys
import wave
import threading
from collections import deque
import colorsys

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
FPS = 60
CHUNK_SIZE = 512  

class DelicateColors:
    """Paleta de cores extremamente suaves e delicadas"""
    
    @staticmethod
    def frequency_to_hue_logarithmic(frequency):
        """
        Calcula a matiz (hue) para uma frequência usando mapeamento
        logarítmico baseado na escala musical cromática (A4 = 440Hz).
        Retorna um valor de 0.0 a 1.0.
        """
        if frequency <= 0:
            return 0.0

        # Calcula o "número da nota" em uma escala contínua (padrão MIDI)
        # A nota Lá 4 (A4) = 440Hz é a nota 69.
        note_number = 69 + 12 * math.log2(frequency / 440.0)

        # O Hue (matiz) é determinado pela posição da nota dentro da oitava (0-11)
        # Usamos o operador de módulo (%) para mapear para o círculo de 12 notas.
        hue = (note_number % 12) / 12.0
        return hue
    
    @staticmethod
    def soft_pastel(base_hue, energy=0.5):
        """Gera cor pastel suave"""
        # Valida parâmetros de entrada
        base_hue = max(0.0, min(1.0, float(base_hue))) if base_hue is not None else 0.0
        energy = max(0.0, min(1.0, float(energy))) if energy is not None else 0.5
        
        # Saturação muito baixa para delicadeza
        saturation = 0.15 + energy * 0.25  # Máximo 40% saturação
        # Brilho alto para suavidade
        value = 0.75 + energy * 0.2  # Entre 75-95% brilho
        
        rgb = colorsys.hsv_to_rgb(base_hue, saturation, value)
        # Garante valores válidos para pygame (0-255)
        return tuple(max(0, min(255, int(c * 255))) for c in rgb)
    
    @staticmethod
    def safe_color(color_tuple, alpha=1.0):
        """Garante que a cor é válida para pygame"""
        if not color_tuple or len(color_tuple) < 3:
            return (100, 100, 150)  # Cor padrão azul suave
        
        alpha = max(0.0, min(1.0, float(alpha)))
        r, g, b = color_tuple[:3]
        
        # Aplica alpha e valida
        return (
            max(0, min(255, int(r * alpha))),
            max(0, min(255, int(g * alpha))),
            max(0, min(255, int(b * alpha)))
        )
    
    @staticmethod
    def flowing_harmonic_color(base_hue, time_phase, frequency_influence, energy=0.5):
        """Cores que fluem harmoniosamente como escoamento laminar"""
        # Validação
        base_hue = max(0.0, min(1.0, float(base_hue or 0.0)))
        energy = max(0.0, min(1.0, float(energy or 0.5)))
        
        # Fluxo harmônico de cores - baseado em teoria das cores
        harmonic_shift = math.sin(time_phase * 0.3) * 0.15  # Oscilação suave ±15%
        frequency_shift = frequency_influence * 0.08  # Influência das frequências
        
        # Hue que flui suavemente
        flowing_hue = (base_hue + harmonic_shift + frequency_shift) % 1.0
        
        # Saturação que respira com a música
        saturation = 0.12 + energy * 0.28 + math.sin(time_phase * 0.5) * 0.06
        
        # Brilho que ondula suavemente
        value = 0.72 + energy * 0.18 + math.sin(time_phase * 0.7) * 0.05
        
        rgb = colorsys.hsv_to_rgb(flowing_hue, saturation, value)
        return tuple(max(0, min(255, int(c * 255))) for c in rgb)
    
    @staticmethod
    def laminar_gradient(hue1, hue2, position, flow_distortion=0.0):
        """Gradiente que simula escoamento laminar"""
        # Posição com distorção de fluxo
        laminar_pos = position + math.sin(position * 6.28) * flow_distortion * 0.1
        laminar_pos = max(0.0, min(1.0, laminar_pos))
        
        # Interpolação suave entre matizes
        hue_diff = hue2 - hue1
        if abs(hue_diff) > 0.5:  # Vai pelo caminho mais curto no círculo de cores
            if hue_diff > 0:
                hue1 += 1.0
            else:
                hue2 += 1.0
                
        blended_hue = (hue1 + (hue2 - hue1) * laminar_pos) % 1.0
        
        # Saturação e brilho suaves
        saturation = 0.18 + laminar_pos * 0.22
        value = 0.75 + math.sin(laminar_pos * 3.14159) * 0.15
        
        rgb = colorsys.hsv_to_rgb(blended_hue, saturation, value)
        return tuple(max(0, min(255, int(c * 255))) for c in rgb)
    
    @staticmethod
    def breathing_gradient(phase):
        """Gradiente suave que respira"""
        # Cores que mudam suavemente como respiração
        base_hues = [0.55, 0.65, 0.15, 0.35]  # Azul, roxo, dourado, verde
        
        # Interpolação suave entre cores
        cycle = (phase % (len(base_hues) * 2)) / len(base_hues)
        hue_index = int(cycle) % len(base_hues)
        next_index = (hue_index + 1) % len(base_hues)
        
        blend = cycle - int(cycle)
        # Suaviza a transição com função senoidal
        smooth_blend = 0.5 + 0.5 * math.sin((blend - 0.5) * math.pi)
        
        hue = base_hues[hue_index] * (1 - smooth_blend) + base_hues[next_index] * smooth_blend
        return DelicateColors.soft_pastel(hue, 0.3)

class InstrumentDetector:
    """Detector de instrumentos específicos na música"""
    
    def __init__(self):
        # Histórico para detecção de padrões
        self.frequency_history = deque(maxlen=30)
        self.energy_history = deque(maxlen=60)
        
        # Detectores específicos
        self.drum_detector = DrumDetector()
        self.melodic_detector = MelodicDetector()
        
    def analyze_instruments(self, spectrum, chunk_data):
        """Analisa e detecta instrumentos na música"""
        self.frequency_history.append(spectrum.copy())
        
        # Detecta bateria e percussão
        drum_events = self.drum_detector.detect_drums(spectrum, chunk_data)
        
        # Detecta instrumentos melódicos
        melodic_events = self.melodic_detector.detect_melodic(spectrum)
        
        return {
            'drums': drum_events,
            'melodic': melodic_events,
            'bass': self.detect_bass_line(spectrum),
            'rhythm_intensity': self.calculate_rhythm_intensity()
        }
    
    def detect_bass_line(self, spectrum):
        """Detecta linha de baixo"""
        if len(spectrum) < 4:
            return 0.0
            
        bass_energy = np.mean(spectrum[:4])  # Frequências baixas
        return min(1.0, bass_energy * 3)
    
    
    def calculate_rhythm_intensity(self):
        """Calcula intensidade rítmica geral"""
        if len(self.frequency_history) < 10:
            return 0.0
            
        # Variação temporal nas frequências baixas
        bass_variation = []
        for freq_data in list(self.frequency_history)[-10:]:
            if len(freq_data) >= 4:
                bass_variation.append(np.mean(freq_data[:4]))
                
        if len(bass_variation) < 5:
            return 0.0
            
        variation = np.std(bass_variation) / (np.mean(bass_variation) + 1e-10)
        return min(1.0, variation)

class DrumDetector:
    """Detector específico para bateria e percussão"""
    
    def __init__(self):
        self.kick_memory = deque(maxlen=20)
        self.snare_memory = deque(maxlen=20)
        self.hihat_memory = deque(maxlen=20)
        
    def detect_drums(self, spectrum, chunk_data):
        """Detecta diferentes elementos da bateria"""
        events = {
            'kick': 0.0,
            'snare': 0.0,
            'hihat': 0.0,
            'crash': 0.0,
            'overall_percussion': 0.0
        }
        
        if len(spectrum) < 8:
            return events
            
        # Kick drum (20-60 Hz) - frequências muito baixas
        kick_energy = np.mean(spectrum[:2]) if len(spectrum) >= 2 else 0
        events['kick'] = self.detect_transient(kick_energy, self.kick_memory, threshold=0.3)
        
        # Snare (150-250 Hz) - frequências médias-baixas com ataque
        snare_energy = np.mean(spectrum[3:5]) if len(spectrum) >= 5 else 0
        events['snare'] = self.detect_transient(snare_energy, self.snare_memory, threshold=0.25)
        
        # Hi-hat (8-12 kHz) - frequências altas
        hihat_energy = np.mean(spectrum[-3:]) if len(spectrum) >= 3 else 0
        events['hihat'] = self.detect_transient(hihat_energy, self.hihat_memory, threshold=0.15)
        
        # Crash/pratos - pico súbito nas altas frequências
        if len(spectrum) >= 6:
            high_freq_energy = np.mean(spectrum[-4:])
            recent_high = np.mean([h[-1] for h in [self.hihat_memory] if len(h) > 0])
            if high_freq_energy > recent_high * 2.5:
                events['crash'] = min(1.0, high_freq_energy * 2)
        
        # Percussão geral - combinação de todos os elementos
        events['overall_percussion'] = min(1.0, 
            events['kick'] * 0.4 + 
            events['snare'] * 0.4 + 
            events['hihat'] * 0.2 + 
            events['crash'] * 0.3
        )
        
        return events
    
    def detect_transient(self, current_energy, memory, threshold=0.2):
        """Detecta transientes (ataques súbitos)"""
        memory.append(current_energy)
        
        if len(memory) < 8:
            return 0.0
            
        recent_avg = np.mean(list(memory)[-8:-1])  # Média dos últimos valores
        
        # Detecta pico súbito
        if current_energy > recent_avg + threshold:
            intensity = (current_energy - recent_avg) / (threshold + 1e-10)
            return min(1.0, intensity * 0.7)
            
        return 0.0

class MelodicDetector:
    """Detector para instrumentos melódicos (piano, strings, etc.)"""
    
    def __init__(self):
        self.harmonic_memory = deque(maxlen=40)
        self.melody_tracker = deque(maxlen=20)
        
    def detect_melodic(self, spectrum):
        """Detecta instrumentos melódicos"""
        events = {
            'piano': 0.0,
            'strings': 0.0,
            'harmony': 0.0,
            'melody_strength': 0.0,
            'chord_progression': 0.0
        }
        
        if len(spectrum) < 8:
            return events
            
        # Piano - rico em harmônicos, frequências médias bem definidas
        piano_range = spectrum[4:10] if len(spectrum) >= 10 else spectrum[4:]
        piano_clarity = self.calculate_harmonic_clarity(piano_range)
        events['piano'] = piano_clarity
        
        # Strings - sustentado, rico em harmônicos, frequências médias-altas
        strings_range = spectrum[6:12] if len(spectrum) >= 12 else spectrum[6:]
        strings_sustain = self.calculate_sustain_quality(strings_range)
        events['strings'] = strings_sustain
        
        # Harmonia geral
        events['harmony'] = self.detect_harmonic_richness(spectrum)
        
        # Força melódica
        events['melody_strength'] = self.calculate_melodic_strength(spectrum)
        
        # Progressão de acordes
        events['chord_progression'] = self.detect_chord_changes(spectrum)
        
        return events
    
    def calculate_harmonic_clarity(self, frequency_range):
        """Calcula clareza harmônica (típico do piano)"""
        if len(frequency_range) < 3:
            return 0.0
            
        # Detecta picos bem definidos
        peaks = []
        for i in range(1, len(frequency_range) - 1):
            if (frequency_range[i] > frequency_range[i-1] and 
                frequency_range[i] > frequency_range[i+1] and
                frequency_range[i] > np.mean(frequency_range) * 1.3):
                peaks.append(frequency_range[i])
        
        if len(peaks) == 0:
            return 0.0
            
        # Clareza baseada no número e definição dos picos
        clarity = min(1.0, len(peaks) / 4.0) * (np.mean(peaks) / (np.std(frequency_range) + 1e-10))
        return min(1.0, clarity * 0.3)
    
    def calculate_sustain_quality(self, frequency_range):
        """Calcula qualidade de sustentação (típico de strings)"""
        if len(frequency_range) < 4:
            return 0.0
            
        self.harmonic_memory.append(frequency_range.copy())
        
        if len(self.harmonic_memory) < 10:
            return 0.0
            
        # Analisa consistência temporal (sustain)
        recent_spectra = list(self.harmonic_memory)[-10:]
        
        consistency_scores = []
        for i in range(len(frequency_range)):
            freq_history = [spectrum[i] if i < len(spectrum) else 0 for spectrum in recent_spectra]
            if len(freq_history) > 5:
                # Sustain = baixa variação + energia consistente
                variation = np.std(freq_history) / (np.mean(freq_history) + 1e-10)
                consistency = 1.0 / (1.0 + variation * 3)
                consistency_scores.append(consistency * np.mean(freq_history))
        
        if len(consistency_scores) == 0:
            return 0.0
            
        return min(1.0, np.mean(consistency_scores) * 0.8)
    
    def detect_harmonic_richness(self, spectrum):
        """Detecta riqueza harmônica geral"""
        if len(spectrum) < 6:
            return 0.0
            
        # Detecta múltiplos harmônicos ativos
        active_bands = sum(1 for x in spectrum if x > 0.1)
        richness = active_bands / len(spectrum)
        
        # Considera também a distribuição de energia
        energy_distribution = np.std(spectrum) / (np.mean(spectrum) + 1e-10)
        
        return min(1.0, richness * energy_distribution * 0.5)
    
    def calculate_melodic_strength(self, spectrum):
        """Calcula força da melodia"""
        self.melody_tracker.append(spectrum.copy())
        
        if len(self.melody_tracker) < 8:
            return 0.0
            
        # Detecta movimento melódico (mudanças nas frequências dominantes)
        recent_spectra = list(self.melody_tracker)[-8:]
        
        # Encontra picos dominantes em cada frame
        dominant_freqs = []
        for spec in recent_spectra:
            if len(spec) > 0:
                dominant_idx = np.argmax(spec)
                dominant_freqs.append(dominant_idx)
        
        if len(dominant_freqs) < 5:
            return 0.0
            
        # Movimento melódico = variação controlada nas frequências dominantes
        freq_changes = np.std(dominant_freqs)
        melodic_activity = min(1.0, freq_changes / len(spectrum) * 4)
        
        return melodic_activity * 0.6
    
    def detect_chord_changes(self, spectrum):
        """Detecta mudanças de acordes"""
        if len(self.harmonic_memory) < 15:
            return 0.0
            
        # Compara espectro atual com espectro de alguns frames atrás
        current = spectrum
        past = list(self.harmonic_memory)[-10]
        
        if len(current) != len(past):
            return 0.0
            
        # Calcula diferença espectral
        spectral_diff = np.sum(np.abs(current - past))
        normalized_diff = spectral_diff / (np.sum(current + past) + 1e-10)
        
        # Mudança de acorde = mudança espectral significativa mas suave
        if 0.2 < normalized_diff < 0.8:
            return min(1.0, normalized_diff * 1.5)
            
        return 0.0

class DrumExplosions:
    """Sistema de explosões para elementos de bateria"""
    
    def __init__(self):
        self.explosions = []
        
    def create_explosion(self, x, y, intensity, explosion_type='kick'):
        """Cria explosão baseada no tipo de elemento de bateria"""
        explosion = {
            'x': x, 'y': y,
            'intensity': intensity,
            'type': explosion_type,
            'particles': [],
            'life': 1.0,
            'age': 0.0,
            'expansion_rate': 50 + intensity * 80
        }
        
        # Cria partículas de matéria escura
        num_particles = int(8 + intensity * 15)
        for i in range(num_particles):
            angle = (i / num_particles) * 2 * math.pi + np.random.random() * 0.5
            speed = 30 + intensity * 50 + np.random.random() * 20
            
            particle = {
                'x': x, 'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 1.0,
                'size': 2 + intensity * 4 + np.random.random() * 3,
                'decay_rate': 0.8 + np.random.random() * 0.4,
                'dark_matter_phase': np.random.random() * 2 * math.pi
            }
            explosion['particles'].append(particle)
            
        self.explosions.append(explosion)
        
    def update(self, dt):
        """Atualiza explosões e desintegração"""
        for explosion in self.explosions[:]:
            explosion['age'] += dt
            explosion['life'] = max(0, 1 - explosion['age'] / 2.0)
            
            # Atualiza partículas
            for particle in explosion['particles'][:]:
                # Movimento
                particle['x'] += particle['vx'] * dt
                particle['y'] += particle['vy'] * dt
                
                # Desaceleração (resistência da matéria escura)
                particle['vx'] *= 0.98
                particle['vy'] *= 0.98
                
                # Desintegração
                particle['life'] -= particle['decay_rate'] * dt
                particle['size'] *= 0.99  # Encolhimento
                
                # Fase de matéria escura
                particle['dark_matter_phase'] += dt * 3
                
                # Remove partícula morta
                if particle['life'] <= 0 or particle['size'] < 0.5:
                    explosion['particles'].remove(particle)
            
            # Remove explosão se sem partículas
            if len(explosion['particles']) == 0 or explosion['life'] <= 0:
                self.explosions.remove(explosion)
                
    def draw(self, screen):
        """Desenha explosões de matéria escura"""
        for explosion in self.explosions:
            explosion_x = explosion['x']
            explosion_y = explosion['y']
            
            # Onda de choque inicial
            if explosion['age'] < 0.3:
                shock_radius = int(explosion['expansion_rate'] * explosion['age'])
                shock_alpha = (0.3 - explosion['age']) / 0.3
                
                # Cor da onda de choque baseada no tipo
                if explosion['type'] == 'kick':
                    shock_color = DelicateColors.soft_pastel(0.0, explosion['intensity'])  # Vermelho
                elif explosion['type'] == 'snare':
                    shock_color = DelicateColors.soft_pastel(0.1, explosion['intensity'])  # Laranja
                else:
                    shock_color = DelicateColors.soft_pastel(0.8, explosion['intensity'])  # Roxo
                    
                final_shock = DelicateColors.safe_color(shock_color, shock_alpha * 0.6)
                
                if shock_radius > 0:
                    try:
                        pygame.draw.circle(screen, final_shock, 
                                         (int(explosion_x), int(explosion_y)), shock_radius, 2)
                    except:
                        pass
            
            # Partículas de matéria escura
            for particle in explosion['particles']:
                if particle['life'] <= 0:
                    continue
                    
                # Efeito de matéria escura (oscilação dimensional)
                dark_oscillation = math.sin(particle['dark_matter_phase']) * 0.3 + 0.7
                
                # Tamanho oscilante
                display_size = max(1, int(particle['size'] * dark_oscillation))
                
                # Cor de matéria escura (tons escuros com brilho sutil)
                darkness = 0.2 + particle['life'] * 0.3
                if explosion['type'] == 'kick':
                    hue = 0.0  # Vermelho escuro
                elif explosion['type'] == 'snare':
                    hue = 0.06  # Laranja escuro
                elif explosion['type'] == 'crash':
                    hue = 0.15  # Amarelo escuro
                else:
                    hue = 0.8   # Roxo escuro
                    
                particle_color = DelicateColors.soft_pastel(hue, darkness)
                final_color = DelicateColors.safe_color(particle_color, particle['life'] * 0.8)
                
                # Posição validada
                px = max(0, min(SCREEN_WIDTH, int(particle['x'])))
                py = max(0, min(SCREEN_HEIGHT, int(particle['y'])))
                
                try:
                    # Núcleo da partícula
                    pygame.draw.circle(screen, final_color, (px, py), display_size)
                    
                    # Aura de matéria escura
                    if display_size > 1:
                        aura_size = display_size + 2
                        aura_color = DelicateColors.safe_color(particle_color, particle['life'] * 0.3)
                        pygame.draw.circle(screen, aura_color, (px, py), aura_size, 1)
                except:
                    continue

class CelestialBodies:
    """Corpos celestes para instrumentos melódicos"""
    
    def __init__(self):
        self.bodies = []
        
    def create_celestial_body(self, x, y, intensity, body_type='piano'):
        """Cria corpo celeste harmônico"""
        body = {
            'x': x, 'y': y,
            'intensity': intensity,
            'type': body_type,
            'life': 3.0 + intensity * 2,
            'age': 0.0,
            'orbit_particles': [],
            'core_pulse_phase': 0.0,
            'harmonic_field': intensity,
            'gravitational_pull': 20 + intensity * 30
        }
        
        # Cria partículas orbitais harmoniosas
        num_orbitals = int(3 + intensity * 8)
        for i in range(num_orbitals):
            orbital_distance = 15 + i * 8 + np.random.random() * 10
            orbital_speed = 0.5 + intensity * 0.8 + np.random.random() * 0.3
            
            orbital = {
                'distance': orbital_distance,
                'angle': (i / num_orbitals) * 2 * math.pi,
                'speed': orbital_speed,
                'size': 1 + intensity * 2,
                'harmonic_phase': np.random.random() * 2 * math.pi,
                'brightness': 0.7 + np.random.random() * 0.3
            }
            body['orbit_particles'].append(orbital)
            
        self.bodies.append(body)
        
    def update(self, dt):
        """Atualiza corpos celestes"""
        for body in self.bodies[:]:
            body['age'] += dt
            body['life'] -= dt / 4
            body['core_pulse_phase'] += dt * 2
            
            # Atualiza órbitas
            for orbital in body['orbit_particles']:
                orbital['angle'] += orbital['speed'] * dt
                orbital['harmonic_phase'] += dt * 1.5
                
                # Calcula posição orbital com perturbação harmônica
                harmonic_offset = math.sin(orbital['harmonic_phase']) * 3
                
                orbital['x'] = body['x'] + (orbital['distance'] + harmonic_offset) * math.cos(orbital['angle'])
                orbital['y'] = body['y'] + (orbital['distance'] + harmonic_offset) * math.sin(orbital['angle'])
                
            # Remove corpo morto
            if body['life'] <= 0:
                self.bodies.remove(body)
                
    def draw(self, screen):
        """Desenha corpos celestes harmoniosos"""
        for body in self.bodies:
            if body['life'] <= 0:
                continue
                
            # Núcleo do corpo celeste
            core_pulse = 0.7 + 0.3 * math.sin(body['core_pulse_phase'])
            core_size = max(2, int((3 + body['intensity'] * 6) * core_pulse))
            
            # Cor baseada no tipo de instrumento
            if body['type'] == 'piano':
                core_hue = 0.15  # Dourado
            elif body['type'] == 'strings':
                core_hue = 0.55  # Azul celestial
            elif body['type'] == 'harmony':
                core_hue = 0.8   # Roxo místico
            else:
                core_hue = 0.3   # Verde etéreo
                
            core_color = DelicateColors.soft_pastel(core_hue, body['intensity'])
            final_core = DelicateColors.safe_color(core_color, body['life'] * 0.9)

            # Posição validada
            bx = max(0, min(SCREEN_WIDTH, int(body['x'])))
            by = max(0, min(SCREEN_HEIGHT, int(body['y'])))
            
            # Campo harmônico (aura)
            aura_radius = int(body['gravitational_pull'] * body['life'])
            if aura_radius > 0:
                aura_color = DelicateColors.safe_color(core_color, body['life'] * 0.2)
                try:
                    pygame.draw.circle(screen, aura_color, (bx, by), aura_radius, 1)
                except:
                    pass
            
            # Núcleo brilhante
            try:
                pygame.draw.circle(screen, final_core, (bx, by), core_size)
                
                # Brilho interno
                if core_size > 2:
                    inner_size = max(1, core_size // 2)
                    inner_color = DelicateColors.safe_color(core_color, body['life'])
                    pygame.draw.circle(screen, inner_color, (bx, by), inner_size)
            except:
                continue
                
            # Partículas orbitais
            for orbital in body['orbit_particles']:
                orbital_brightness = orbital['brightness'] * body['life']
                if orbital_brightness <= 0:
                    continue
                    
                # Oscilação harmônica
                harmonic_glow = math.sin(orbital['harmonic_phase']) * 0.2 + 0.8
                orbital_size = max(1, int(orbital['size'] * harmonic_glow))
                
                # Cor orbital complementar
                orbital_hue = (core_hue + 0.1) % 1.0
                orbital_color = DelicateColors.soft_pastel(orbital_hue, orbital_brightness)
                final_orbital = DelicateColors.safe_color(orbital_color, orbital_brightness * 0.8)
                
                # Posição validada
                ox = max(0, min(SCREEN_WIDTH, int(orbital['x'])))
                oy = max(0, min(SCREEN_HEIGHT, int(orbital['y'])))
                
                try:
                    pygame.draw.circle(screen, final_orbital, (ox, oy), orbital_size)
                    
                    # Trilha orbital sutil
                    if orbital_size > 1:
                        trail_color = DelicateColors.safe_color(orbital_color, orbital_brightness * 0.3)
                        pygame.draw.line(screen, trail_color, (bx, by), (ox, oy), 1)
                except:
                    continue

class MusicalDNAAnalyzer:
    """🧬 ANALISADOR DE DNA MUSICAL - Identidade Visual Única por Música"""
    
    def __init__(self):
        # Memórias temporais para análise profunda
        self.spectral_memory = deque(maxlen=200)
        self.harmonic_memory = deque(maxlen=100) 
        self.rhythm_memory = deque(maxlen=150)
        self.chroma_memory = deque(maxlen=50)
        self.energy_memory = deque(maxlen=80)
        
        # 🧬 DNA MUSICAL ÚNICO - Características Profundas
        self.musical_dna = {
            # 🎵 IDENTIDADE TONAL (que notas/escalas domina)
            'tonal_center': 0.0,                    # Tom principal (0-11: C, C#, D...)
            'mode_brightness': 0.5,                 # Maior=1.0, Menor=0.0, Modal=0.5
            'chromatic_signature': np.zeros(12),    # Assinatura cromática única
            'scale_stability': 0.0,                 # Estabilidade tonal
            
            # 🥁 IDENTIDADE RÍTMICA (como se move no tempo)
            'tempo_stability': 0.0,                 # Consistência do tempo
            'rhythmic_complexity': 0.0,             # Sincopas, polirritmos
            'beat_pattern_dna': np.zeros(16),       # Padrão único de batidas
            'syncopation_index': 0.0,               # Índice de sincopa
            'groove_signature': deque(maxlen=32),   # Assinatura do groove
            
            # 🎼 IDENTIDADE HARMÔNICA (como as notas se relacionam)
            'harmonic_richness': 0.0,               # Densidade harmônica
            'consonance_ratio': 0.5,                # Consonância vs Dissonância
            'chord_complexity': 0.0,                # Complexidade dos acordes
            'harmonic_rhythm': deque(maxlen=20),    # Ritmo harmônico
            'tension_release_curve': deque(maxlen=40), # Curva tensão-resolução
            
            # 🎶 IDENTIDADE MELÓDICA (como a melodia se comporta)
            'melodic_range': 0.0,                   # Amplitude melódica
            'melodic_direction_bias': 0.0,          # Tendência ascendente/descendente
            'interval_signature': np.zeros(12),     # Assinatura de intervalos
            'phrase_complexity': 0.0,               # Complexidade das frases
            'melodic_repetition': 0.0,              # Fator de repetição melódica
            
            # 🔊 IDENTIDADE TÍMBRICA (como soa, textura)
            'spectral_centroid': 0.0,               # Brilho tímbrico
            'spectral_rolloff': 0.0,                # Conteúdo de agudos
            'spectral_flatness': 0.0,               # Ruído vs tonal
            'timbral_flux': 0.0,                    # Mudança tímbrica
            'formant_signature': np.zeros(5),       # Assinatura de formantes
            
            # 📊 IDENTIDADE DINÂMICA (energia e intensidade)
            'dynamic_range': 0.0,                   # Alcance dinâmico
            'energy_variance': 0.0,                 # Variação energética
            'attack_sharpness': 0.0,                # Nitidez dos ataques
            'sustain_character': 0.0,               # Caráter de sustentação
            'decay_profile': np.zeros(8),           # Perfil de decaimento
            
            # 🏗️ IDENTIDADE ESTRUTURAL (organização musical)
            'phrase_length_avg': 0.0,               # Comprimento de frases
            'section_contrast': 0.0,                # Contraste entre seções
            'repetition_density': 0.0,              # Densidade de repetições
            'surprise_quotient': 0.0,               # Quociente de surpresa
            'structural_complexity': 0.0,           # Complexidade estrutural
            
            # 🌊 IDENTIDADE DE FLUXO (como flui no tempo)
            'rhythmic_flow': deque(maxlen=60),      # Fluxo rítmico
            'harmonic_flow': deque(maxlen=40),      # Fluxo harmônico
            'energy_flow': deque(maxlen=50),        # Fluxo energético
            'texture_evolution': deque(maxlen=30),  # Evolução da textura
        }
        
        # 🎨 MAPEAMENTO DNA → ELEMENTOS VISUAIS
        self.visual_dna_mapping = {
            'spiral_curvature_factor': 1.0,         # Curvatura da espiral
            'particle_behavior_type': 'harmonic',   # Tipo de comportamento
            'color_evolution_speed': 1.0,           # Velocidade de mudança de cor
            'geometric_complexity': 1.0,            # Complexidade geométrica
            'flow_dynamics_type': 'laminar',        # Tipo de dinâmica de fluxo
            'symmetry_breaking_factor': 0.0,        # Quebra de simetria
            'fractional_dimensions': np.zeros(3),   # Dimensões fractais
            'resonance_frequencies': np.zeros(8),   # Frequências de ressonância visual
        }
    
    def analyze_musical_dna(self, spectrum, chunk_data, tempo_estimate=120):
        """🧬 Análise completa do DNA musical"""
        
        # Armazena dados para análise temporal
        self.spectral_memory.append(spectrum.copy())
        self.energy_memory.append(np.sum(spectrum))
        
        # Análise cromática (notas musicais)
        chroma_vector = self.extract_chroma_features(spectrum)
        self.chroma_memory.append(chroma_vector)
        
        # 🎵 IDENTIDADE TONAL
        self.analyze_tonal_identity(chroma_vector)
        
        # 🥁 IDENTIDADE RÍTMICA  
        self.analyze_rhythmic_identity(chunk_data, tempo_estimate)
        
        # 🎼 IDENTIDADE HARMÔNICA
        self.analyze_harmonic_identity(spectrum)
        
        # 🎶 IDENTIDADE MELÓDICA
        self.analyze_melodic_identity(spectrum)
        
        # 🔊 IDENTIDADE TÍMBRICA
        self.analyze_timbral_identity(spectrum, chunk_data)
        
        # 📊 IDENTIDADE DINÂMICA
        self.analyze_dynamic_identity()
        
        # 🏗️ IDENTIDADE ESTRUTURAL
        self.analyze_structural_identity()
        
        # 🌊 FLUXOS TEMPORAIS
        self.analyze_temporal_flows()
        
        # 🎨 MAPEIA DNA PARA ELEMENTOS VISUAIS
        self.map_dna_to_visual_elements()
        
        return self.musical_dna.copy()
    
    def extract_chroma_features(self, spectrum):
        """Extrai características cromáticas (notas musicais)"""
        # Mapeia espectro para 12 classes de altura (C, C#, D, D#, etc.)
        chroma = np.zeros(12)
        
        for i, energy in enumerate(spectrum):
            # Mapeia banda espectral para nota musical
            # Aproximação simples: divide espectro em 12 partes
            chroma_index = i % 12
            chroma[chroma_index] += energy
            
        # Normaliza
        if np.sum(chroma) > 0:
            chroma /= np.sum(chroma)
            
        return chroma
    
    def analyze_tonal_identity(self, chroma_vector):
        """🎵 Analisa identidade tonal da música"""
        
        # Centro tonal (nota mais proeminente)
        dominant_note = np.argmax(chroma_vector)
        self.musical_dna['tonal_center'] = (
            self.musical_dna['tonal_center'] * 0.98 + dominant_note * 0.02
        )
        
        # Brilho modal (maior vs menor)
        # Aproximação: notas maiores vs menores
        major_notes = [0, 2, 4, 5, 7, 9, 11]  # C, D, E, F, G, A, B
        minor_notes = [1, 3, 6, 8, 10]         # C#, D#, F#, G#, A#
        
        major_energy = sum(chroma_vector[note] for note in major_notes)
        minor_energy = sum(chroma_vector[note] for note in minor_notes)
        
        if major_energy + minor_energy > 0:
            brightness = major_energy / (major_energy + minor_energy)
            self.musical_dna['mode_brightness'] = (
                self.musical_dna['mode_brightness'] * 0.95 + brightness * 0.05
            )
        
        # Assinatura cromática (distribuição de notas)
        self.musical_dna['chromatic_signature'] = (
            self.musical_dna['chromatic_signature'] * 0.99 + chroma_vector * 0.01
        )
        
        # Estabilidade tonal
        if len(self.chroma_memory) > 10:
            recent_chromas = list(self.chroma_memory)[-10:]
            stability = 1.0 - np.mean([
                np.std([chroma[i] for chroma in recent_chromas])
                for i in range(12)
            ])
            self.musical_dna['scale_stability'] = (
                self.musical_dna['scale_stability'] * 0.9 + stability * 0.1
            )
    
    def analyze_rhythmic_identity(self, chunk_data, tempo_estimate):
        """🥁 Analisa identidade rítmica"""
        
        # Detecta onset (início de notas/batidas)
        onset_strength = self.detect_onset_strength(chunk_data)
        self.rhythm_memory.append(onset_strength)
        
        # Complexidade rítmica (variação nos onsets)
        if len(self.rhythm_memory) > 20:
            rhythm_variance = np.var(list(self.rhythm_memory)[-20:])
            complexity = min(1.0, rhythm_variance * 10)
            self.musical_dna['rhythmic_complexity'] = (
                self.musical_dna['rhythmic_complexity'] * 0.95 + complexity * 0.05
            )
        
        # Padrão de beat único
        beat_position = int((len(self.rhythm_memory) % 16))
        self.musical_dna['beat_pattern_dna'][beat_position] = (
            self.musical_dna['beat_pattern_dna'][beat_position] * 0.9 + onset_strength * 0.1
        )
        
        # Índice de sincopa (off-beat emphasis)
        if len(self.rhythm_memory) >= 8:
            recent_onsets = list(self.rhythm_memory)[-8:]
            on_beat = sum(recent_onsets[i] for i in [0, 2, 4, 6])  # Tempos fortes
            off_beat = sum(recent_onsets[i] for i in [1, 3, 5, 7]) # Tempos fracos
            
            if on_beat + off_beat > 0:
                syncopation = off_beat / (on_beat + off_beat)
                self.musical_dna['syncopation_index'] = (
                    self.musical_dna['syncopation_index'] * 0.9 + syncopation * 0.1
                )
        
        # Assinatura do groove
        groove_value = onset_strength * (1 + self.musical_dna['syncopation_index'])
        self.musical_dna['groove_signature'].append(groove_value)
    
    def detect_onset_strength(self, chunk_data):
        """Detecta força de onset (início de nota/batida)"""
        if len(chunk_data) < 10:
            return 0.0
            
        # Detecta mudança súbita de energia
        energy_diff = np.diff(np.abs(chunk_data))
        onset_strength = np.mean(np.maximum(energy_diff, 0))
        
        return min(1.0, onset_strength * 1000)  # Normaliza
    
    def analyze_harmonic_identity(self, spectrum):
        """🎼 Analisa identidade harmônica"""
        
        # Riqueza harmônica (número de componentes ativas)
        active_bands = sum(1 for x in spectrum if x > 0.1)
        richness = active_bands / len(spectrum)
        self.musical_dna['harmonic_richness'] = (
            self.musical_dna['harmonic_richness'] * 0.95 + richness * 0.05
        )
        
        # Armazena para análise harmônica
        self.harmonic_memory.append(spectrum.copy())
        
        # Ratio consonância/dissonância
        if len(spectrum) >= 8:
            # Aproximação: baixas frequências = consonantes, altas = dissonantes
            consonant_energy = np.mean(spectrum[:4])
            dissonant_energy = np.mean(spectrum[4:])
            
            if consonant_energy + dissonant_energy > 0:
                consonance = consonant_energy / (consonant_energy + dissonant_energy)
                self.musical_dna['consonance_ratio'] = (
                    self.musical_dna['consonance_ratio'] * 0.92 + consonance * 0.08
                )
        
        # Complexidade de acordes (distribuição de energia)
        if len(spectrum) > 0:
            chord_complexity = np.std(spectrum) / (np.mean(spectrum) + 1e-10)
            self.musical_dna['chord_complexity'] = (
                self.musical_dna['chord_complexity'] * 0.9 + chord_complexity * 0.1
            )
        
        # Ritmo harmônico (mudanças nas harmonias)
        if len(self.harmonic_memory) >= 2:
            current_harmony = spectrum
            previous_harmony = self.harmonic_memory[-2]
            
            harmonic_change = np.sum(np.abs(current_harmony - previous_harmony))
            self.musical_dna['harmonic_rhythm'].append(harmonic_change)
            
        # Curva tensão-resolução (baseada na dissonância)
        tension_level = 1.0 - self.musical_dna['consonance_ratio']
        self.musical_dna['tension_release_curve'].append(tension_level)
    
    def analyze_melodic_identity(self, spectrum):
        """🎶 Analisa identidade melódica"""
        
        # Range melódico (amplitude frequencial)
        if len(spectrum) > 0:
            # Encontra frequências com energia significativa
            significant_freqs = [i for i, energy in enumerate(spectrum) if energy > 0.1]
            
            if len(significant_freqs) > 1:
                melodic_range = (max(significant_freqs) - min(significant_freqs)) / len(spectrum)
                self.musical_dna['melodic_range'] = (
                    self.musical_dna['melodic_range'] * 0.9 + melodic_range * 0.1
                )
        
        # Direção melódica (ascendente/descendente)
        if len(self.spectral_memory) >= 2:
            current_centroid = self.calculate_spectral_centroid(spectrum)
            previous_centroid = self.calculate_spectral_centroid(self.spectral_memory[-2])
            
            direction = (current_centroid - previous_centroid) / len(spectrum)
            direction = np.tanh(direction * 5)  # Normaliza entre -1 e 1
            
            self.musical_dna['melodic_direction_bias'] = (
                self.musical_dna['melodic_direction_bias'] * 0.95 + direction * 0.05
            )
        
        # Assinatura de intervalos
        if len(self.spectral_memory) >= 5:
            # Analisa intervalos entre picos espectrais
            recent_spectra = list(self.spectral_memory)[-5:]
            interval_counts = np.zeros(12)
            
            for spec in recent_spectra:
                peaks = self.find_spectral_peaks(spec)
                for i in range(len(peaks)-1):
                    interval = (peaks[i+1] - peaks[i]) % 12
                    interval_counts[interval] += 1
            
            if np.sum(interval_counts) > 0:
                interval_signature = interval_counts / np.sum(interval_counts)
                self.musical_dna['interval_signature'] = (
                    self.musical_dna['interval_signature'] * 0.9 + interval_signature * 0.1
                )
    
    def calculate_spectral_centroid(self, spectrum):
        """Calcula centroide espectral"""
        if np.sum(spectrum) == 0:
            return 0
        
        indices = np.arange(len(spectrum))
        return np.sum(indices * spectrum) / np.sum(spectrum)
    
    def find_spectral_peaks(self, spectrum, threshold=0.1):
        """Encontra picos no espectro"""
        peaks = []
        for i in range(1, len(spectrum) - 1):
            if (spectrum[i] > spectrum[i-1] and 
                spectrum[i] > spectrum[i+1] and 
                spectrum[i] > threshold):
                peaks.append(i)
        return peaks
    
    def analyze_timbral_identity(self, spectrum, chunk_data):
        """🔊 Analisa identidade tímbrica"""
        
        # Centroide espectral (brilho)
        centroid = self.calculate_spectral_centroid(spectrum)
        normalized_centroid = centroid / len(spectrum)
        self.musical_dna['spectral_centroid'] = (
            self.musical_dna['spectral_centroid'] * 0.9 + normalized_centroid * 0.1
        )
        
        # Rolloff espectral (85% da energia)
        cumsum = np.cumsum(spectrum)
        total_energy = cumsum[-1]
        rolloff_index = np.where(cumsum >= 0.85 * total_energy)[0]
        
        if len(rolloff_index) > 0:
            rolloff = rolloff_index[0] / len(spectrum)
            self.musical_dna['spectral_rolloff'] = (
                self.musical_dna['spectral_rolloff'] * 0.9 + rolloff * 0.1
            )
        
        # Planura espectral (ruído vs tonal)
        if len(spectrum) > 0 and np.sum(spectrum) > 0:
            geometric_mean = np.exp(np.mean(np.log(spectrum + 1e-10)))
            arithmetic_mean = np.mean(spectrum)
            flatness = geometric_mean / arithmetic_mean
            
            self.musical_dna['spectral_flatness'] = (
                self.musical_dna['spectral_flatness'] * 0.9 + flatness * 0.1
            )
        
        # Fluxo tímbrico (mudança espectral)
        if len(self.spectral_memory) >= 2:
            current = spectrum
            previous = self.spectral_memory[-2]
            flux = np.sum(np.abs(current - previous))
            
            self.musical_dna['timbral_flux'] = (
                self.musical_dna['timbral_flux'] * 0.9 + flux * 0.1
            )
    
    def analyze_dynamic_identity(self):
        """📊 Analisa identidade dinâmica"""
        
        if len(self.energy_memory) < 10:
            return
            
        recent_energies = list(self.energy_memory)[-20:]
        
        # Range dinâmico
        dynamic_range = (max(recent_energies) - min(recent_energies)) / (max(recent_energies) + 1e-10)
        self.musical_dna['dynamic_range'] = (
            self.musical_dna['dynamic_range'] * 0.9 + dynamic_range * 0.1
        )
        
        # Variância energética
        energy_variance = np.var(recent_energies) / (np.mean(recent_energies) + 1e-10)
        self.musical_dna['energy_variance'] = (
            self.musical_dna['energy_variance'] * 0.9 + energy_variance * 0.1
        )
        
        # Nitidez dos ataques
        energy_diffs = np.diff(recent_energies)
        attack_sharpness = np.mean(np.maximum(energy_diffs, 0))
        self.musical_dna['attack_sharpness'] = (
            self.musical_dna['attack_sharpness'] * 0.9 + attack_sharpness * 0.1
        )
    
    def analyze_structural_identity(self):
        """🏗️ Analisa identidade estrutural"""
        
        # Densidade de repetições
        if len(self.spectral_memory) >= 20:
            recent_spectra = list(self.spectral_memory)[-20:]
            
            # Calcula similaridade entre espectros
            similarities = []
            for i in range(len(recent_spectra)):
                for j in range(i+1, len(recent_spectra)):
                    similarity = self.calculate_cosine_similarity(
                        recent_spectra[i], recent_spectra[j]
                    )
                    similarities.append(similarity)
            
            if similarities:
                repetition_density = np.mean(similarities)
                self.musical_dna['repetition_density'] = (
                    self.musical_dna['repetition_density'] * 0.95 + repetition_density * 0.05
                )
        
        # Quociente de surpresa (mudanças inesperadas)
        if len(self.energy_memory) >= 10:
            recent_energies = list(self.energy_memory)[-10:]
            expected_energy = np.mean(recent_energies[:-1])
            actual_energy = recent_energies[-1]
            
            surprise = abs(actual_energy - expected_energy) / (expected_energy + 1e-10)
            self.musical_dna['surprise_quotient'] = (
                self.musical_dna['surprise_quotient'] * 0.9 + surprise * 0.1
            )
    
    def calculate_cosine_similarity(self, vec1, vec2):
        """Calcula similaridade cosseno entre dois vetores"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0
            
        return dot_product / (norm1 * norm2)
    
    def analyze_temporal_flows(self):
        """🌊 Analisa fluxos temporais"""
        
        # Fluxo rítmico
        if len(self.rhythm_memory) >= 10:
            recent_rhythm = list(self.rhythm_memory)[-10:]
            rhythm_flow = np.mean(recent_rhythm)
            self.musical_dna['rhythmic_flow'].append(rhythm_flow)
        
        # Fluxo harmônico
        if len(self.harmonic_memory) >= 5:
            recent_harmonics = list(self.harmonic_memory)[-5:]
            harmonic_flow = np.mean([np.sum(h) for h in recent_harmonics])
            self.musical_dna['harmonic_flow'].append(harmonic_flow)
        
        # Fluxo energético
        if len(self.energy_memory) >= 10:
            recent_energies = list(self.energy_memory)[-10:]
            energy_flow = np.mean(recent_energies)
            self.musical_dna['energy_flow'].append(energy_flow)
    
    def map_dna_to_visual_elements(self):
        """🎨 Mapeia DNA musical para elementos visuais únicos"""
        
        # Curvatura da espiral baseada na complexidade melódica
        melodic_complexity = (
            self.musical_dna['melodic_range'] * 
            self.musical_dna['interval_signature'].std()
        )
        self.visual_dna_mapping['spiral_curvature_factor'] = 0.5 + melodic_complexity * 1.5
        
        # Tipo de comportamento das partículas
        if self.musical_dna['rhythmic_complexity'] > 0.6:
            self.visual_dna_mapping['particle_behavior_type'] = 'chaotic'
        elif self.musical_dna['consonance_ratio'] > 0.7:
            self.visual_dna_mapping['particle_behavior_type'] = 'harmonic'
        else:
            self.visual_dna_mapping['particle_behavior_type'] = 'orbital'
        
        # Velocidade de evolução das cores
        tonal_stability = self.musical_dna.get('scale_stability', 0.5)
        self.visual_dna_mapping['color_evolution_speed'] = 0.3 + (1 - tonal_stability) * 1.7
        
        # Complexidade geométrica
        structural_complexity = (
            self.musical_dna['harmonic_richness'] + 
            self.musical_dna['rhythmic_complexity'] +
            self.musical_dna.get('phrase_complexity', 0)
        ) / 3.0
        self.visual_dna_mapping['geometric_complexity'] = 0.5 + structural_complexity * 2.0
        
        # Tipo de dinâmica de fluxo
        if self.musical_dna['dynamic_range'] > 0.7:
            self.visual_dna_mapping['flow_dynamics_type'] = 'turbulent'
        elif self.musical_dna['energy_variance'] > 0.5:
            self.visual_dna_mapping['flow_dynamics_type'] = 'transitional'
        else:
            self.visual_dna_mapping['flow_dynamics_type'] = 'laminar'
        
        # Fator de quebra de simetria
        asymmetry = (
            abs(self.musical_dna['melodic_direction_bias']) + 
            self.musical_dna['syncopation_index'] +
            self.musical_dna.get('surprise_quotient', 0)
        ) / 3.0
        self.visual_dna_mapping['symmetry_breaking_factor'] = asymmetry
        
        # Frequências de ressonância visual
        chromatic_sig = self.musical_dna['chromatic_signature']
        if np.sum(chromatic_sig) > 0:
            # Mapeia notas musicais para frequências visuais
            for i in range(min(8, len(chromatic_sig))):
                self.visual_dna_mapping['resonance_frequencies'][i] = chromatic_sig[i]

class GentleAudioAnalyzer:
    """Analisador de áudio ultra-suave"""
    
    def __init__(self, audio_file):
        print("🌸 Preparando experiência delicada...")
        
        self.load_audio(audio_file)
        self.chunk_size = CHUNK_SIZE
        self.audio_start_time = None
        
        # Análise ultra-suavizada
        self.spectrum = np.zeros(16)  # Apenas 16 bandas para simplicidade
        self.smooth_spectrum = np.zeros(16)
        self.ultra_smooth = np.zeros(16)
        
        # Estados de serenidade
        self.serenity_level = 0.5
        self.flow_rhythm = 0.0
        self.breath_cycle = 0.0
        self.gentle_energy = 0.0
        
        # Histórico para suavização
        self.energy_memory = deque(maxlen=60)  # 1 segundo de memória
        
        # Detector de instrumentos
        self.instrument_detector = InstrumentDetector()
        self.current_chunk_data = np.zeros(CHUNK_SIZE)
        
        # 🧬 DNA Musical Analyzer - Identidade Única
        self.dna_analyzer = MusicalDNAAnalyzer()
        
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=1, buffer=256)
        pygame.mixer.init()
        
    def load_audio(self, filename):
        """Carrega áudio com processamento gentil"""
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
        print(f"🎵 Áudio preparado com delicadeza")
        
    def start_playback(self):
        try:
            pygame.mixer.music.play()
            self.audio_start_time = time.time()
            print("💫 Experiência delicada iniciada...")
        except Exception as e:
            print(f"❌ Erro ao iniciar playback: {e}")
    
    def start_playbook_safe(self):
        """Versão segura do start_playback"""
        try:
            self.start_playback()
        except Exception as e:
            print(f"⚠️ Problema no áudio: {e}")
            print("🌸 Continuando em modo silencioso...")
        
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
        # Janela ultra-suave
        return chunk * np.hanning(len(chunk))
        
    def analyze_gently(self):
        """Análise extremamente suave e orgânica com identidade musical e detecção de instrumentos"""
        chunk = self.get_current_chunk()
        self.current_chunk_data = chunk.copy()
        
        if len(chunk) == 0 or np.max(np.abs(chunk)) < 1e-6:
            return self.get_serene_state()
            
        # FFT com suavização extrema
        fft = np.fft.rfft(chunk)
        magnitude = np.abs(fft)

         # --- NOVA PARTE: CALCULAR FREQUÊNCIAS ---
        freqs = np.fft.rfftfreq(len(chunk), 1.0 / self.sample_rate)
        
        # Encontra a frequência dominante (pico de energia)
        dominant_freq = 0
        if len(magnitude) > 0 and np.max(magnitude) > 0:
            dominant_index = np.argmax(magnitude)
            dominant_freq = freqs[dominant_index]
            
        # Calcula a frequência central de cada uma das 16 bandas
        band_center_freqs = np.zeros(16)
        for i in range(16):
            start_idx = int((i / 16) * len(freqs))
            end_idx = int(((i + 1) / 16) * len(freqs))
            if end_idx > start_idx:
                band_center_freqs[i] = np.mean(freqs[start_idx:end_idx])

        
        
        # Reduz para 16 bandas suaves
        new_spectrum = np.zeros(16)
        for i in range(16):
            start_idx = int((i / 16) * len(magnitude))
            end_idx = int(((i + 1) / 16) * len(magnitude))
            if end_idx > start_idx:
                new_spectrum[i] = np.mean(magnitude[start_idx:end_idx])
                
        # Tripla suavização para máxima delicadeza
        alpha1 = 0.02  # Ultra-lento
        alpha2 = 0.05  # Muito lento
        alpha3 = 0.1   # Lento
        
        self.spectrum = self.spectrum * (1 - alpha1) + new_spectrum * alpha1
        self.smooth_spectrum = self.smooth_spectrum * (1 - alpha2) + self.spectrum * alpha2
        self.ultra_smooth = self.ultra_smooth * (1 - alpha3) + self.smooth_spectrum * alpha3
        
        # Estados de serenidade
        total_energy = np.sum(self.ultra_smooth)
        self.energy_memory.append(total_energy)
        
        if len(self.energy_memory) > 10:
            avg_energy = np.mean(list(self.energy_memory)[-30:])
            self.gentle_energy = avg_energy
            
            # Nível de serenidade baseado na consistência
            energy_variance = np.var(list(self.energy_memory)[-20:])
            self.serenity_level = 0.3 + (1.0 - min(1.0, energy_variance * 10)) * 0.6
            
        # Ritmo de fluxo orgânico
        self.flow_rhythm += 0.01 * (1 + self.gentle_energy)
        
        # Ciclo de respiração natural
        self.breath_cycle += 0.005 * (0.5 + self.serenity_level * 0.5)
        
        # Extração de características musicais avançadas
        beat_energy = self.detect_beat_energy(chunk)
        harmonic_richness = self.calculate_harmonic_richness(magnitude)
        melodic_direction = self.calculate_melodic_direction()
        
        # Análise de instrumentos específicos
        instruments = self.instrument_detector.analyze_instruments(self.ultra_smooth, chunk)
        
        # 🧬 ANÁLISE DE DNA MUSICAL - Identidade Única
        musical_dna = self.dna_analyzer.analyze_musical_dna(self.ultra_smooth, chunk)
        
        return {
            'spectrum': self.ultra_smooth,
            'dominant_freq': dominant_freq, # << NOVO
            'band_center_freqs': band_center_freqs, # << NOVO
            'serenity_level': self.serenity_level,
            'gentle_energy': self.gentle_energy,
            'flow_rhythm': self.flow_rhythm,
            'breath_cycle': self.breath_cycle,
            'current_time': self.get_current_time(),
            'beat_energy': beat_energy,
            'harmonic_richness': harmonic_richness,
            'melodic_direction': melodic_direction,
            'instruments': instruments,
            'musical_dna': musical_dna,  # 🧬 DNA Musical único
            'visual_dna': self.dna_analyzer.visual_dna_mapping  # 🎨 Mapeamento visual
        }
    
    def detect_beat_energy(self, chunk):
        """Detecta energia de beat de forma suave"""
        instant_energy = np.mean(chunk ** 2)
        
        if len(self.energy_memory) < 8:
            return 0.0
            
        recent_avg = np.mean(list(self.energy_memory)[-8:])
        beat_strength = max(0, (instant_energy - recent_avg) / (recent_avg + 1e-10))
        
        return min(1.0, beat_strength * 0.5)  # Suavizado
    
    def calculate_harmonic_richness(self, magnitude):
        """Calcula riqueza harmônica da música"""
        if len(magnitude) == 0:
            return 0.5
            
        # Detecta picos harmônicos
        peaks = []
        for i in range(2, len(magnitude) - 2):
            if magnitude[i] > magnitude[i-1] and magnitude[i] > magnitude[i+1]:
                if magnitude[i] > np.mean(magnitude) * 1.2:  # Threshold
                    peaks.append(magnitude[i])
        
        # Riqueza baseada no número e intensidade dos picos
        if len(peaks) == 0:
            return 0.1
            
        richness = min(1.0, len(peaks) / 20.0) * (np.std(peaks) / (np.mean(peaks) + 1e-10))
        return richness * 0.3 + 0.2  # Normalizado e suavizado
    
    def calculate_melodic_direction(self):
        """Calcula direção melódica"""
        if len(self.energy_memory) < 16:
            return 0.0
            
        recent = list(self.energy_memory)[-16:]
        
        # Tendência simples
        first_half = np.mean(recent[:8])
        second_half = np.mean(recent[8:])
        
        direction = (second_half - first_half) / (first_half + 1e-10)
        return np.tanh(direction * 3) * 0.5  # Normalizado e suavizado
        
    def get_serene_state(self):
        return {
            'spectrum': np.ones(16) * 0.1,
            'serenity_level': 0.8,
            'gentle_energy': 0.1,
            'flow_rhythm': self.flow_rhythm,
            'breath_cycle': self.breath_cycle,
            'current_time': self.get_current_time(),
            'beat_energy': 0.0,
            'harmonic_richness': 0.3,
            'melodic_direction': 0.0
        }

class UniqueMusicalSpiral:
    """Espiral winding que cria identidade visual única para cada música"""
    
    def __init__(self, center_x, center_y):
        self.center_x = center_x
        self.center_y = center_y
        
        # Espiral winding matemática
        self.spiral_points = []
        self.max_spiral_points = 120
        self.golden_ratio = (1 + math.sqrt(5)) / 2
        self.current_angle = 0.0
        
        # Identidade musical única
        self.musical_dna = {
            'spectral_signature': np.zeros(12),  # Assinatura espectral
            'rhythm_pattern': deque(maxlen=8),   # Padrão rítmico
            'harmonic_richness': 0.5,            # Riqueza harmônica
            'melodic_tendency': 0.0,             # Tendência melódica
            'energy_character': 0.3              # Caráter energético
        }
        
        # Elementos matemáticos únicos
        self.fibonacci_points = []
        self.harmonic_particles = []
        self.beat_resonance_rings = []
        self.sacred_geometry = []
        
        # Sistemas de instrumentos específicos
        self.drum_explosions = DrumExplosions()
        self.celestial_bodies = CelestialBodies()
        
        # 🧬 Sistema de DNA Visual Único
        self.dna_visual_elements = {
            'unique_spiral_patterns': [],
            'dna_color_palette': [],
            'signature_geometries': [],
            'rhythmic_signatures': [],
            'harmonic_fingerprints': [],
            'tonal_identity_markers': [],
        }
            
    def update(self, spectrum, gentle_energy, serenity_level, dt, instruments=None, musical_dna=None, visual_dna=None):
        """Atualização com extração de identidade musical única e detecção de instrumentos"""
        
        # Processa DNA musical para identidade visual única
        if musical_dna and visual_dna:
            self.process_musical_dna(musical_dna, visual_dna)
        
        # Extrai identidade musical única
        self.extract_musical_identity(spectrum, gentle_energy)
        
        # Adiciona ponto à espiral winding
        self.add_spiral_point(spectrum, gentle_energy, dt)
        
        # Atualiza elementos matemáticos especiais
        self.update_fibonacci_constellation(dt)
        self.update_harmonic_particles(spectrum, dt)
        
        # Cria ressonâncias de energia
        if gentle_energy > 0.15:
            self.create_energy_resonance(gentle_energy, serenity_level)
            
        # Atualiza ressonâncias existentes
        self.update_energy_resonances(dt)
        
        # Geometria sagrada baseada na música
        self.update_sacred_geometry(spectrum, serenity_level, dt)
        
        # Processa eventos de instrumentos específicos
        if instruments:
            self.process_instrument_events(instruments, dt)
            
        # 🧬 PROCESSA DNA MUSICAL ÚNICO
        if musical_dna and visual_dna:
            self.process_musical_dna(musical_dna, visual_dna)
    
    def extract_musical_identity(self, spectrum, energy):
        """Extrai características únicas que definem a música"""
        # Assinatura espectral (frequências dominantes)
        if len(spectrum) >= 12:
            for i in range(12):
                band_idx = int(i * len(spectrum) / 12)
                target = spectrum[band_idx] if band_idx < len(spectrum) else 0
                # Suavização extrema para identidade estável
                self.musical_dna['spectral_signature'][i] = (
                    self.musical_dna['spectral_signature'][i] * 0.995 + target * 0.005
                )
        
        # Padrão rítmico
        self.musical_dna['rhythm_pattern'].append(energy)
        
        # Riqueza harmônica
        if len(spectrum) > 0:
            richness = np.std(spectrum) / (np.mean(spectrum) + 1e-10)
            self.musical_dna['harmonic_richness'] = (
                self.musical_dna['harmonic_richness'] * 0.99 + richness * 0.01
            )
        
        # Tendência melódica
        if len(list(self.musical_dna['rhythm_pattern'])) >= 3:
            recent = list(self.musical_dna['rhythm_pattern'])[-3:]
            trend = (recent[-1] - recent[0]) / (len(recent) + 1e-10)
            self.musical_dna['melodic_tendency'] = (
                self.musical_dna['melodic_tendency'] * 0.98 + trend * 0.02
            )
    
    def add_spiral_point(self, spectrum, energy, dt):
        """Adiciona ponto à espiral com base na música"""
        if len(self.spiral_points) >= self.max_spiral_points:
            self.spiral_points.pop(0)  # Remove o mais antigo
        
        # Incremento do ângulo baseado na proporção áurea + energia musical
        angle_base = 2 * math.pi / self.golden_ratio
        energy_influence = energy * math.pi / 8  # Variação de até 22.5°
        self.current_angle += angle_base + energy_influence
        
        # Raio baseado na posição na espiral + características musicais
        base_radius = len(self.spiral_points) * 0.8
        
        # Modulação baseada na identidade musical
        dominant_freq = np.argmax(self.musical_dna['spectral_signature']) if np.sum(self.musical_dna['spectral_signature']) > 0 else 0
        
        radius_modulation = 1 + energy * self.musical_dna['harmonic_richness'] * 0.5
        final_radius = base_radius * radius_modulation
        
        # Posição do ponto
        x = self.center_x + final_radius * math.cos(self.current_angle)
        y = self.center_y + final_radius * math.sin(self.current_angle)
        
        # Cor única baseada na identidade musical
        # Mapeia frequência dominante para matiz
        hue = (dominant_freq / 12.0 + self.musical_dna['melodic_tendency'] * 0.1) % 1.0
        
        # Ondulação laminar baseada em frequências
        laminar_phase = self.current_angle * 0.2 + len(self.spiral_points) * 0.1
        frequency_wave = np.mean(spectrum) if len(spectrum) > 0 else 0.1
        
        # Deslocamento ondulatorio suave (escoamento laminar)
        wave_amplitude = 3 + frequency_wave * 8
        laminar_x_offset = math.sin(laminar_phase) * wave_amplitude
        laminar_y_offset = math.cos(laminar_phase * 1.3) * wave_amplitude * 0.7
        
        # Aplica ondulação laminar
        x += laminar_x_offset
        y += laminar_y_offset
        
        # Mantém na tela com margem
        x = max(50, min(SCREEN_WIDTH - 50, x))
        y = max(50, min(SCREEN_HEIGHT - 50, y))
        
        point = {
            'x': x, 'y': y,
            'angle': self.current_angle,
            'radius': final_radius,
            'energy': energy,
            'hue': hue,
            'age': 0.0,
            'life': 1.0,
            'is_fibonacci': len(self.spiral_points) in [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89],
            'laminar_phase': laminar_phase,
            'frequency_influence': frequency_wave
        }
        
        self.spiral_points.append(point)
        
        # Envelhece pontos existentes
        for point in self.spiral_points:
            point['age'] += dt
            point['life'] = max(0, 1 - point['age'] / 10.0)  # 10 segundos de vida
    
    def update_fibonacci_constellation(self, dt):
        """Atualiza constelação baseada em Fibonacci"""
        fibonacci_positions = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        
        for fib_num in fibonacci_positions[:6]:  # Primeiros 6
            if fib_num <= len(self.spiral_points):
                spiral_point = self.spiral_points[fib_num - 1]
                if spiral_point['life'] > 0.5:
                    
                    # Cria partícula especial
                    if len(self.fibonacci_points) < 15:
                        fib_particle = {
                            'x': spiral_point['x'],
                            'y': spiral_point['y'],
                            'fibonacci_index': fib_num,
                            'pulse_phase': 0.0,
                            'life': 3.0
                        }
                        self.fibonacci_points.append(fib_particle)
        
        # Atualiza partículas Fibonacci existentes
        for particle in self.fibonacci_points[:]:
            particle['pulse_phase'] += dt * 1.5
            particle['life'] -= dt / 3
            
            if particle['life'] <= 0:
                self.fibonacci_points.remove(particle)
    
    def update_harmonic_particles(self, spectrum, dt, band_center_freqs=None):
        """Partículas que orbitam representando harmonias"""
        # Limita número de partículas
        self.harmonic_particles = [p for p in self.harmonic_particles if p['life'] > 0]
        
        # Cria novas partículas baseadas no espectro
        if len(spectrum) > 0 and len(self.harmonic_particles) < 24:
            for i in range(0, min(len(spectrum), 12), 2):
                energy = spectrum[i]
                if energy > 0.08:
                    # Calcula frequência central segura
                    center_freq = i / 12.0 if band_center_freqs is None or i >= len(band_center_freqs) else band_center_freqs[i]
                    
                    particle = {
                        'orbit_angle': i * (2 * math.pi / 12),
                        'orbit_radius': 50 + energy * 60,
                        'rotation_speed': 0.3 + energy * 0.7,
                        'energy': energy,
                        'life': 2.0,
                        'center_freq': center_freq,
                        'hue': i / 12.0
                    }
                    self.harmonic_particles.append(particle)
        
        # Atualiza partículas existentes
        for particle in self.harmonic_particles:
            particle['orbit_angle'] += particle['rotation_speed'] * dt
            particle['life'] -= dt / 2
            
            # Posição orbital
            particle['x'] = self.center_x + particle['orbit_radius'] * math.cos(particle['orbit_angle'])
            particle['y'] = self.center_y + particle['orbit_radius'] * math.sin(particle['orbit_angle'])
    
    def create_energy_resonance(self, energy, serenity):
        """Cria ressonância visual da energia"""
        resonance = {
            'radius': 3,
            'max_radius': 20 + energy * 35,
            'intensity': energy,
            'serenity': serenity,
            'life': 1.0
        }
        self.beat_resonance_rings.append(resonance)
    
    def update_energy_resonances(self, dt):
        """Atualiza anéis de ressonância"""
        for ring in self.beat_resonance_rings[:]:
            ring['radius'] += ring['max_radius'] * dt * 1.2
            ring['life'] -= dt * 1.2
            
            if ring['life'] <= 0:
                self.beat_resonance_rings.remove(ring)
    
    def update_sacred_geometry(self, spectrum, serenity, dt):
        """Geometria sagrada matemática"""
        # Cria formas geométricas baseadas no espectro
        if len(spectrum) > 6 and np.mean(spectrum) > 0.1:
            if len(self.sacred_geometry) < 8:
                # Número de lados baseado na música
                sides = 3 + int(np.argmax(spectrum[:6]))  # 3-8 lados
                
                geometry = {
                    'sides': sides,
                    'radius': 30 + np.mean(spectrum) * 50,
                    'rotation': 0.0,
                    'spin_speed': serenity * 0.5,
                    'life': 4.0,
                    'hue': np.argmax(spectrum) / len(spectrum)
                }
                self.sacred_geometry.append(geometry)
        
        # Atualiza geometrias existentes
        for geom in self.sacred_geometry[:]:
            geom['rotation'] += geom['spin_speed'] * dt
            geom['life'] -= dt / 4
            
            if geom['life'] <= 0:
                self.sacred_geometry.remove(geom)
    
    def process_instrument_events(self, instruments, dt):
        """Processa eventos de instrumentos específicos"""
        drums = instruments.get('drums', {})
        melodic = instruments.get('melodic', {})
        
        # Cria explosões para eventos de bateria
        if drums.get('kick', 0) > 0.3:
            # Explosão de kick no centro-baixo
            explosion_x = self.center_x + np.random.randint(-50, 51)
            explosion_y = self.center_y + 40 + np.random.randint(-20, 21)
            self.drum_explosions.create_explosion(explosion_x, explosion_y, drums['kick'], 'kick')
            
        if drums.get('snare', 0) > 0.25:
            # Explosão de snare no centro-alto
            explosion_x = self.center_x + np.random.randint(-60, 61)
            explosion_y = self.center_y - 30 + np.random.randint(-25, 26)
            self.drum_explosions.create_explosion(explosion_x, explosion_y, drums['snare'], 'snare')
            
        if drums.get('crash', 0) > 0.4:
            # Explosão de crash nas bordas
            explosion_x = self.center_x + np.random.randint(-100, 101)
            explosion_y = self.center_y + np.random.randint(-80, 81)
            self.drum_explosions.create_explosion(explosion_x, explosion_y, drums['crash'], 'crash')
            
        if drums.get('hihat', 0) > 0.2:
            # Mini explosões de hi-hat
            explosion_x = self.center_x + np.random.randint(-40, 41)
            explosion_y = self.center_y + np.random.randint(-40, 41)
            self.drum_explosions.create_explosion(explosion_x, explosion_y, drums['hihat'] * 0.7, 'hihat')
        
        # Cria corpos celestes para instrumentos melódicos
        if melodic.get('piano', 0) > 0.2:
            # Corpo celeste de piano
            body_x = self.center_x + np.random.randint(-80, 81)
            body_y = self.center_y + np.random.randint(-60, 61)
            self.celestial_bodies.create_celestial_body(body_x, body_y, melodic['piano'], 'piano')
            
        if melodic.get('strings', 0) > 0.25:
            # Corpo celeste de strings
            body_x = self.center_x + np.random.randint(-70, 71)
            body_y = self.center_y + np.random.randint(-50, 51)
            self.celestial_bodies.create_celestial_body(body_x, body_y, melodic['strings'], 'strings')
            
        if melodic.get('harmony', 0) > 0.3:
            # Corpo celeste harmônico
            body_x = self.center_x + np.random.randint(-90, 91)
            body_y = self.center_y + np.random.randint(-70, 71)
            self.celestial_bodies.create_celestial_body(body_x, body_y, melodic['harmony'], 'harmony')
        
        # Atualiza sistemas
        self.drum_explosions.update(dt)
        self.celestial_bodies.update(dt)
            
    def process_musical_dna(self, musical_dna, visual_dna):
        """Processa DNA musical para criar identidade visual única por música"""
        if not musical_dna or not visual_dna:
            return
            
        # Aplica características tonais únicas
        if 'tonal_complexity' in musical_dna:
            complexity = musical_dna['tonal_complexity']
            self.dna_visual_elements['spiral_curvature_factor'] = 0.5 + complexity * 0.5
            
        if 'harmonic_richness' in musical_dna:
            richness = musical_dna['harmonic_richness']
            self.dna_visual_elements['particle_density_factor'] = 0.3 + richness * 0.7
            
        # Aplica características rítmicas
        if 'rhythmic_complexity' in musical_dna:
            rhythm = musical_dna['rhythmic_complexity']
            self.dna_visual_elements['spiral_speed_factor'] = 0.5 + rhythm * 1.0
            
        if 'beat_strength' in musical_dna:
            strength = musical_dna['beat_strength']
            self.dna_visual_elements['pulse_intensity'] = 0.2 + strength * 0.8
            
        # Aplica características melódicas
        if 'melodic_complexity' in musical_dna:
            melody = musical_dna['melodic_complexity']
            self.dna_visual_elements['color_variation_speed'] = 0.1 + melody * 0.4
            
        # Aplica características timbrais
        if 'spectral_centroid_mean' in musical_dna:
            centroid = musical_dna['spectral_centroid_mean'] / 8000.0  # Normalizar
            centroid = max(0, min(1, centroid))
            self.dna_visual_elements['brightness_factor'] = 0.3 + centroid * 0.7
            
        if 'spectral_rolloff_mean' in musical_dna:
            rolloff = musical_dna['spectral_rolloff_mean'] / 11000.0  # Normalizar
            rolloff = max(0, min(1, rolloff))
            self.dna_visual_elements['energy_spread_factor'] = 0.2 + rolloff * 0.8
            
        # Aplica características dinâmicas
        if 'rms_energy_mean' in musical_dna:
            energy = musical_dna['rms_energy_mean']
            self.dna_visual_elements['overall_intensity'] = 0.1 + energy * 0.9
            
        # Aplica mapeamento visual específico
        for visual_param, value in visual_dna.items():
            if visual_param in self.dna_visual_elements:
                # Mistura o valor do DNA com o valor existente
                current = self.dna_visual_elements[visual_param]
                self.dna_visual_elements[visual_param] = (current + value) * 0.5
    
    def draw(self, screen, spectrum):
        """Desenha identidade visual única da música incluindo instrumentos específicos"""
        
        # Desenha espiral winding principal
        self.draw_musical_spiral(screen)
        
        # Desenha constelação de Fibonacci
        self.draw_fibonacci_constellation(screen)
        
        # Desenha partículas harmônicas orbitais
        self.draw_harmonic_particles(screen)
        
        # Desenha ressonâncias de energia
        self.draw_energy_resonances(screen)
        
        # Desenha geometria sagrada
        self.draw_sacred_geometry(screen)
        
        # Mandala espectral matemática
        self.draw_spectral_mandala(screen, spectrum)
        
        # Sistemas de instrumentos específicos
        self.drum_explosions.draw(screen)
        self.celestial_bodies.draw(screen)
        
        # Assinatura visual da música
        self.draw_musical_signature(screen)
    
    def quadratic_bezier(self, p1, p2, p3, t):
        """Calcula ponto na curva de Bézier quadrática"""
        # Fórmula: B(t) = (1-t)²P1 + 2(1-t)tP2 + t²P3
        x = (1-t)**2 * p1[0] + 2*(1-t)*t * p2[0] + t**2 * p3[0]
        y = (1-t)**2 * p1[1] + 2*(1-t)*t * p2[1] + t**2 * p3[1]
        return (int(x), int(y))
    
    def draw_musical_spiral_dna(self, screen):
        """Desenha espiral winding com modificações baseadas no DNA musical único"""
        if len(self.spiral_points) < 3:
            return
            
        # Obtém fatores únicos do DNA musical
        curvature = self.dna_visual_elements.get('spiral_curvature_factor', 1.0)
        brightness = self.dna_visual_elements.get('brightness_factor', 0.5)
        intensity = self.dna_visual_elements.get('overall_intensity', 0.5)
        color_variation = self.dna_visual_elements.get('color_variation_speed', 0.25)
        
        # Calcula cor única baseada no DNA
        time_factor = pygame.time.get_ticks() * 0.001 * color_variation
        
        # Cor base única por música
        r = int(127 + 100 * math.sin(time_factor) * brightness)
        g = int(100 + 80 * math.cos(time_factor * 1.3) * brightness)  
        b = int(150 + 105 * math.sin(time_factor * 0.7) * brightness)
        
        # Aplica intensidade geral
        r = int(r * intensity)
        g = int(g * intensity)  
        b = int(b * intensity)
        
        current_time = time.time()
        
        # Desenha espiral com características únicas
        for i in range(len(self.spiral_points) - 2):
            p1 = self.spiral_points[i]
            p2 = self.spiral_points[i + 1]
            p3 = self.spiral_points[i + 2]
            
            # Modulação única da espessura baseada no DNA
            progress = i / len(self.spiral_points)
            thickness_mod = 1.0 + 0.5 * math.sin(progress * math.pi * curvature)
            thickness = max(1, int(3 * thickness_mod))
            
            # Cor com variação única por segmento baseada no DNA
            segment_r = max(0, min(255, int(r * (0.8 + 0.4 * math.sin(progress * 10 * curvature)))))
            segment_g = max(0, min(255, int(g * (0.9 + 0.2 * math.cos(progress * 8 * curvature)))))
            segment_b = max(0, min(255, int(b * (0.85 + 0.3 * math.sin(progress * 6 * curvature)))))
            
            # Interpolação suave para curvas fluidas (usando curva de Bézier quadrática)
            num_segments = 8
            for j in range(num_segments):
                t1 = j / num_segments
                t2 = (j + 1) / num_segments
                
                # Pontos da curva de Bézier
                point1 = self.quadratic_bezier(p1, p2, p3, t1)
                point2 = self.quadratic_bezier(p1, p2, p3, t2)
                
                # Desenha linha com características únicas
                pygame.draw.line(screen, (segment_r, segment_g, segment_b), 
                               point1, point2, thickness)
        
        # Desenha pontos de destaque únicos
        highlight_density = self.dna_visual_elements.get('particle_density_factor', 0.5)
        points_to_highlight = max(3, int(len(self.spiral_points) * highlight_density * 0.1))
        
        for i in range(0, len(self.spiral_points), max(1, len(self.spiral_points) // points_to_highlight)):
            pos = self.spiral_points[i]
            
            # Cor de destaque única
            highlight_r = min(255, r + 50)
            highlight_g = min(255, g + 30) 
            highlight_b = min(255, b + 40)
            
            # Tamanho único baseado no DNA
            size = max(2, int(4 * intensity))
            pygame.draw.circle(screen, (highlight_r, highlight_g, highlight_b), 
                             (int(pos[0]), int(pos[1])), size)
        
        # Adiciona efeito de brilho único nas extremidades
        if len(self.spiral_points) > 2:
            # Início da espiral
            start_glow = int(20 * intensity)
            pygame.draw.circle(screen, (r, g, b), 
                             (int(self.spiral_points[0][0]), int(self.spiral_points[0][1])), start_glow, 2)
            
            # Final da espiral
            end_glow = int(15 * intensity)
            pygame.draw.circle(screen, (min(255, r + 30), min(255, g + 20), min(255, b + 25)), 
                             (int(self.spiral_points[-1][0]), int(self.spiral_points[-1][1])), end_glow, 2)
    
    def draw_musical_spiral(self, screen):
        """Desenha curvas winding fluidas com escoamento laminar"""
        if len(self.spiral_points) < 3:
            return
        
        current_time = time.time()
        
        # Desenha segmentos com curvas fluidas e cores harmoniosas
        for i in range(len(self.spiral_points) - 2):
            p1 = self.spiral_points[i]
            p2 = self.spiral_points[i + 1]
            p3 = self.spiral_points[i + 2]
            
            if p1['life'] <= 0 or p2['life'] <= 0 or p3['life'] <= 0:
                continue
            
            # Múltiplos segmentos para curva suave (interpolação)
            curve_segments = 8
            for seg in range(curve_segments):
                t = seg / curve_segments
                t_next = (seg + 1) / curve_segments
                
                # Interpolação quadrática suave (Bézier simples)
                def bezier_point(t):
                    # Curva quadrática entre p1, p2, p3
                    inv_t = 1 - t
                    x = inv_t * inv_t * p1['x'] + 2 * inv_t * t * p2['x'] + t * t * p3['x']
                    y = inv_t * inv_t * p1['y'] + 2 * inv_t * t * p2['y'] + t * t * p3['y']
                    return x, y
                
                x1, y1 = bezier_point(t)
                x2, y2 = bezier_point(t_next)
                
                # Ondulação laminar adicional
                flow_phase = current_time * 0.5 + i * 0.1 + seg * 0.05
                flow_intensity = (p1['frequency_influence'] + p2['frequency_influence']) * 0.5
                
                laminar_offset = math.sin(flow_phase) * flow_intensity * 2
                y1 += laminar_offset
                y2 += laminar_offset * 0.8
                
                # Cores que fluem harmoniosamente
                segment_energy = (p1['energy'] + p2['energy']) * 0.5
                base_hue = (p1['hue'] + p2['hue']) * 0.5
                
                # Cor fluida harmoniosa
                flowing_color = DelicateColors.flowing_harmonic_color(
                    base_hue, 
                    current_time + i * 0.2, 
                    flow_intensity,
                    segment_energy
                )
                
                # Alpha que respira com a vida dos pontos
                alpha = (p1['life'] + p2['life']) * 0.4
                final_color = DelicateColors.safe_color(flowing_color, alpha)
                
                # Espessura que varia com energia e fluxo
                base_thickness = 1 + segment_energy * 2
                flow_thickness = 1 + math.sin(flow_phase * 2) * 0.3
                thickness = max(1, int(base_thickness * flow_thickness))
                
                # Valida posições
                x1 = max(0, min(SCREEN_WIDTH, int(x1)))
                y1 = max(0, min(SCREEN_HEIGHT, int(y1)))
                x2 = max(0, min(SCREEN_WIDTH, int(x2)))
                y2 = max(0, min(SCREEN_HEIGHT, int(y2)))
                
                # Desenha segmento fluido
                try:
                    pygame.draw.line(screen, final_color, (x1, y1), (x2, y2), thickness)
                except:
                    continue
        
        # Desenha pontos de conexão com gradientes laminares
        self.draw_laminar_connection_points(screen, current_time)
        
    def draw_laminar_connection_points(self, screen, current_time):
        """Desenha pontos de conexão com efeito laminar"""
        # Pontos especiais (Fibonacci) com gradiente laminar
        for i, point in enumerate(self.spiral_points):
            if point['life'] <= 0:
                continue
                
            if point['is_fibonacci']:  # Ponto especial Fibonacci
                # Tamanho que pulsa com escoamento
                flow_pulse = math.sin(current_time * 1.5 + i * 0.3) * 0.2 + 1
                base_size = 2 + point['energy'] * 4
                size = max(1, int(base_size * flow_pulse))
                
                # Posição validada
                x = max(0, min(SCREEN_WIDTH, int(point['x'])))
                y = max(0, min(SCREEN_HEIGHT, int(point['y'])))
                
                # Gradiente laminar em camadas
                for layer in range(3, 0, -1):
                    layer_size = size + layer * 2
                    layer_alpha = point['life'] * (0.3 - layer * 0.08)
                    
                    # Cor que flui com gradiente laminar
                    layer_hue = (point['hue'] + layer * 0.05 + current_time * 0.1) % 1.0
                    layer_color = DelicateColors.flowing_harmonic_color(
                        layer_hue,
                        current_time + i * 0.2,
                        point['frequency_influence'],
                        point['energy']
                    )
                    
                    final_color = DelicateColors.safe_color(layer_color, layer_alpha)
                    
                    try:
                        pygame.draw.circle(screen, final_color, (x, y), layer_size)
                    except:
                        continue
                
                # Núcleo dourado (proporção áurea)
                core_size = max(1, size // 2)
                golden_hue = 0.12  # Dourado
                core_color = DelicateColors.flowing_harmonic_color(
                    golden_hue,
                    current_time * 0.8,
                    point['frequency_influence'] * 1.5,
                    0.8
                )
                final_core = DelicateColors.safe_color(core_color, point['life'])
                
                try:
                    pygame.draw.circle(screen, final_core, (x, y), core_size)
                except:
                    continue
    
    def draw_fibonacci_constellation(self, screen):
        """Desenha constelação baseada em Fibonacci"""
        for particle in self.fibonacci_points:
            if particle['life'] <= 0:
                continue
                
            # Pulsação suave
            pulse = 0.5 + 0.5 * math.sin(particle['pulse_phase'])
            
            # Tamanho baseado no índice de Fibonacci
            base_size = 2 + math.log(particle['fibonacci_index'] + 1)
            size = max(1, int(base_size * (0.8 + pulse * 0.2)))
            
            # Cor dourada (proporção áurea)
            golden_hue = 0.12  # Dourado
            color = DelicateColors.soft_pastel(golden_hue, pulse * 0.7)
            alpha_color = DelicateColors.safe_color(color, particle['life'])
            
            # Valida posição
            x = max(0, min(SCREEN_WIDTH, int(particle['x'])))
            y = max(0, min(SCREEN_HEIGHT, int(particle['y'])))
            
            pygame.draw.circle(screen, alpha_color, (x, y), size)
    
    def draw_harmonic_particles(self, screen):
        """Partículas harmônicas com escoamento laminar"""
        current_time = time.time()
        
        for i, particle in enumerate(self.harmonic_particles):
            if particle['life'] <= 0:
                continue
            
            # Ondulação laminar na posição
            laminar_phase = current_time * 0.8 + i * 0.4
            flow_offset_x = math.sin(laminar_phase) * particle['energy'] * 3
            flow_offset_y = math.cos(laminar_phase * 1.2) * particle['energy'] * 2
            
            x = particle['x'] + flow_offset_x
            y = particle['y'] + flow_offset_y
                
            # Tamanho que pulsa com fluxo laminar
            flow_pulse = math.sin(laminar_phase * 1.5) * 0.3 + 1
            base_size = 2 + particle['energy'] * 4
            size = max(1, int(base_size * flow_pulse))
            
            # Cor harmoniosa fluente
            flowing_color = DelicateColors.flowing_harmonic_color(
                particle['hue'],
                current_time * 0.6 + i * 0.3,
                particle['energy'],
                particle['energy']
            )
            
            
            # Valida posição
            x = max(0, min(SCREEN_WIDTH, int(x)))
            y = max(0, min(SCREEN_HEIGHT, int(y)))

            # Cor baseada na FREQUÊNCIA REAL com mapeamento logarítmico
            # Usamos a nova função que adicionamos na classe DelicateColors
            hue = DelicateColors.frequency_to_hue_logarithmic(particle['center_freq'])
            
            color = DelicateColors.soft_pastel(hue, particle['energy'])
            alpha_color = DelicateColors.safe_color(color, particle['life'] * 0.8)
                
            try:
                pygame.draw.circle(screen, alpha_color, (x, y), size)
            except:
                continue
            
            # Trilha laminar conectando ao centro
            trail_segments = 5
            for seg in range(trail_segments):
                t = seg / trail_segments
                trail_x = x + (self.center_x - x) * t
                trail_y = y + (self.center_y - y) * t
                
                # Ondulação na trilha
                trail_flow = math.sin(laminar_phase + seg * 0.5) * particle['energy']
                trail_y += trail_flow
                
                trail_alpha = particle['life'] * (0.1 - seg * 0.015)
                trail_color = DelicateColors.safe_color(flowing_color, trail_alpha)
                
                trail_x = max(0, min(SCREEN_WIDTH, int(trail_x)))
                trail_y = max(0, min(SCREEN_HEIGHT, int(trail_y)))
                
                try:
                    pygame.draw.circle(screen, trail_color, (trail_x, trail_y), 1)
                except:
                    continue
    
    def draw_energy_resonances(self, screen):
        """Desenha anéis de ressonância da energia"""
        for ring in self.beat_resonance_rings:
            if ring['life'] <= 0:
                continue
                
            # Cor baseada na intensidade e serenidade
            intensity = ring['intensity']
            serenity = ring['serenity']
            
            if intensity > 0.6:
                hue = 0.0   # Vermelho suave para energia forte
            elif intensity > 0.3:
                hue = 0.08  # Laranja suave
            else:
                hue = 0.6   # Azul suave
            
            # Modifica cor baseada na serenidade
            hue = (hue + serenity * 0.3) % 1.0
            
            color = DelicateColors.soft_pastel(hue, intensity)
            alpha_color = DelicateColors.safe_color(color, ring['life'] * 0.6)
            
            radius = max(1, int(ring['radius']))
            if radius > 0:
                pygame.draw.circle(screen, alpha_color,
                                 (self.center_x, self.center_y), radius, 2)
    
    def draw_sacred_geometry(self, screen):
        """Desenha geometria sagrada matemática"""
        for geom in self.sacred_geometry:
            if geom['life'] <= 0:
                continue
                
            # Vértices do polígono
            vertices = []
            for i in range(geom['sides']):
                angle = geom['rotation'] + i * (2 * math.pi / geom['sides'])
                x = self.center_x + geom['radius'] * math.cos(angle)
                y = self.center_y + geom['radius'] * math.sin(angle)
                vertices.append((int(x), int(y)))
            
            # Cor baseada na harmonia
            color = DelicateColors.soft_pastel(geom['hue'], 0.7)
            alpha_color = DelicateColors.safe_color(color, geom['life'] * 0.4)
            
            # Desenha polígono
            if len(vertices) > 2:
                try:
                    pygame.draw.polygon(screen, alpha_color, vertices, 2)
                except:
                    pass  # Ignora se vertices inválidos
    
    def draw_spectral_mandala(self, screen, spectrum):
        """Mandala matemática baseada no espectro"""
        if len(spectrum) == 0:
            return
            
        num_petals = min(len(spectrum), 12)
        
        for i in range(num_petals):
            energy = spectrum[i] if i < len(spectrum) else 0
            
            if energy < 0.05:
                continue
            
            # Posição baseada na proporção áurea
            angle = i * (2 * math.pi / self.golden_ratio)
            distance = 70 + energy * 50
            
            x = self.center_x + distance * math.cos(angle)
            y = self.center_y + distance * math.sin(angle)
            
            # Cor mapeada à frequência
            hue = (i / num_petals + 0.2) % 1.0
            color = DelicateColors.soft_pastel(hue, energy)
            
            size = max(1, int(1 + energy * 6))
            x_pos = max(0, min(SCREEN_WIDTH, int(x)))
            y_pos = max(0, min(SCREEN_HEIGHT, int(y)))
            pygame.draw.circle(screen, color, (x_pos, y_pos), size)
    
    def draw_musical_signature(self, screen):
        """Desenha assinatura visual da música"""
        # Assinatura espectral como barras delicadas
        signature_x = 25
        signature_y = 50
        
        for i, freq_energy in enumerate(self.musical_dna['spectral_signature']):
            if freq_energy > 0.01:
                bar_height = max(1, int(freq_energy * 30))
                hue = i / 12.0
                color = DelicateColors.soft_pastel(hue, freq_energy)
                
                # Valida rectângulo
                rect_x = max(0, signature_x + i * 5)
                rect_y = max(0, signature_y - bar_height)
                rect_w = 3
                rect_h = bar_height
                
                if rect_x + rect_w < SCREEN_WIDTH and rect_y + rect_h < SCREEN_HEIGHT:
                    pygame.draw.rect(screen, color, (rect_x, rect_y, rect_w, rect_h))
        
        # Padrão rítmico como pontos
        rhythm_y = signature_y + 25
        for i, beat_val in enumerate(list(self.musical_dna['rhythm_pattern'])):
            if beat_val > 0.08:
                size = max(1, int(beat_val * 3))
                color = DelicateColors.soft_pastel(0.8, beat_val)  # Roxo suave
                
                # Valida posição
                x_pos = max(0, min(SCREEN_WIDTH, signature_x + i * 6))
                y_pos = max(0, min(SCREEN_HEIGHT, rhythm_y))
                
                pygame.draw.circle(screen, color, (x_pos, y_pos), size)

class FlowingPetals:
    """Pétalas flutuantes orgânicas"""
    
    def __init__(self):
        self.petals = []
        self.spawn_timer = 0
        
    def update(self, spectrum, gentle_energy, dt):
        """Atualiza pétalas com movimento orgânico"""
        self.spawn_timer += dt
        
        # Cria novas pétalas suavemente
        if self.spawn_timer > 2.0 + np.random.random() * 3.0:
            self.spawn_timer = 0
            
            # Cria pétala no topo da tela
            petal = {
                'x': np.random.random() * SCREEN_WIDTH,
                'y': -10,
                'vx': (np.random.random() - 0.5) * 20,
                'vy': 10 + np.random.random() * 20,
                'size': 3 + np.random.random() * 6,
                'hue': np.random.random(),
                'life': 1.0,
                'rotation': np.random.random() * 2 * math.pi,
                'spin': (np.random.random() - 0.5) * 0.5,
                'sway_phase': np.random.random() * 2 * math.pi,
                'sway_speed': 0.5 + np.random.random() * 1.0
            }
            self.petals.append(petal)
            
        # Atualiza pétalas existentes
        for petal in self.petals[:]:
            # Movimento suave com balanceio
            petal['sway_phase'] += petal['sway_speed'] * dt
            sway = math.sin(petal['sway_phase']) * 15
            
            petal['x'] += (petal['vx'] + sway) * dt
            petal['y'] += petal['vy'] * dt
            petal['rotation'] += petal['spin'] * dt
            
            # Responde suavemente ao espectro
            if len(spectrum) > 0:
                spectrum_influence = np.mean(spectrum) * 10
                petal['vx'] += (np.random.random() - 0.5) * spectrum_influence * dt
                
            # Envelhecimento suave
            petal['life'] -= dt * 0.1
            
            # Remove pétalas que saíram ou morreram
            if petal['y'] > SCREEN_HEIGHT + 50 or petal['life'] <= 0:
                self.petals.remove(petal)
                
        # Limita número de pétalas
        if len(self.petals) > 30:
            self.petals = self.petals[-30:]
            
    def draw(self, screen):
        """Desenha pétalas delicadas"""
        for petal in self.petals:
            if petal['life'] <= 0:
                continue
                
            # Cor suave com transparência
            alpha = petal['life']
            color = DelicateColors.soft_pastel(petal['hue'], alpha * 0.7)
            
            # Tamanho que muda suavemente
            size = max(1, int(petal['size'] * alpha))
            
            # Valida posição
            x_pos = max(0, min(SCREEN_WIDTH, int(petal['x'])))
            y_pos = max(0, min(SCREEN_HEIGHT, int(petal['y'])))
            
            if size > 0:
                # Desenha pétala como elipse rotacionada (simples)
                pygame.draw.circle(screen, color, (x_pos, y_pos), size)
                
                # Brilho no centro
                highlight = DelicateColors.soft_pastel(petal['hue'], alpha)
                highlight_size = max(1, size // 2)
                pygame.draw.circle(screen, highlight, (x_pos, y_pos), highlight_size)

class GentleWaves:
    """Ondas extremamente suaves e orgânicas"""
    
    def __init__(self, y_position):
        self.y_base = y_position
        self.phase = 0.0
        self.amplitude = 25
        
    def update(self, spectrum, flow_rhythm, dt):
        """Atualização orgânica das ondas"""
        self.phase = flow_rhythm
        
        # Amplitude varia suavemente com o áudio
        if len(spectrum) > 0:
            energy = np.mean(spectrum)
            target_amplitude = 15 + energy * 40
            self.amplitude = self.amplitude * 0.98 + target_amplitude * 0.02
            
    def draw(self, screen, spectrum):
        """Desenha ondas suaves como seda"""
        points = []
        
        # Gera pontos da onda
        for x in range(0, SCREEN_WIDTH + 10, 8):
            # Múltiplas ondas harmônicas suaves
            wave1 = math.sin(x * 0.005 + self.phase) * self.amplitude
            wave2 = math.sin(x * 0.008 + self.phase * 0.7) * self.amplitude * 0.5
            wave3 = math.sin(x * 0.003 + self.phase * 1.3) * self.amplitude * 0.3
            
            y = self.y_base + wave1 + wave2 + wave3
            points.append((x, int(y)))
            
        # Desenha onda com gradiente suave
        if len(points) > 1:
            for i in range(len(points) - 1):
                progress = i / len(points)
                
                # Cor que flui suavemente
                hue = (self.phase * 0.1 + progress * 0.3) % 1.0
                color = DelicateColors.soft_pastel(hue, 0.6)
                
                # Valida pontos
                p1 = points[i]
                p2 = points[i + 1]
                x1 = max(0, min(SCREEN_WIDTH, int(p1[0])))
                y1 = max(0, min(SCREEN_HEIGHT, int(p1[1])))
                x2 = max(0, min(SCREEN_WIDTH, int(p2[0])))
                y2 = max(0, min(SCREEN_HEIGHT, int(p2[1])))
                
                pygame.draw.line(screen, color, (x1, y1), (x2, y2), 2)

class DelicateVisualizer:
    """Visualizador delicado e orgânico"""
    
    def __init__(self, audio_file):
        try:
            print("🎮 Inicializando pygame...")
            pygame.init()
            
            print("📺 Criando tela...")
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("🌸 Visualizador Delicado - Espiral Winding")
            
            self.clock = pygame.time.Clock()
            self.running = True
            
            print("🎵 Inicializando analisador de áudio...")
            # Analisador gentil
            self.analyzer = GentleAudioAnalyzer(audio_file)
            
            print("🌀 Criando elementos visuais...")
            # Elementos visuais delicados
            center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
            
            self.musical_spiral = UniqueMusicalSpiral(center_x, center_y)
            self.flowing_petals = FlowingPetals()
            
            # Ondas suaves em camadas
            self.gentle_waves = [
                GentleWaves(SCREEN_HEIGHT * 0.3),
                GentleWaves(SCREEN_HEIGHT * 0.7)
            ]
            
            # Estado visual suave
            self.background_breathing = 0.0
            
            print("✅ Visualizador delicado carregado com sucesso!")
            print("💫 SPACE=pause, ESC=sair")
            print("🌊 Relaxe e deixe-se levar pela suavidade...")
            
            # Auto-start
            threading.Timer(1.5, self.analyzer.start_playbook_safe).start()
            
        except Exception as e:
            print(f"❌ Erro na inicialização: {e}")
            raise
        
    def update(self, dt):
        """Atualização orgânica e suave"""
        features = self.analyzer.analyze_gently()
        
        # Atualiza elementos com delicadeza e identidade musical única
        self.musical_spiral.update(
            features['spectrum'], 
            features['gentle_energy'], 
            features['serenity_level'], 
            dt,
            features.get('instruments'),
            features.get('musical_dna'),
            features.get('visual_dna')
        )
        self.flowing_petals.update(features['spectrum'], features['gentle_energy'], dt)
        
        for wave in self.gentle_waves:
            wave.update(features['spectrum'], features['flow_rhythm'], dt)
            
        # Respiração do fundo
        self.background_breathing = features['breath_cycle']
        
    def draw(self):
        """Desenha experiência delicada"""
        try:
            features = self.analyzer.analyze_gently()
        except Exception as e:
            print(f"⚠️ Erro na análise: {e}")
            features = self.analyzer.get_serene_state()
        
        # Fundo que respira suavemente
        breath_intensity = 0.5 + 0.3 * math.sin(self.background_breathing)
        base_color = DelicateColors.breathing_gradient(features['flow_rhythm'])
        
        # Gradiente suave de fundo
        for y in range(SCREEN_HEIGHT):
            progress = y / SCREEN_HEIGHT
            
            # Mistura cores suavemente
            r, g, b = base_color
            fade_factor = 0.7 + 0.3 * progress * breath_intensity
            
            final_color = (
                int(r * fade_factor * 0.3),
                int(g * fade_factor * 0.4),
                int(b * fade_factor * 0.5)
            )
            
            pygame.draw.line(self.screen, final_color, (0, y), (SCREEN_WIDTH, y))
            
        # Ondas suaves
        for wave in self.gentle_waves:
            wave.draw(self.screen, features['spectrum'])
            
        # Pétalas flutuantes
        self.flowing_petals.draw(self.screen)
        
        # Identidade musical única - espiral winding + elementos matemáticos
        try:
            self.musical_spiral.draw(self.screen, features['spectrum'])
        except Exception as e:
            print(f"⚠️ Erro no desenho da espiral: {e}")
            # Desenha algo simples como fallback
            pygame.draw.circle(self.screen, (100, 150, 200), 
                             (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), 50, 2)
        
        pygame.display.flip()
        
    def handle_events(self):
        """Eventos suaves"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                        
    def run(self):
        """Loop principal delicado"""
        print("🌸 Iniciando experiência delicada...")
        
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            self.handle_events()
            self.update(dt)
            self.draw()
            
        pygame.mixer.music.stop()
        pygame.quit()
        print("🙏 Experiência delicada concluída")

def main():
    print("🌸 VISUALIZADOR DELICADO - ESPIRAL WINDING")
    print("💫 Inicializando...")
    import os
    from tkinter import Tk, filedialog

    audio_file = None

    # Se um arquivo foi passado como argumento, usa ele
    if len(sys.argv) >= 2:
        audio_file = sys.argv[1]
    else:
        # tenta usar um padrão na pasta musics
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
                audio_file = default_audio
        else:
            # abre diálogo para escolher arquivo
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

    try:
        print(f"🎵 Carregando áudio: {audio_file}")

        # Testa dependências mínimas
        import pygame  # noqa: F401
        import numpy as np  # noqa: F401
        import wave  # noqa: F401
        print("✅ Dependências OK")

        # Testa se arquivo existe
        if not os.path.exists(audio_file):
            print(f"❌ Arquivo não encontrado: {audio_file}")
            input("Pressione Enter para sair...")
            return

        print("✅ Arquivo encontrado")
        print("🌸 Iniciando visualizador...")

        visualizer = DelicateVisualizer(audio_file)
        visualizer.run()

    except KeyboardInterrupt:
        print("🌸 Interrompido pelo usuário")
    except Exception as e:
        print(f"❌ ERRO DETALHADO:")
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensagem: {e}")
        import traceback
        print("Traceback:")
        traceback.print_exc()
        input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()
