import cv2
import threading
import time

# 一个简单的摄像头采集线程，维护最新一帧（用于 MJPEG）
class Camera:
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src)
        self.frame = None
        self.running = False
        self.lock = threading.Lock()

    def start(self):
        if self.running:
            return
        self.running = True
        threading.Thread(target=self._capture_loop, daemon=True).start()

    def _capture_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.1)
                continue
            # 可在此处加入姿态/情绪推理并保存元数据
            _, jpg = cv2.imencode('.jpg', frame)
            with self.lock:
                self.frame = jpg.tobytes()
            time.sleep(0.03)

    def read(self):
        with self.lock:
            return self.frame

    def stop(self):
        self.running = False
        try:
            self.cap.release()
        except Exception:
            pass

# 单例摄像头
camera = Camera(src=0)
camera.start()