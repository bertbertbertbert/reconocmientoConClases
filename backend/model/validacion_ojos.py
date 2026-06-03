import math
import statistics

class validacion_ojos:

    F_CONSECUTIVOS = 2
    FRAMES_CALIBRACION = 30
    FACTOR_UMBRAL = 0.70
    UMBRAL_MIN = 0.18
    UMBRAL_MAX = 0.38

    def __init__(self):
        self._ear_muestras = []
        self._umbral_ear = None
        self._ear_reposo = None
        self.contador_frames = 0
        self.contador_parpadeos = 0
        self.usuario_validado = False

    def esta_calibrado(self):
        return self._umbral_ear is not None

    def calcular_distancia_px(self, p1, p2, ancho, alto):
        x1, y1 = p1.x * ancho, p1.y * alto
        x2, y2 = p2.x * ancho, p2.y * alto
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def calcular_ear_ojo(self, puntos, indices, ancho, alto):
        v1 = self.calcular_distancia_px(puntos[indices[1]], puntos[indices[5]], ancho, alto)
        v2 = self.calcular_distancia_px(puntos[indices[2]], puntos[indices[4]], ancho, alto)
        h = self.calcular_distancia_px(puntos[indices[0]], puntos[indices[3]], ancho, alto)
        return (v1 + v2) / (2.0 * h)

    def procesar_ojos(self, PARPADEOS_REQUERIDOS, puntos_cara, ancho_frame, alto_frame):
        indices_ojo_izq = [33, 159, 158, 133, 144, 145]
        indices_ojo_der = [362, 386, 385, 263, 373, 374]

        ear_izq = self.calcular_ear_ojo(puntos_cara, indices_ojo_izq, ancho_frame, alto_frame)
        ear_der = self.calcular_ear_ojo(puntos_cara, indices_ojo_der, ancho_frame, alto_frame)
        promedio_ear = (ear_izq + ear_der) / 2.0

        if not self.esta_calibrado():
            self._ear_muestras.append(promedio_ear)
            if len(self._ear_muestras) >= self.FRAMES_CALIBRACION:
                self._ear_reposo = float(statistics.median(self._ear_muestras))
                self._umbral_ear = max(self.UMBRAL_MIN,
                                      min(self.UMBRAL_MAX, self._ear_reposo * self.FACTOR_UMBRAL))
                print(f"[Calibración] EAR reposo={self._ear_reposo:.3f} → umbral fijado en {self._umbral_ear:.3f}")
            return "Calibrando", promedio_ear, self.contador_parpadeos, self.usuario_validado

        DESC = "Validando. Por favor, cierre y abra los ojos."
        if promedio_ear < self._umbral_ear:
            self.contador_frames += 1
        else:
            if self.contador_frames >= self.F_CONSECUTIVOS:
                self.contador_parpadeos += 1
            self.contador_frames = 0

        self.usuario_validado = (self.contador_parpadeos >= PARPADEOS_REQUERIDOS)
        return DESC, promedio_ear, self.contador_parpadeos, self.usuario_validado

    def resetear(self):
        self._ear_muestras = []
        self._umbral_ear = None
        self._ear_reposo = None
        self.contador_frames = 0
        self.contador_parpadeos = 0
        self.usuario_validado = False