import time
import threading
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
import uvicorn
from model.registro_video import registro_video
from model.validacion_ojos import validacion_ojos
from model.estado_sesion import estado_sesion
from model.procesador_frames_cv2 import procesador_frames
from model.detector_puntos_faciales_mediapipe import detector_puntos_faciales
from model.encoding_cara_face_recognition import encoding_cara
from model.consultas_bbdd import consultas_bbdd
from model.construir_json import construir_json


class controller:

    def __init__(self, app):
        self.app = app
        self.conn = consultas_bbdd()
        self.ec = encoding_cara()
        self.vo = validacion_ojos()
        self.password = ""
        self.registrar_rutas()

    #conecta el tipo de conexión con la función que se debe ejecutar con cada conexópn
    def registrar_rutas(self):
        self.app.post("/auth/start-login")(self.start_login)
        self.app.post("/auth/start_registro")(self.start_registro)
        self.app.websocket("/ws_login")(self.websocket_endpoint_login)
        self.app.websocket("/ws_registro")(self.websocket_endpoint_registro)
    
    #funcion de la priemra valiación. Usuario y contraseña
    def start_login(self, data: dict):
        usuario = data["usuario"]
        password = data["password"]
        return self.conn.verificar_usuario_password(usuario, password)
    
    def start_registro(self, data: dict):
        usuario = data["usuario"]
        password = data["password"]        
        resultado = self.conn.verificar_usuario_password( usuario, password)
        if resultado["ok"]:
            return {"ok":False, "msj":"Nombre de usuario no disponible"}
        self.password = password  
        return {"ok": True, "usuario": usuario}
            
    #funcion que crea un hilo para hacer peticion al bbdd sin parar el flujo principal
    def hilo_consulta_servidor(self, encoding, es, usuario):
        es.resultado_db = self.conn.buscar_usuario_asincrono(encoding, usuario)
        es.buscando_en_db = False
        es.db_ready = True

    #funcion donde se ejecuta la conexion websocket y los procesos para pasar segunda validación del usuario usuario 
    async def websocket_endpoint_login(self, websocket: WebSocket):
        await websocket.accept()
        usuario = websocket.query_params.get("usuario")
        es = estado_sesion()
        pf = procesador_frames()
        dpf = detector_puntos_faciales()
        rv = registro_video()
        
        #reseta los valores en cada conexión websocket
        self.vo.resetear()

        print("Cliente conectado")

        #constantes en la validacion
        PROCESAR_CADA_N_FRAMES = 3
        PARPADEOS_REQUERIDOS = 2
        MAX_ESPERA = 20
        TIEMPO_ESPERA = 10

        try:
            while True:
                data = await websocket.receive_text()
                
                # calcular los fps reales por segundo
                tiempo_transcurrido = time.time() - es.inicio
                if tiempo_transcurrido >= 1.0:
                    es.fps_real = es.contadorFrames / tiempo_transcurrido

                #pasamos la data (el frame sin procesar) a la clase procesar frame para pasarlo a rgb y
                #añadirle un overlay con datos en el video guardado (libreria cv2)
                frame, rgb_frame, h, w = pf.procesar_frame(data)
                es.contadorFrames += 1
                
                #le pasamos el frame en formato rgb a la clase detecgtar_puntos (mediapipe) para calcular los puntos_faciales
                #y el número de caras
                resultados, num_caras = dpf.detectar_puntos(rgb_frame)
                #inicamos la variables que vamos a utilizar para localizar la cara
                left, right, top, bottom = 0, 0, 0, 0
                #tiempo actual para calcular tiempos de espera
                tiempo_actual = time.time()

                #switch para controlar el flujo según el número de caras
                match num_caras:
                    case 0:
                        #si no encuentra cara en 5 segundos desde el inicio envia el último json y cierra conexión
                        if tiempo_actual - es.inicio >= 5:
                            es.desc = "Error: No se detectan caras"
                            await websocket.send_json(construir_json.construir_json(es, num_caras, PARPADEOS_REQUERIDOS))
                            break
                        else:
                            es.desc = "Buscando cara..."

                    case 1:
                        #si encuentra una solo cara creas coordenadas utilizando los resultados de la funcion detectar_puntos
                        puntos_cara = resultados.face_landmarks[0]
                        x_coords = [int(p.x * w) for p in puntos_cara]
                        y_coords = [int(p.y * h) for p in puntos_cara]
                        left, right = min(x_coords), max(x_coords)
                        top, bottom = min(y_coords), max(y_coords)

                        #busca al usuario cada tres frames, calculando el encoding de la cara 
                        #que ha encontrado con el encoding de la bbdd solo si buscando_en_db es false (si no está buscando ya)
                        #en un hilo diferente sin bloquear el flujo principal
                        if not es.usuario_encontrado and (es.contadorFrames % PROCESAR_CADA_N_FRAMES == 0):
                            encoding = self.ec.calcular_encoding(rgb_frame, top, right, bottom, left)
                            if not es.buscando_en_db:
                                es.buscando_en_db = True
                                hilo_db = threading.Thread(
                                    target=self.hilo_consulta_servidor,
                                    args=(encoding, es, usuario)
                                )
                                hilo_db.daemon = True
                                hilo_db.start()
                            
                            #valores por defectos
                            es.nombre = "Desconocido"
                            es.desc = "No se reconoce el usuario."
                            
                            #si la consulta ha acabado y ha encontrado resultado cambia valores para seguir con la validaciçon
                            if es.db_ready:
                                if es.resultado_db is not None:
                                    nombre_encontrado, _ = es.resultado_db
                                    es.nombre = nombre_encontrado
                                    es.desc = "Usuario reconocido. Verificando parpadeo..."
                                    es.usuario_encontrado = True
                                #si la consulta ha acabado pero no ha encontrado resultado vuelve a false para repetir en la siguiente
                                #iteracion del bucle
                                es.db_ready = False
                        if es.nombre == "Desconocido" and tiempo_actual - es.inicio >= TIEMPO_ESPERA/2:
                            break
                        #si se ha encontrado usuario pasamos valores a la clase validacion_ojos para validar números de parapadeo
                        #y extraemos la información que nos devuelve el metodo de esta clase
                        elif es.usuario_encontrado:
                            DESC, promedio_ear, total_parpadeos, usuario_validado = self.vo.procesar_ojos(
                                PARPADEOS_REQUERIDOS, puntos_cara, ancho_frame=w, alto_frame=h
                            )
                            #actualizamos valores después de recibir valores de procesar_ojos 
                            es.promedio_ear = promedio_ear
                            es.total_parpadeos = total_parpadeos
                            es.usuario_validado = usuario_validado

                            #si procesar_ojos de la clase validacon_ojos nos da usaurio_valido cambiamos valores del estado de la sesion
                            if usuario_validado:
                                es.desc = "Usuario validado. Acceso aceptado."
                                es.reconocido = True
                            
                            #si no pasa la validacion y excede el tiempo de espera *2 damos error por tiempo excedido y desconectamos
                            else:
                                es.desc = DESC
                                if tiempo_actual - es.inicio >= TIEMPO_ESPERA * 2:
                                    es.desc = "Error: Tiempo de espera excedido."
                                    await websocket.send_json(construir_json.construir_json(es, num_caras, PARPADEOS_REQUERIDOS))
                                    break

                    case _:
                        # mes de una cara(default)
                        if es.contadorFrames % PROCESAR_CADA_N_FRAMES == 0:
                            es.desc = "Error: Se encontró más de una cara"
                            await websocket.send_json(construir_json.construir_json(es, num_caras, PARPADEOS_REQUERIDOS))
                            break
                
                #si sale del switch reconocido, aumentamos el valor del contador de frames desde que se ha reconocido y validado
                if es.reconocido:
                    es.frames_tras_validacion += 1
                
                frame = pf.overlay(frame, es.usuario_encontrado, es.reconocido, es.total_parpadeos, es.nombre, es.fps_real, left, right, top, bottom, w)
                es.buffer.append(frame)
                
                #una vez se ha cumplido el tiempo establecido para mostrar que el usario se ha validado correctamente, salimos
                await websocket.send_json(construir_json.construir_json(es, num_caras, PARPADEOS_REQUERIDOS, left, top, right, bottom))
                if es.reconocido and es.frames_tras_validacion >= MAX_ESPERA:
                    fecha_bd, nombre_archivo = rv.crearVideoRegistro(es.buffer, es.nombre, es.fps_real)
                    if es.usuario_validado:
                        self.conn.registrar_video_login(es.nombre, fecha_bd, nombre_archivo)
                    break
        except Exception as e:
            print(f"Cliente desconectado: {e}")
    
    async def websocket_endpoint_registro(self, websocket: WebSocket):
        await websocket.accept()
        usuario = websocket.query_params.get("usuario")
        es = estado_sesion()
        pf = procesador_frames()
        dpf = detector_puntos_faciales()
        ec = encoding_cara()
        inicio_con_cara = None  
        try:
            while True:
                data = await websocket.receive_text()
                frame, rgb_frame, h, w = pf.procesar_frame(data)
                es.contadorFrames += 1
                resultados, num_caras = dpf.detectar_puntos(rgb_frame)
                left, right, top, bottom = 0, 0, 0, 0
                tiempo_actual = time.time()  #actualizar DESPUÉS de recibir el frame

                if num_caras == 1:
                    if inicio_con_cara is None:
                        inicio_con_cara = time.time()  #empezar a contar cuando aparece la cara

                    segundos_con_cara = tiempo_actual - inicio_con_cara
                    await websocket.send_json({"desc": f"Mire a la cámara para capturar lanmakrs. Capturando... {int(segundos_con_cara)}/5s"})

                    if segundos_con_cara >= 5:  # han pasado 5 segundos con cara detectada
                        puntos_cara = resultados.face_landmarks[0]

                        x_coords = [int(p.x * w) for p in puntos_cara]
                        y_coords = [int(p.y * h) for p in puntos_cara]
                        left, right = min(x_coords), max(x_coords)
                        top, bottom = min(y_coords), max(y_coords)
                        encoding = ec.calcular_encoding(rgb_frame, top, right, bottom, left)
                        resultado = self.conn.verificar_registro(usuario, self.password, encoding)
                        await websocket.send_json({"desc": "Registro completado"})
                        break

                else:
                    inicio_con_cara = None  #resetear si se pierde la cara
                    await websocket.send_json({"desc": "Coloca tu cara frente a la cámara"})

        except Exception as e:
            print(f"Error creando encoding: {e}")
                              
app = FastAPI()
wsc = controller(app)
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)