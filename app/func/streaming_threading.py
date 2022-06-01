import time
import threading
try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from thread import get_ident
    except ImportError:
        from _thread import get_ident


class CameraEvent(object):
    """Класс событий, который генерит новый кадр для клиента"""
    def __init__(self):
        self.events = {}

    def wait(self):
        """Ожидание следующего кадра"""
        ident = get_ident()
        if ident not in self.events:
            # это новый клиент
            # добавить запись для него в словарь self.events
            # каждая запись имеет два элемента: threading.Event() и метку времени
            self.events[ident] = [threading.Event(), time.time()]
        return self.events[ident][0].wait()

    def set(self):
        """Вызывается потоком камеры, когда доступен новый кадр."""
        now = time.time()
        remove = []
        for ident, event in self.events.items():
            if not event[0].isSet():
                # если это клиентское событие не установлено, то установивем его
                # также обновляем последнюю установленную временную метку до текущего момента
                event[0].set()
                event[1] = now
            else:
                # если событие клиента уже установлено, значит клиент
                # не обработал предыдущий кадр
                # если событие длится более 5 секунд, то предположим
                # клиент ушел и удалим его
                if now - event[1] > 5:
                    remove.append(ident)

        for ident in remove:
            del self.events[ident]

    def clear(self):
        """Вызывается из потока каждого клиента после обработки кадра."""
        self.events[get_ident()][0].clear()


class BaseCamera(object):
    thread = None  # фоновый поток, считывающий кадры с камеры
    frame = None  # текущий кадр хранится здесь фоновым потоком
    last_access = 0  # время последнего доступа клиента к камере
    event = CameraEvent()

    def __init__(self):
        """Запустите поток фоновой камеры, если он еще не запущен."""
        if BaseCamera.thread is None:
            BaseCamera.last_access = time.time()

            # начать поток фонового кадра
            BaseCamera.thread = threading.Thread(target=self._thread)
            BaseCamera.thread.start()

            # ждем пока кадры будут доступны
            while self.get_frame() is None:
                time.sleep(0)

    def get_frame(self):
        """Вернуть текущий кадр камеры."""
        BaseCamera.last_access = time.time()

        # ждем сигнала от потока камеры
        BaseCamera.event.wait()
        BaseCamera.event.clear()

        return BaseCamera.frame

    @staticmethod
    def frames():
        """"Генератор, возвращающий кадры с камеры."""
        raise RuntimeError('Must be implemented by subclasses.')

    @classmethod
    def _thread(cls):
        """Поток камеры."""
        print('[INFO] Starting camera thread.')
        frames_iterator = cls.frames()
        for frame in frames_iterator:
            BaseCamera.frame = frame
            BaseCamera.event.set()  # отправляем сигнал клиентам
            time.sleep(0)

            # если не было ни одного клиента, запрашивающего фреймы в
            # последние 10 секунд, то дропаем поток
            if time.time() - BaseCamera.last_access > 10:
                frames_iterator.close()
                print('[INFO] Stopping camera thread due to inactivity.')
                break
        BaseCamera.thread = None