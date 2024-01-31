from flask import Flask, request, jsonify
import opennsfw2 as n2
import os
import random
import string
import logging

app = Flask(__name__)

# 配置日志
log_format = '[%(asctime)s] [%(levelname)s] - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format, handlers=[logging.StreamHandler()])

def generate_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def detect_nsfw_image(image_path):
    nsfw_probability = n2.predict_image(image_path)
    return nsfw_probability

def detect_nsfw_video(video_path):
    elapsed_seconds, nsfw_probabilities = n2.predict_video_frames(video_path)
    return elapsed_seconds, nsfw_probabilities

def save_file(file, file_type):
    random_string = generate_random_string(8)
    original_filename, file_extension = os.path.splitext(file.filename)
    new_filename = f'{random_string}-{original_filename}{file_extension}'
    file_path = os.path.join('/tmp', new_filename)
    file.save(file_path)
    return file_path, new_filename

def delete_file(file_path):
    try:
        os.remove(file_path)
        logging.info(f'Temporary file deleted: {file_path}')
    except Exception as e:
        logging.error(f'Error deleting temporary file {file_path}: {e}')

@app.route('/image', methods=['POST'])
def handle_image_request():
    try:
        if 'image' in request.files:
            image_file = request.files['image']
            image_path, image_filename = save_file(image_file, 'image')

            logging.info(f'Received image file: {image_filename}, Temporary file: {image_path}')
            
            nsfw_probability = detect_nsfw_image(image_path)
            logging.info(f'Temporary file: {image_path}, Image NSFW probability: {nsfw_probability}')

            delete_file(image_path)

            result = {
                'status': 'success',
                'message': 'Image uploaded successfully.',
                'nsfw_probability': nsfw_probability
            }

            return jsonify(result), 200
        else:
            result = {'status': 'error', 'message': 'Missing image file in the request.'}
            return jsonify(result), 400
    except Exception as e:
        logging.error(f'Error processing image request: {e}')
        result = {'status': 'error', 'message': 'Internal server error.'}
        return jsonify(result), 500

@app.route('/video', methods=['POST'])
def handle_video_request():
    try:
        if 'video' in request.files:
            video_file = request.files['video']
            video_path, video_filename = save_file(video_file, 'video')

            logging.info(f'Received video file: {video_filename}, Temporary file: {video_path}')
            
            elapsed_seconds, nsfw_probabilities = detect_nsfw_video(video_path)
            logging.info(f'Temporary file: {video_path}, Video NSFW probabilities: {nsfw_probabilities}')

            delete_file(video_path)

            result = {
                'status': 'success',
                'message': 'Video uploaded successfully.',
                'elapsed_seconds': elapsed_seconds,
                'nsfw_probabilities': nsfw_probabilities
            }

            return jsonify(result), 200
        else:
            result = {'status': 'error', 'message': 'Missing video file in the request.'}
            return jsonify(result), 400
    except Exception as e:
        logging.error(f'Error processing video request: {e}')
        result = {'status': 'error', 'message': 'Internal server error.'}
        return jsonify(result), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

