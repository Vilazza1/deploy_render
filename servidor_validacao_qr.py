from flask import Flask
from urllib.parse import unquote
import os
import json

app = Flask(__name__)
ARQUIVO_USADOS = "usados.json"

# Cria o arquivo JSON se não existir
if not os.path.exists(ARQUIVO_USADOS):
    with open(ARQUIVO_USADOS, "w") as f:
        json.dump([], f)

@app.route("/")
def home():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Scanner QR Code</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f7f7f7;
                text-align: center;
                padding: 20px;
                margin: 0;
            }
            #reader {
                width: 100%;
                max-width: 400px;
                margin: 20px auto;
            }
            button {
                font-size: 18px;
                padding: 12px 24px;
                margin-top: 30px;
                cursor: pointer;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 8px;
            }
            .box {
                margin: 20px auto;
                max-width: 90%;
                font-size: 20px;
                color: #333;
            }
            a.usados-link {
                display: inline-block;
                margin-top: 20px;
                font-size: 18px;
                color: #007bff;
                text-decoration: none;
            }
            a.usados-link:hover {
                text-decoration: underline;
            }
        </style>
        <script src="https://unpkg.com/html5-qrcode"></script>
    </head>
    <body>
        <div class="box" id="mensagem">Clique em "Escanear QR Code" para começar</div>
        <button id="btnScan">Escanear QR Code</button>
        <div id="reader" style="display:none;"></div>
        <br>
        <a href="/usados" class="usados-link">Ver QR Codes escaneados</a>

        <script>
            const btnScan = document.getElementById('btnScan');
            const reader = document.getElementById('reader');
            const mensagemBox = document.getElementById('mensagem');
            let scanner;

            btnScan.addEventListener('click', () => {
                btnScan.style.display = 'none';
                reader.style.display = 'block';

                scanner = new Html5Qrcode("reader");

                Html5Qrcode.getCameras().then(devices => {
                    if (devices && devices.length) {
                        const backCamera = devices.find(device => device.label.toLowerCase().includes('back')) || devices[0];

                        scanner.start(
                            backCamera.id,
                            { fps: 10, qrbox: 250 },
                            (decodedText, decodedResult) => {
                                scanner.stop().then(() => {
                                    scanner.clear();  // limpa o scanner
                                    reader.style.display = 'none';
                                    btnScan.style.display = 'block';

                                    mensagemBox.innerHTML = `Validando código: <b>${decodedText}</b> ...`;

                                    fetch('/validar/' + encodeURIComponent(decodedText))
                                        .then(response => response.text())
                                        .then(html => {
                                            mensagemBox.innerHTML = html;
                                            scanner = null; // permite novo scanner no próximo clique
                                        })
                                        .catch(err => {
                                            mensagemBox.innerHTML = "Erro ao validar código.";
                                        });
                                }).catch(err => {
                                    console.error('Erro ao parar o scanner', err);
                                });
                            },
                            errorMessage => {
                                // Ignora erros temporários de leitura
                            }
                        ).catch(err => {
                            mensagemBox.innerHTML = "Não foi possível iniciar a câmera.";
                            btnScan.style.display = 'block';
                        });
                    } else {
                        mensagemBox.innerHTML = "Nenhuma câmera encontrada.";
                        btnScan.style.display = 'block';
                    }
                }).catch(err => {
                    mensagemBox.innerHTML = "Erro ao acessar câmeras: " + err;
                    btnScan.style.display = 'block';
                });
            });
        </script>
    </body>
    </html>
    """
    return html

@app.route("/validar/<codigo>")
def validar_qrcode(codigo):
    codigo = unquote(codigo)

    try:
        dados = json.loads(codigo)  # tenta interpretar JSON

        with open(ARQUIVO_USADOS, "r") as f:
            usados = json.load(f)

        if codigo in usados:
            mensagem = """
            <div style="color:#ff4d4d; font-weight:bold; font-size:24px;">⚠️ QRCODE JÁ USADO!</div>
            <small>Este código já foi validado anteriormente.</small>
            """
            cor = "#ffdddd"
        else:
            mensagem = """
            <div style="color:#4CAF50; font-weight:bold; font-size:24px;">✅ QRCODE VÁLIDO!</div>
            <small>Bem-vindo ao evento 🎉</small>
            """
            usados.append(codigo)
            with open(ARQUIVO_USADOS, "w") as f:
                json.dump(usados, f, indent=4)
            cor = "#ddffdd"

        detalhes = "<ul style='list-style:none; padding-left:0; font-size:18px; text-align:left;'>"
        for chave, valor in dados.items():
            detalhes += f"<li><strong>{chave.replace('_', ' ').title()}:</strong> {valor}</li>"
        detalhes += "</ul>"

        html = f"""
        <div style="background:{cor};padding:20px;border-radius:10px; max-width:500px; margin:20px auto; color:#333; font-family: Arial, sans-serif;">
            {mensagem}
            {detalhes}
        </div>
        """
    except json.JSONDecodeError:
        with open(ARQUIVO_USADOS, "r") as f:
            usados = json.load(f)

        if codigo in usados:
            mensagem = "⚠️ QRCODE JÁ USADO!<br><small>Este código já foi validado anteriormente.</small>"
            cor = "#ff4d4d"
        else:
            mensagem = "✅ QRCODE VÁLIDO!<br><small>Bem-vindo ao evento 🎉</small>"
            usados.append(codigo)
            with open(ARQUIVO_USADOS, "w") as f:
                json.dump(usados, f, indent=4)
            cor = "#4CAF50"

        html = f"""
        <div style="background:{cor};padding:20px;border-radius:10px;color:white;font-size:22px;max-width:500px;margin:20px auto;">
            {mensagem}<br><br>
            <strong>Código:</strong> {codigo}
        </div>
        """

    return html

@app.route("/usados")
def listar_usados():
    if os.path.exists(ARQUIVO_USADOS):
        with open(ARQUIVO_USADOS, "r") as f:
            usados = json.load(f)
    else:
        usados = []

    html = """
    <html>
    <head>
        <title>QR Codes Usados</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #eef1f5;
                margin: 0;
                padding: 0;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
            }
            h1 {
                text-align: center;
                margin-bottom: 30px;
                color: #333;
            }
            .qrcode-list {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                list-style: none;
                padding: 0;
            }
            .qrcode-card {
                background: white;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                font-size: 16px;
                word-break: break-word;
                display: flex;
                align-items: center;
                gap: 12px;
                transition: transform 0.2s;
            }
            .qrcode-card:hover {
                transform: scale(1.02);
            }
            .icon {
                font-size: 20px;
                color: #4CAF50;
            }
            .back-link {
                display: block;
                margin: 30px auto 0;
                text-align: center;
                font-size: 18px;
                color: #007bff;
                text-decoration: none;
            }
            .back-link:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>QR Codes Escaneados</h1>
            <ul class="qrcode-list">
    """

    for codigo in usados:
        html += f"""
        <li class="qrcode-card">
            <span class="icon">✅</span> {codigo}
        </li>
        """

    html += """
            </ul>
            <a class="back-link" href="/">← Voltar para a página inicial</a>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
