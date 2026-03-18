import os
import uuid
import pika
import logging
import json
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
QUEUE_NAME = os.getenv('QUEUE_NAME', 'image_tasks')
UPLOAD_DIR = os.getenv('UPLOAD_DIR', './uploads')
RESULT_DIR = os.getenv('RESULT_DIR', './results')

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_to_rabbitmq(message):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
        )
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)

        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)  # persistent
        )
        connection.close()
        return True
    except Exception as e:
        logging.error(f"RabbitMQ error: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400

    file = request.files['file']
    operation = request.form.get('operation', 'blur')

    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'status': 'error', 'message': 'File type not allowed'}), 400

    filename = secure_filename(file.filename)
    task_id = str(uuid.uuid4())
    ext = filename.rsplit('.', 1)[1].lower()
    saved_filename = f"{task_id}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, saved_filename)
    file.save(filepath)

    task_data = {
        'task_id': task_id,
        'operation': operation,
        'filename': saved_filename,
        'original_name': filename
    }

    import json
    success = send_to_rabbitmq(json.dumps(task_data))

    if success:
        return jsonify({
            'status': 'success',
            'message': 'Task sent to queue',
            'task_id': task_id,
            'operation': operation
        }), 200
    else:
        return jsonify({'status': 'error', 'message': 'Failed to send to queue'}), 500

@app.route('/result/<task_id>', methods=['GET'])
def get_result(task_id):
    result_path = os.path.join(RESULT_DIR, f"{task_id}.json")
    image_path = os.path.join(RESULT_DIR, f"{task_id}.jpg")

    if os.path.exists(result_path) and os.path.exists(image_path):
        with open(result_path, 'r') as f:
            data = json.load(f)
        return jsonify({
            'status': 'ready',
            'result': data,
            'image_url': f'/results/{task_id}.jpg'
        })
    return jsonify({'status': 'pending'})

@app.route('/results/<filename>')
def serve_result(filename):
    from flask import send_from_directory
    return send_from_directory(RESULT_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)