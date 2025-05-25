# Enigma Machine

A Python-based simulation of the historic Enigma cipher machine, featuring configurable rotors, plugboard, and seed-based reproducible encryption/decryption. Inspired by the WWII-era Enigma, this project allows you to explore classical rotor-based cryptography and see how a simple seed can generate consistent configurations.

[View on GitHub](https://github.com/dev-760/Enigma-Machine)

---

## Features

* **Rotor Configuration**: Three rotors (I, II, III) with standard wiring.
* **Reflector**: Simplified reflector for bidirectional signal flow.
* **Seed-Based Initialization**: Uses SHA-256 hashing of a user-provided seed to generate consistent rotor positions and plugboard settings.
* **Plugboard**: Up to 6 randomized letter-pair swaps per seed.
* **Rotor Stepping**: Simulates notch turnover: right rotor steps each letter, middle and left step on full rotations.
* **Encryption & Decryption**: Same process for both—feeding ciphertext back through the machine yields the original message if seed and settings match.
* **Animated CLI**: Visual rotor stepping animation in the terminal.
* **Settings Menu**: Configure seed, view current configuration, and reset to defaults.

---

## Technical Specifications

### Architecture

```text
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Plugboard     │ -> │ Rotor System │ -> │   Reflector     │
│   (6 pairs)     │    │ (3 rotors)   │    │   (26 wires)    │
└─────────────────┘    └──────────────┘    └─────────────────┘
```

### Rotor Specifications

| Component | Configuration              | Specification    |
| --------- | -------------------------- | ---------------- |
| Rotor I   | EKMFLGDQVZNTOWYHXUSPAIBRCJ | Right-most rotor |
| Rotor II  | AJDKSIRUXBLHWTMCQGZNPYFVOE | Middle rotor     |
| Rotor III | BDFHJLCPRTXVZNYEIWGAKMUSQO | Left-most rotor  |
| Reflector | YRUHQSLDPXNGOKMIEBFZCWVJAT | Type B Reflector |

### Cryptographic Parameters

* **Key Space**: 26³ rotor positions × 2⁶ plugboard configurations
* **Stepping Mechanism**: Odometer-style advancement with double-stepping
* **Character Set**: A–Z (26 letters), preserves non-alphabetic characters
* **Reciprocal Property**: Encryption and decryption use identical operations

---

## Getting Started

### Prerequisites

* Python 3.7 or higher

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/dev-760/Enigma-Machine.git
   cd Enigma-Machine
   ```

2. (Optional) Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\\Scripts\\activate
   ```

3. Install dependencies (none beyond the stdlib):

   ```bash
   pip install -r requirements.txt  # currently empty
   ```

## Usage

Run the main script:

```bash
python enigma_machine.py
```

### Menu Options

1. **Encrypt**: Encrypt a plaintext message. Requires a seed to be set.
2. **Decrypt**: Decrypt a ciphertext message. Uses the same process as encryption.
3. **Settings**:

   * **Enter Seed**: Input a secret seed (text) shared by sender and receiver.
   * **View Current Configuration**: Display seed, rotor positions, and plugboard mappings.
   * **Reset to Default**: Clear seed and reset machine.
4. **Exit**: Quit the program.

### Example

```text
=== ENIGMA MACHINE V0.1 ===
Current Seed: SECRET123
Rotor Positions: K Q M
Plugboard: 6 pairs configured

1. Encrypt
2. Decrypt
3. Settings
4. Exit
```

## How It Works

1. **Seed Hashing**: The input seed is hashed via SHA-256 to produce a 32-bit integer.
2. **Rotor & Plugboard Setup**: Using the seeded random generator, three rotor positions (A–Z) and six plugboard pairs are chosen.
3. **Encoding**:

   * Advance rotors according to stepping rules.
   * Apply plugboard swap.
   * Pass signal through Rotors III → II → I.
   * Reflect using reflector wiring.
   * Pass signal back through Rotors I → II → III in reverse.
   * Apply plugboard again.
4. **Repeat** for each character; only alphabetic characters are transformed.


## Acknowledgments

* Inspired by the historic Enigma machine.
* Uses Python's standard library and `hashlib` for stable seeding.
