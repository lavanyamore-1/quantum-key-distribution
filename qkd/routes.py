from flask import Blueprint, render_template, request, jsonify
import numpy as np
import random

main = Blueprint('main', __name__)

def generate_bits(n):
    return np.random.randint(0, 2, n)

def generate_bases(n):
    return np.random.randint(0, 3, n)  

def encode_qubits(bits, bases, protocol):
    qubits = []
    for bit, base in zip(bits, bases):
        if protocol == 'BB84':
            if base == 0:
                qubits.append('H' if bit == 0 else 'V')
            else:
                qubits.append('D' if bit == 0 else 'A')
        elif protocol == 'E91':
            qubits.append(bit)  
    return qubits

def measure_qubits(qubits, bases, protocol):
    measured_bits = []
    for qubit, base in zip(qubits, bases):
        if protocol == 'BB84':
            if (qubit == 'H' and base == 0) or (qubit == 'D' and base == 1):
                measured_bits.append(0)
            elif (qubit == 'V' and base == 0) or (qubit == 'A' and base == 1):
                measured_bits.append(1)
            else:
                measured_bits.append(random.choice([0, 1]))
        elif protocol == 'E91':
            measured_bits.append(qubit)  
    return measured_bits

def sift_key(sender_bits, sender_bases, receiver_bases):
    return [bit for bit, s_base, r_base in zip(sender_bits, sender_bases, receiver_bases) if s_base == r_base]

def bell_inequality_test(alice_bits, bob_bits):
    return np.random.choice([True, False], p=[0.85, 0.15]) 

def eavesdrop(alice_qubits):
    eve_bases = generate_bases(len(alice_qubits))
    eve_measured_bits = measure_qubits(alice_qubits, eve_bases, protocol='E91')  
    eve_qubits = encode_qubits(eve_measured_bits, eve_bases, 'E91')
    return eve_qubits, eve_measured_bits, eve_bases

def compute_qber(alice_key, bob_key):
    if len(alice_key) == 0:
        return None 
    errors = sum(1 for a, b in zip(alice_key, bob_key) if a != b)
    return round(errors / len(alice_key), 2)

def introduce_errors(bits, error_rate):
    return [bit if random.random() > error_rate else 1 - bit for bit in bits]

def format_bits(bits, row_length=58):
    return '\n'.join([''.join(map(str, bits[i:i+row_length])) for i in range(0, len(bits), row_length)])

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/simulate', methods=['POST'])
def simulate():
    text_message = request.json.get('message', '')
    n = len(text_message) * 8  
    protocol = request.json.get('protocol', 'BB84')
    randomize_eavesdropper = request.json.get('randomize_eavesdropper', False)
    eavesdropper = request.json.get('eavesdropper', False) if not randomize_eavesdropper else random.choice([True, False])
    
    alice_bits = generate_bits(n)
    alice_bases = generate_bases(n)
    bob_bases = generate_bases(n)
    alice_qubits = encode_qubits(alice_bits, alice_bases, protocol)
    alice_sent_bits = alice_bits.copy()
    
    if eavesdropper:
        alice_qubits, eve_measured_bits, eve_bases = eavesdrop(alice_qubits)
        eavesdropping_detected = True
        error_rate = round(random.uniform(0.25, 0.5), 2)
    else:
        eve_bases = None
        eavesdropping_detected = False
        error_rate = round(random.uniform(0.0, 0.24), 2)
    
    bob_bits = measure_qubits(alice_qubits, bob_bases, protocol)
    bob_sent_bits = bob_bits.copy()
    
    if protocol == 'E91' and request.json.get('randomize', False):
        eavesdropping_detected = not bell_inequality_test(alice_bits, bob_bits)
    
    shared_key = sift_key(alice_bits, alice_bases, bob_bases)
    alice_received_bits = sift_key(alice_sent_bits, alice_bases, bob_bases)
    bob_received_bits = sift_key(bob_sent_bits, alice_bases, bob_bases)
    
    if eavesdropper:
        bob_received_bits = introduce_errors(bob_received_bits, error_rate)
    
    qber = compute_qber(alice_received_bits, bob_received_bits)
    received_message = text_message if not eavesdropping_detected else "MALFORMED"
    
    result = {
        "protocol": protocol,
        "original_message": text_message,
        "received_message": received_message,
        "alice_sent_bits": format_bits(alice_sent_bits),
        "alice_received_bits": format_bits(alice_received_bits),
        "bob_sent_bits": format_bits(bob_sent_bits),
        "bob_received_bits": format_bits(bob_received_bits),
        "shared_key": format_bits(shared_key),
        "eavesdropping_detected": eavesdropper if not randomize_eavesdropper else eavesdropping_detected,
        "error_rate": error_rate,
        "qber": qber
    }
    return jsonify(result)
