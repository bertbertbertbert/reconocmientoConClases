//loguin user y password
const loginForm = document.getElementById("loginForm");
const registroForm = document.getElementById("registroForm");
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const overlay = document.getElementById('overlay');
const mensaje = document.getElementById('mensaje');
const ctx = canvas.getContext('2d');
const ctxOverlay = overlay.getContext('2d');

loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const usuario = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    // 1. Llamada HTTP a FastAPI para iniciar sesión
    const response = await fetch("http://localhost:8000/auth/start-login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            usuario,
            password
        })
    });

    const data = await response.json();

    if (data.ok) {
        loginForm.style.display = 'none';
        registroForm.style.display = 'none';
        document.getElementById('biometria').style.display = 'block';

         loginBiometrica(data.usuario);
        // 2. Aquí pasas a fase biométrica
       
    } else {
        alert("Credenciales incorrectas");
    }
});

registroForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const usuario = document.getElementById("usernameRegistro").value;
    const password = document.getElementById("passwordRegistro").value;

    // 1. Llamada HTTP a FastAPI para iniciar sesión
    const response = await fetch("http://localhost:8000/auth/start_registro", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            usuario,
            password
        })
    });
  
    const data = await response.json();

    if (!data.ok) {
      alert(data.msj);

    } else {
        loginForm.style.display = 'none';
        registroForm.style.display = 'none';
        document.getElementById('biometria').style.display = 'block';
        registroBiometrica(usuario);
    }
});

const loginBiometrica = (usuario)=>{

// Conectar WebSocket
const ws = new WebSocket(`ws://localhost:8000/ws_login?usuario=${usuario}`); //websocket protocol que manté la conexió oberta 

//funcion de websocker que se ejecuta cuando se inicia conexion
ws.onopen = () => {
    mensaje.textContent = 'Conectado al servidor';
    console.log('WebSocket conectado');
};

//funcion de websocker que se ejecuta durante la conexion
ws.onmessage = (event) => {
     const data = JSON.parse(event.data);
     mensaje.textContent = data.desc;
     mostrarOverlayInfo(data) 
};

//funcion que se ejecuta al cerrar conexion
ws.onclose = () => {
  const stream = video.srcObject;
  if(stream){
    stream.getTracks().forEach(track => track.stop())
    video.srcObject = null;
  }
    ctxOverlay.clearRect(0, 0, overlay.width, overlay.height);
    mensaje.textContent = mensaje.textContent + ' Desconectado del servidor';
};

// Activar cámara
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
        enviarFrames();
    })
    .catch(err => {
        mensaje.textContent = 'Error al acceder a la cámara: ' + err;
    });

// Enviar frames al servidor
function enviarFrames() {
    setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
            ctx.drawImage(video, 0, 0, 640, 480);
            const base64 = canvas.toDataURL('image/jpeg', 0.7).split(',')[1];
            ws.send(base64);
        }
    }, 100); // cada 100ms = 10 frames por segundo
}

// construir recuadro y texto en la imagen
    function mostrarOverlayInfo(data) {
        // limpiar el canvas antes de dibujar
        ctxOverlay.clearRect(0, 0, overlay.width, overlay.height);
        console.log("bbox:", data.bbox, "num_caras:", data.num_caras, "estado", data.desc);

        if (data.num_caras === 1 && data.bbox) {
            const { left, top, right, bottom } = data.bbox;

            // color según estado
            let color = 'red';
            let font = '20px Arial'
            if (data.reconocido) color = 'green';
            else if (data.nombre !== 'Desconocido') color = 'yellow';

            //franja superior
            ctxOverlay.fillStyle = 'rgba(0, 0, 0, 0.7)';
            ctxOverlay.fillRect(0, 0, overlay.width, 80);

            //fps 
            ctxOverlay.fillStyle = 'white';
            ctxOverlay.font = font;
            ctxOverlay.fillText(`fps: ${data.fps}`, 500, 30);

            //estado
            ctxOverlay.fillStyle = 'white';
            ctxOverlay.font = font;
            ctxOverlay.fillText(`Estado: ${data.desc}`, 10, 30);

            // dibujar recuadro
            ctxOverlay.strokeStyle = color;
            ctxOverlay.lineWidth = 2;
            ctxOverlay.strokeRect(left, top, right - left, bottom - top);

            // nombre encima del recuadro
            ctxOverlay.fillStyle = color;
            ctxOverlay.font = font;
            ctxOverlay.fillText(data.nombre, left, top - 5);

            // mostrar nº de parpadeos
            ctxOverlay.fillStyle = 'black';
            ctxOverlay.font = font
             ctxOverlay.fillText(`parpadeos: ${data.total_parpadeos}/2`, 10, 300);

        }
   }

}

//funcion envia frames para registro de vectores faciales
const registroBiometrica = (usuario) =>{

    const ws = new WebSocket(`ws://localhost:8000/ws_registro?usuario=${usuario}`); //websocket protocol que manté la conexió oberta 

    //funcion de websocker que se ejecuta cuando se inicia conexion
    ws.onopen = () => {
        mensaje.textContent = 'Conectado al servidor';
        console.log('WebSocket conectado');
    };

    //funcion de websocker que se ejecuta durante la conexion
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("llega aqui");
        mensaje.textContent = data.desc;
       
    };

    ws.onclose = () => {
        const stream = video.srcObject;
        if(stream){
            stream.getTracks().forEach(track => track.stop())
            video.srcObject = null;
        }
    };

    navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
        enviarFrames();
    })
    .catch(err => {
        mensaje.textContent = 'Error al acceder a la cámara: ' + err;
    });

    // Enviar frames al servidor
    function enviarFrames() {
        setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ctx.drawImage(video, 0, 0, 640, 480);
                const base64 = canvas.toDataURL('image/jpeg', 0.7).split(',')[1];
                ws.send(base64);
            }
        }, 100); // cada 100ms = 10 frames por segundo
    }
}