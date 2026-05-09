# prompt_lib.py
# СТАБИЛЬНАЯ ВЕРСИЯ (без эмуляции шума)

import math
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

STYLES = ["Steampunk", "Cyberpunk", "Biopunk", "Dieselpunk", "Surrealism", "Impressionism", "Art Nouveau", "Cubism", "Gothic", "Baroque", "Renaissance", "Abstract", "Minimalism", "Vaporwave", "Solarpunk", "Afrofuturism"]
OBJECTS = ["a floating crystal", "a clockwork whale", "a neon-lit samurai", "a glass forest", "a forgotten android", "a bio-luminescent mushroom", "a celestial kraken", "an arcane library", "a derelict starship", "a sentient storm", "a mechanical heart", "a robotic monk"]
SETTINGS = ["in a submerged city", "on a volcanic moon", "inside a Dyson sphere", "during a supernova", "in a zero-gravity chamber", "within a digital matrix", "in an alien jungle", "on a floating island", "in a gothic megastructure", "at the edge of a black hole", "in a retro-futuristic diner", "among ancient ruins"]
ARTISTS = ["in the style of H.R. Giger", "in the style of Zdzisław Beksiński", "in the style of Moebius", "in the style of Salvador Dalí", "in the style of Vincent van Gogh", "in the style of Syd Mead", "in the style of Hayao Miyazaki", "in the style of Greg Rutkowski", "in the style of Alphonse Mucha"]
EFFECTS = ["cinematic lighting", "god rays", "volumetric fog", "lens flare", "highly detailed", "sharp focus", "8k resolution", "unreal engine 5", "octane render", "vivid colors", "dramatic atmosphere", "eerie glow"]

def get_quantum_random_index(list_size: int) -> int:
    if list_size <= 0: return 0
    num_qubits = (list_size - 1).bit_length()
    if num_qubits <= 0: return 0

    qc = QuantumCircuit(num_qubits)
    qc.h(range(num_qubits))
    qc.measure_all()
    
    simulator = AerSimulator()
    transpiled_qc = transpile(qc, simulator)
    result = simulator.run(transpiled_qc, shots=1, memory=True).result()
    
    binary_outcome = result.get_memory()[0]
    decimal_outcome = int(binary_outcome, 2)
    
    return decimal_outcome % list_size

def generate_prompt() -> str:
    obj = OBJECTS[get_quantum_random_index(len(OBJECTS))]
    style = STYLES[get_quantum_random_index(len(STYLES))]
    setting = SETTINGS[get_quantum_random_index(len(SETTINGS))]
    artist = ARTISTS[get_quantum_random_index(len(ARTISTS))]
    effect1 = EFFECTS[get_quantum_random_index(len(EFFECTS))]
    
    remaining_effects = [e for e in EFFECTS if e != effect1]
    effect2 = remaining_effects[get_quantum_random_index(len(remaining_effects))]
    
    prompt = (
        f"{obj} {setting}, {artist}, {style}, "
        f"{effect1}, {effect2}, cinematic composition"
    )
    return prompt
