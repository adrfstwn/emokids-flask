from apps import create_app, socketio
import threading
import logging
import cv2
import base64
import time
from ultralytics import YOLO

app = create_app()
logging.basicConfig(level=logging.DEBUG)

# Inisialisasi kamera
camera = cv2.VideoCapture(0)  
if not camera.isOpened():
    logging.error("Error: Kamera tidak terbuka")
    exit()
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)
print(f"Lebar frame: {camera.get(cv2.CAP_PROP_FRAME_WIDTH)}")
print(f"Tinggi frame: {camera.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
print(f"FPS: {camera.get(cv2.CAP_PROP_FPS)}")

model = YOLO("ekspresi_ncnn_model")
latest_frame = None

def capture_and_detect():
    global latest_frame, camera
    consecutive_failures = 0
    max_failures = 10

    while True:
        try:
            success, frame = camera.read()
            if success:
                consecutive_failures = 0
                results = model(frame)
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        b = box.xyxy[0].cpu().numpy().astype(int)
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        label = f"{r.names[cls]} {conf:.2f}"
                        cv2.rectangle(frame, (b[0], b[1]), (b[2], b[3]), (0, 255, 0), 2)
                        cv2.putText(frame, label, (b[0], b[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                
                _, buffer = cv2.imencode('.jpg', frame)
                latest_frame = base64.b64encode(buffer).decode('utf-8')
            else:
                consecutive_failures += 1
                logging.warning(f"Gagal menangkap frame. Kegagalan berurutan: {consecutive_failures}")
                if consecutive_failures >= max_failures:
                    logging.error("Terlalu banyak kegagalan berurutan. Mencoba menginisialisasi ulang kamera.")
                    camera.release()
                    time.sleep(2)
                    camera = cv2.VideoCapture(0)
                    if not camera.isOpened():
                        logging.error("Gagal menginisialisasi ulang kamera. Keluar.")
                        break
                    consecutive_failures = 0
        except Exception as e:
            logging.error(f"Kesalahan dalam capture_and_detect: {str(e)}")
        time.sleep(0.1)

def send_frame():
    global latest_frame
    while True:
        if latest_frame is not None:
            socketio.emit('new_frame', {'image': latest_frame})
        socketio.sleep(0.1)

if __name__ == '__main__':
    try:
        threading.Thread(target=capture_and_detect, daemon=True).start()
        socketio.start_background_task(send_frame)
        socketio.run(app, debug=False)
    except Exception as e:
        logging.error(f"Kesalahan saat memulai aplikasi: {str(e)}")
    finally:
        camera.release()
