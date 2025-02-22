from flask import Flask, request, jsonify, render_template, send_file
import sqlite3
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY, name TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Route to render homepage
@app.route('/')
def home():
    return render_template('index.html')

# Generate certificate function
def generate_certificate(name):
    template = Image.open("certificate_template.png")  # Ensure you have a template image
    draw = ImageDraw.Draw(template)
    font = ImageFont.truetype("arial.ttf", 50)
    draw.text((400, 300), name, (0, 0, 0), font=font)  # Adjust coordinates as needed
    
    output = io.BytesIO()
    template.save(output, format="PNG")
    output.seek(0)
    return output

# API to check and provide certificate
@app.route('/get_certificate', methods=['POST'])
def get_certificate():
    data = request.json
    name = data.get("name")
    
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("SELECT * FROM students WHERE name=?", (name,))
    student = c.fetchone()
    conn.close()
    
    if student:
        cert = generate_certificate(name)
        return send_file(cert, mimetype='image/png', as_attachment=True, download_name=f"{name}_certificate.png")
    else:
        return jsonify({"error": "Name not found in database."}), 404

if __name__ == '__main__':
    app.run(debug=True)