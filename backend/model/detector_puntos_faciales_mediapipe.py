import os
import mediapipe as mp

class detector_puntos_faciales:

    def __init__(self):
        #configuracion MEDIAPIPE
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        BaseOptions = mp.tasks.BaseOptions
        FaceLandmarker = mp.tasks.vision.FaceLandmarker
        FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        # Configura el detector de landmarks faciales:
        # - Usa el modelo .task que está en la misma carpeta
        # - Sin blendshapes ni matrices de transformación (no las necesitamos)
        # - Detecta hasta 2 caras (para detectar si hay más de una)
        # - Modo IMAGE: procesa cada frame de forma independiente
        opciones = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=os.path.join(BASE_DIR, 'face_landmarker.task')),
        output_face_blendshapes=False,
        output_facial_transformation_matrixes=False,
        num_faces=2,
        running_mode=VisionRunningMode.IMAGE
        )
        self.landmarker = FaceLandmarker.create_from_options(opciones)


    def detectar_puntos(self, rgb_frame):
        # Detecta landmarks faciales con MediaPipe
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        resultados = self.landmarker.detect(mp_image)
        num_caras = len(resultados.face_landmarks) if resultados.face_landmarks else 0
        return resultados, num_caras