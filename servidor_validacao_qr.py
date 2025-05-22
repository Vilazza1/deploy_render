from flask import Flask, render_template_string
import os
import json

app = Flask(__name__)
ARQUIVO_USADOS = "usados.json"

# Garante que o arquivo de controle exista
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
        <title>Scanner QR Code</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f7f7f7; text-align: center; padding: 50px; }
            #reader { width: 300px; margin: 20px auto; }
            button { font-size: 18px; padding: 10px 20px; margin-top: 30px; cursor: pointer; }
            .box { margin: 20px auto; max-width: 500px; font-size: 24px; color: #333; }
        </style>
        <script src="https://unpkg.com/html5-qrcode"></script>
    </head>
    <body>
        <div class="box" id="mensagem"></div>
        <button id="btnScan">Escanear QR Code</button>
        <div id="reader" style="display:none;"></div>

        <script>
            const btnScan = document.getElementById('btnScan');
            const reader = document.getElementById('reader');
            const mensagemBox = document.getElementById('mensagem');
            let scanner;

            btnScan.addEventListener('click', () => {{
                btnScan.style.display = 'none';
                reader.style.display = 'block';

                scanner = new Html5Qrcode("reader");
                scanner.start(
                    {{ facingMode: "environment" }},
                    {{
                        fps: 10,
                        qrbox: 250
                    }},
                    (decodedText, decodedResult) => {{
                        scanner.stop().then(() => {{
                            reader.style.display = 'none';
                            btnScan.style.display = 'block';

                            mensagemBox.innerHTML = `Validando código: <b>${{decodedText}}</b> ...`;

                            fetch('/validar/' + encodeURIComponent(decodedText))
                                .then(response => response.text())
                                .then(html => {{
                                    mensagemBox.innerHTML = html;
                                }})
                                .catch(err => {{
                                    mensagemBox.innerHTML = "Erro ao validar código.";
                                }});
                        }}).catch(err => {{
                            console.error('Erro ao parar o scanner', err);
                        }});
                    }},
                    errorMessage => {{
                        // erro silencioso
                    }}
                ).catch(err => {{
                    mensagemBox.innerHTML = "Não foi possível acessar a câmera.";
                }});
            }});
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
