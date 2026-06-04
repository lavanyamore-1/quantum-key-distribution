# Quantum Key Distribution Simulation

This project is a web-based simulation of Quantum Key Distribution (QKD) protocols, specifically BB84 and E91. It allows users to simulate the transmission of qubits between Alice and Bob, with the option to include an eavesdropper.

## Features

- Simulate the transmission of qubits using BB84 or E91 protocols.
- Option to enable or disable an eavesdropper.
- Randomize the eavesdropper's actions.
- Display results including sent and received bits, shared keys, and error rates.

## Prerequisites

- Python 3.6 or  higher
- Flask
- NumPy

## Installation and Running the Application


1. Navigate to the directory containing `run.py`:
   ```bash
   cd path/to/your/project
   ```
   
2. pip install -r requirements.txt


3. Run the application:
   ```bash
   python run.py
   ```
4. Open your web browser and go to `http://127.0.0.1:5000/` to access the simulation interface.



## Usage

- Enter the number of qubits to simulate.
- Select the desired protocol (BB84 or E91).
- Choose whether to enable the eavesdropper.
- Click "Run Simulation" to see the results.
