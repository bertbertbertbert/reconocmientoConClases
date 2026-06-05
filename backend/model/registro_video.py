import cv2
from datetime import datetime
import os

class registro_video:

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RUTA_VIDEOS = os.path.join(BASE_DIR, '..', '..', 'videos')
    
    
    def crearVideoRegistro(self, buffer, usuario, fps_real):
        try:
            os.makedirs(self.RUTA_VIDEOS, exist_ok=True)
            fecha = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
            fecha_bd = datetime.now()
            nombre_archivo = f"{usuario}_access_{fecha}.avi"
            ruta_archivo = f"{self.RUTA_VIDEOS}/{nombre_archivo}"
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            primer_frame = buffer[0]
            out = cv2.VideoWriter(ruta_archivo, fourcc, fps_real, (primer_frame.shape[1], primer_frame.shape[0]))
            for f in buffer:
                out.write(f)
            out.release()
            print(f"Video {nombre_archivo} generado correctamente.")
            return fecha_bd, ruta_archivo
        except Exception as e:
            print(f"Error en la creacion del video de validación: {e}")
            return None, None