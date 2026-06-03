import face_recognition

class encoding_cara:

    def calcular_encoding(self, rgb_frame, top, right, bottom, left):
        locaciones_caras = [(top, right, bottom, left)]
        encodings_caras = face_recognition.face_encodings(rgb_frame, locaciones_caras)

        if len(encodings_caras) > 0:
            return encodings_caras[0]
        return None