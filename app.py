from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime
import json

# Inicializar la aplicación Flask
app = Flask(__name__)
CORS(app)  # Permitir solicitudes desde el frontend

# Configuración
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB máximo
DATA_FILE = 'data.json'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Crear directorio de uploads si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Funciones auxiliares
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Datos por defecto
        return {
            "characters": [
                {
                    "id": 1,
                    "name": "El Director",
                    "description": "El misterioso líder del circo, siempre observando desde las sombras.",
                    "imageUrl": None
                },
                {
                    "id": 2,
                    "name": "La Adivina",
                    "description": "Ve el futuro en sus cartas, pero nunca revela su propio destino.",
                    "imageUrl": None
                },
                {
                    "id": 3,
                    "name": "El Hombre de Goma",
                    "description": "Puede contorsionarse de formas imposibles, pero a un precio terrible.",
                    "imageUrl": None
                },
                {
                    "id": 4,
                    "name": "La Tragafuegos",
                    "description": "Domina las llamas, pero lucha por controlar el fuego en su interior.",
                    "imageUrl": None
                },
                {
                    "id": 5,
                    "name": "El Forzudo",
                    "description": "Su fuerza es legendaria, pero cada demostración le cuesta parte de su humanidad.",
                    "imageUrl": None
                }
            ],
            "chapters": [
                {
                    "id": 1,
                    "title": "Capítulo 1: La Llegada",
                    "description": "El circo llega a un pueblo desprevenido, anunciándose con carteles que aparecen como por arte de magia.",
                    "panels": []
                },
                {
                    "id": 2,
                    "title": "Capítulo 2: La Primera Función",
                    "description": "",
                    "panels": []
                },
                {
                    "id": 3,
                    "title": "Capítulo 3: El Precio",
                    "description": "",
                    "panels": []
                }
            ],
            "fanarts": []
        }

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Rutas de la API
@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(load_data())

@app.route('/data', methods=['POST'])
def update_data():
    data = request.get_json()
    save_data(data)
    return jsonify({'message': 'Datos actualizados correctamente'})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Generar nombre único para el archivo
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
        filename = secure_filename(unique_filename)
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename,
            'url': f"/images/{filename}"
        }), 200
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/images/<filename>')
def get_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete-image/<filename>', methods=['DELETE'])
def delete_image(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({'message': 'File deleted successfully'}), 200
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/list-images')
def list_images():
    try:
        images = []
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if allowed_file(filename):
                images.append({
                    'filename': filename,
                    'url': f"/images/{filename}",
                    'upload_date': datetime.fromtimestamp(
                        os.path.getctime(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    ).strftime('%Y-%m-%d %H:%M:%S')
                })
        return jsonify({'images': images}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ruta principal - Servir el frontend
@app.route('/')
def serve_frontend():
    return render_template('index.html')

# Punto de entrada de la aplicación
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)