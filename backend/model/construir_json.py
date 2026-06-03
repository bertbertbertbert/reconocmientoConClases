class construir_json:

    @staticmethod
    def construir_json(es, num_caras, PARPADEOS_REQUERIDOS, left=0, top=0, right=0, bottom=0):
        return {
            "num_caras": num_caras,
            "nombre": es.nombre,
            "desc": es.desc,
            "total_parpadeos": es.total_parpadeos,
            "parpadeos_requeridos": PARPADEOS_REQUERIDOS,
            "promedio_ear": es.promedio_ear,
            "fps": es.fps_real,
            "reconocido": es.reconocido,
            "bbox": {"left": left, "top": top, "right": right, "bottom": bottom}
        }
    

