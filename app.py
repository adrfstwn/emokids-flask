from apps import create_app, socketio, db
from apps.models import PoseData
import logging
import logging.handlers
import os
import cv2
import base64
import time
import numpy as np
from ultralytics import YOLO
from flask import request, jsonify

app = create_app()
# Ensure the log directory exists
log_dir = "logs"
if not os.path.exists(log_dir):
    try:
        os.makedirs(log_dir)
    except OSError as e:
        print(f"Error creating log directory: {e}")
        raise

# Configure logging
log_file = os.path.join(log_dir, "error.log")
try:
    log_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10000, backupCount=1)
    log_handler.setLevel(logging.ERROR)
    log_formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    log_handler.setFormatter(log_formatter)
    app.logger.addHandler(log_handler)
    logging.basicConfig(level=logging.DEBUG)
except Exception as e:
    print(f"Error setting up logging: {e}")
    raise

model = YOLO("ekspresi_ncnn_model")

latest_frame_with_detection = None
latest_raw_frame = None

def process_image(image_data):
    global latest_frame_with_detection
    global latest_raw_frame

    try:
        # Decode the base64 image data
        image_data = base64.b64decode(image_data)
        np_arr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Save the raw frame
        _, buffer = cv2.imencode('.jpg', frame)
        latest_raw_frame = base64.b64encode(buffer).decode('utf-8')

        # Process detection
        frame_with_detection = frame.copy()
        results = model(frame_with_detection)
        for r in results:
            boxes = r.boxes
            for box in boxes:
                b = box.xyxy[0].cpu().numpy().astype(int)
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                label = f"{r.names[cls]} {conf:.2f}"
                cv2.rectangle(frame_with_detection, (b[0], b[1]), (b[2], b[3]), (0, 255, 0), 2)
                cv2.putText(frame_with_detection, label, (b[0], b[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                # Save to database
                with app.app_context():
                    data_pose = PoseData(
                        timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                        pose=r.names[cls],
                        confidence=conf
                    )
                    try:
                        db.session.add(data_pose)
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        logging.error(f"Database error: {str(e)}")

        # Save the frame with detection
        _, buffer = cv2.imencode('.jpg', frame_with_detection)
        latest_frame_with_detection = base64.b64encode(buffer).decode('utf-8')

    except Exception as e:
        logging.error(f"Error in process_image: {str(e)}")

@app.route('/process_image', methods=['POST'])
def process_image_route():
    data = request.json
    image_data = data['image'].split(',')[1]
    process_image(image_data)

    return jsonify({
        'detected_image': 'data:image/jpeg;base64,' + latest_frame_with_detection
    })

def send_frame():
    global latest_frame_with_detection
    global latest_raw_frame
    while True:
        if latest_raw_frame is not None:
            socketio.emit('raw_frame', {
                'raw_image': latest_raw_frame
            })
        if latest_frame_with_detection is not None:
            socketio.emit('new_frame', {
                'detected_image': latest_frame_with_detection
            })
        socketio.sleep(0.1)

if __name__ == '__main__':
    try:
        socketio.start_background_task(send_frame)
        socketio.run(app, debug=False)
    except Exception as e:
        logging.error(f"Error starting the application: {str(e)}")
