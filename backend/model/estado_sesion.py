from collections import deque
import time

class estado_sesion:

    def __init__(self):
        self.buscando_en_db = False
        self.db_ready = False
        self.resultado_db = None
        self.fps_real = 30
        self.contadorFrames = 0
        self.inicio = time.time()
        self.buffer = deque(maxlen=150)
        self.total_parpadeos = 0
        self.promedio_ear = 0
        self.usuario_valido = False
        self.usuario_encontrado = False
        self.nombre = "Desconocido"
        self.desc = "Buscando cara en imagen..."
        self.reconocido = False
        self.frames_tras_validacion = 0

