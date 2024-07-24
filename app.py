from apps import create_app, socketio, db
from apps.models import PoseData
import logging
import cv2
import base64
import time
import numpy as np
from ultralytics import YOLO
from flask import request, jsonify

app = create_app()
logging.basicConfig(level=logging.DEBUG)

model = YOLO("ekspresi_ncnn_model")

latest_frame_with_detection = None

def process_image(image_data):
    global latest_frame_with_detection

    try:
        # Decode the base64 image data
        image_data = base64.b64decode(image_data)
        np_arr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

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
    while True:
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
