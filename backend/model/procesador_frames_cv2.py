import cv2
import base64
import numpy as np

class procesador_frames:

    def procesar_frame(self, data):
        img_bytes = base64.b64decode(data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if frame is None:
           return None  # Frame corrupto, devuelve None
        # Convierte a RGB (MediaPipe trabaja en RGB, OpenCV en BGR)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = frame.shape   
        return frame, rgb_frame, h, w
    
    def overlay(self, frame, usuario_encontrado, reconocido, total_parpadeos, nombre, fps_real, left, right, top, bottom, w):
        color = (0, 255, 0) if reconocido else (0, 255, 255) if usuario_encontrado else (0, 0, 255)

        # Recuadro alrededor de la cara
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

        # Nombre encima del recuadro
        cv2.putText(frame, nombre, (left, top - 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # fps
        cv2.putText(frame, 'fps: ' + str(fps_real), (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        # Parpadeos 
        texto_fps = 'parpadeos ' + str(total_parpadeos) + '/2'
        (ancho_texto, _), _ = cv2.getTextSize(texto_fps, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.putText(frame, texto_fps, (w - ancho_texto - 10, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        return frame