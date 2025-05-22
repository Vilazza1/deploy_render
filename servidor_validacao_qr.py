from flask import Flask, render_template_string
import os
import json

app = Flask(__name__)
ARQUIVO_USADOS = "usados.json"

# Cria arquivo de controle se não existir
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
                                    reader.style.display = 'none';
                                    btnScan.style.display = 'block';

                                    mensagemBox.innerHTML = `Validando código: <b>${decodedText}</b> ...`;

                                    fetch('/validar/' + encodeURIComponent(decodedText))
                                        .then(response => response.text())
                                        .then(html => {
                                            mensagemBox.innerHTML = html;
                                        })
                                        .catch(err => {
                                            mensagemBox.innerHTML = "Erro ao validar código.";
                                        });
                                }).catch(err => {
                                    console.error('Erro ao parar o scanner', err);
                                });
                            },
                            errorMessage => {
                                // Erros silenciosos durante leitura
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
        {mensagem}
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
            body { font-family: Arial, sans-serif; padding: 20px; background: #f7f7f7; }
            h1 { text-align: center; }
            ul { max-width: 600px; margin: 20px auto; padding: 0; list-style: none; }
            li { background: white; margin: 5px 0; padding: 12px 20px; border-radius: 8px; font-size: 18px; }
            a { display: block; max-width: 200px; margin: 20px auto; text-align: center; text-decoration: none; color: #007bff; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>QR Codes Escaneados</h1>
        <ul>
    """

    for codigo in usados:
        html += f"<li>{codigo}</li>"

    html += """
        </ul>
        <a href="/">Voltar para a página inicial</a>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
