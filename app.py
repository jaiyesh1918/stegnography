from flask import Flask, render_template, request, jsonify, send_file
import cv2
import numpy as np
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt():
    file = request.files['image']
    message = request.form['message']
    key = request.form['key']

    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
    d = {chr(i): i for i in range(255)}

    # Step 1: Store message length in the first pixel
    msg_len = len(message)
    img[0, 0] = (msg_len, 0, 0)  # Store length in (R, G, B)

    n, m, z = 1, 0, 0  # Start storing message after first pixel
    for char in message:
        img[n, m, z] = d[char]
        n, m = n + 1, m + 1
        z = (z + 1) % 3

    enc_path = 'static/encrypted_image.png'
    cv2.imwrite(enc_path, img)

    return send_file(enc_path, as_attachment=True)

@app.route('/decrypt', methods=['POST'])
def decrypt():
    file = request.files['image']
    key = request.form['key']

    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
    c = {i: chr(i) for i in range(255)}

    # Step 2: Read stored message length
    msg_len = img[0, 0][0]  # Extract length from first pixel

    message = ""
    n, m, z = 1, 0, 0  # Start reading message after first pixel
    for _ in range(msg_len):  # Read only required characters
        message += c[img[n, m, z]]
        n, m = n + 1, m + 1
        z = (z + 1) % 3

    return jsonify({"message": message})

if __name__ == '__main__':
    app.run(debug=True)
