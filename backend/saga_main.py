# saga_main.py
from flask import Flask, render_template, request, jsonify, redirect, url_for
from saga_aiml import init_kernel, handle_input
from Bio import SeqIO, pairwise2
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
aiml_kernel, last_topic = init_kernel()

@app.route("/")
def index():
    return jsonify({'message': "Saga backend is alive"})

@app.route("/api/ping", methods=["GET"])
def ping():
    return jsonify({"message": "pong"})

@app.route('/chat')
def chat():
    global last_topic
    user_input = request.args.get('msg')
    print("User input", user_input)

    bot_response, last_topic = handle_input(aiml_kernel, user_input, last_topic)
    print("Bot response", bot_response)

    return jsonify({'bot_response': bot_response})

@app.route('/upload-fasta', methods=['POST'])
def upload_fasta():
    file = request.files.get('fasta_file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    
    try: 
        # Save the uploaded file temporarily
        filepath = os.path.join("/tmp", file.filename)
        file.save(filepath)

        # Read sequences from the FASTA
        records = list(SeqIO.parse(filepath, "fasta"))
        if len(records) < 2:
            return jsonify({'error': 'Need at least two sequences for alignment'})
        
        # Align the first two sequences
        seq1 = str(records[0].seq)
        seq2 = str(records[1].seq)
        alignments = pairwise2.align.globalxx(seq1, seq2)
        result = pairwise2.format_alignment(*alignments[0])

        return jsonify({'alignment': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
