import os
from flask import Flask, send_from_directory, render_template_string

app = Flask(__name__)

CARPETA_VIDEOS = 'peliculas'
CARPETA_MINIATURAS = os.path.join(CARPETA_VIDEOS, 'miniaturas')

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>🎬 Mis Películas</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            font-family: 'Segoe UI', sans-serif;
            color: #fff;
        }
        h1 {
            text-align: center;
            margin-bottom: 20px;
            font-size: 2em;
        }
        #buscador {
            display: block;
            margin: 0 auto 30px auto;
            padding: 10px 20px;
            width: 80%;
            max-width: 400px;
            border-radius: 12px;
            border: none;
            background: rgba(255, 255, 255, 0.15);
            color: white;
            font-size: 1em;
        }
        #buscador::placeholder {
            color: #ccc;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 20px;
            padding: 0 10px;
            max-width: 900px;
            margin: 0 auto;
        }
        .card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            overflow: hidden;
            position: relative;
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
            backdrop-filter: blur(8px);
            cursor: pointer;
            transition: transform 0.2s ease;
        }
        .card:hover {
            transform: scale(1.03);
        }
        .card img {
            width: 100%;
            height: auto;
            display: block;
        }
        .card-title {
            padding: 10px;
            font-size: 1em;
            text-align: center;
        }
        .overlay {
            position: absolute;
            inset: 0;
            background: rgba(0,0,0,0.6);
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        .card:hover .overlay {
            opacity: 1;
        }
        .overlay button {
            padding: 10px 20px;
            border: none;
            background: #00ffcc;
            color: #000;
            border-radius: 20px;
            font-weight: bold;
            cursor: pointer;
        }
        @media (max-width: 600px) {
            .card-title {
                font-size: 0.9em;
            }
        }

        /* Modal video player */
        #modalPlayer {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.85);
            z-index: 9999;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        #modalPlayer.active {
            display: flex;
        }
        #modalContent {
            position: relative;
            max-width: 90vw;
            max-height: 80vh;
            width: 720px;
            background: rgba(255,255,255,0.1);
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.7);
            backdrop-filter: blur(12px);
            overflow: hidden;
        }
        #modalContent video {
            width: 100%;
            height: 100%;
            display: block;
            border-radius: 16px;
            background: black;
        }
        #closeBtn {
            position: absolute;
            top: 10px;
            right: 10px;
            background: #ff0044;
            border: none;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            font-weight: bold;
            color: white;
            cursor: pointer;
            font-size: 20px;
            line-height: 30px;
            text-align: center;
            z-index: 10000;
        }
    </style>
</head>
<body>
    <h1>🎬 Mis Películas</h1>
    <input type="text" id="buscador" placeholder="Buscar película...">
    <div class="grid" id="lista">
        {% for video in videos %}
        <div class="card" data-nombre="{{ video.nombre_normalizado }}">
            <img src="/miniaturas/{{ video.thumbnail }}" alt="Miniatura">
            <div class="card-title">{{ video.nombre_base }}</div>
            <div class="overlay">
                <button onclick="reproducir('{{ video.archivo }}')">▶ Ver</button>
            </div>
        </div>
        {% endfor %}
    </div>

    <!-- Modal reproductor -->
    <div id="modalPlayer">
        <div id="modalContent">
            <button id="closeBtn" onclick="cerrarPlayer()">×</button>
            <video id="video" controls autoplay>
                <source id="source" src="" type="video/mp4">
                Tu navegador no puede reproducir este video.
            </video>
        </div>
    </div>

    <script>
        function normalizar(texto) {
            return texto.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
        }

        const buscador = document.getElementById('buscador');
        buscador.addEventListener('input', () => {
            const filtro = normalizar(buscador.value);
            document.querySelectorAll('.card').forEach(card => {
                const nombre = normalizar(card.getAttribute('data-nombre'));
                card.style.display = nombre.includes(filtro) ? 'block' : 'none';
            });
        });

        const modal = document.getElementById("modalPlayer");
        const video = document.getElementById("video");
        const source = document.getElementById("source");

        function reproducir(nombre) {
            source.src = "/videos/" + nombre;
            video.load();
            modal.classList.add("active");
            video.focus();
        }

        function cerrarPlayer() {
            modal.classList.remove("active");
            video.pause();
            video.currentTime = 0;
            source.src = "";
            video.load();
        }

        // Cerrar modal si se hace click fuera del video
        modal.addEventListener('click', (e) => {
            if(e.target === modal) {
                cerrarPlayer();
            }
        });

        // También cerrar con ESC
        document.addEventListener('keydown', (e) => {
            if(e.key === "Escape" && modal.classList.contains("active")) {
                cerrarPlayer();
            }
        });
    </script>
</body>
</html>
'''

def normalizar(texto):
    import unicodedata
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()

@app.route('/')
def index():
    if not os.path.exists(CARPETA_VIDEOS):
        return f"La carpeta '{CARPETA_VIDEOS}' no existe.", 404

    archivos = sorted(os.listdir(CARPETA_VIDEOS))
    extensiones = ('.mp4', '.mkv', '.avi', '.mov')
    videos = []

    for archivo in archivos:
        if archivo.lower().endswith(extensiones):
            nombre_base = os.path.splitext(archivo)[0]
            nombre_normalizado = normalizar(nombre_base)
            thumb_ext = next(
                (ext for ext in ['.jpg', '.png', '.jpeg', '.webp'] 
                 if os.path.exists(os.path.join(CARPETA_MINIATURAS, nombre_base + ext))),
                None
            )
            thumbnail = nombre_base + thumb_ext if thumb_ext else 'default.jpg'
            videos.append({
                'archivo': archivo,
                'nombre_base': nombre_base,
                'nombre_normalizado': nombre_normalizado,
                'thumbnail': thumbnail
            })

    return render_template_string(HTML_TEMPLATE, videos=videos)

@app.route('/videos/<path:nombre>')
def video(nombre):
    return send_from_directory(CARPETA_VIDEOS, nombre)

@app.route('/miniaturas/<path:nombre>')
def miniatura(nombre):
    return send_from_directory(CARPETA_MINIATURAS, nombre)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
