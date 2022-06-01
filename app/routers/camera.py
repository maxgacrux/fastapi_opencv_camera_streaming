from fastapi import APIRouter
from fastapi.responses import StreamingResponse, HTMLResponse
from app.func.streaming_threading import BaseCamera
import cv2

camera = APIRouter()
frame_c = cv2.VideoCapture(0)


class Camera(BaseCamera):
    def __init__(self):
        super().__init__()

    @staticmethod
    def frames():
        frame = cv2.VideoCapture(0, cv2.CAP_V4L) #cv2.CAP_DSHOW)
        print(frame.isOpened(), "\n\n\n")
        if not frame.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            _, img = frame.read()
            yield cv2.imencode('.jpg', img)[1].tobytes()


def video_streaming_generator(camera_streaming):
    """Функция генератора потокового видео."""
    while True:
        frame = camera_streaming.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@camera.get('/video_feed', response_class=HTMLResponse)
async def video_feed():
    """Видео-стриминг"""
    return StreamingResponse(
        video_streaming_generator(Camera()), media_type='multipart/x-mixed-replace; boundary=frame'
    )
