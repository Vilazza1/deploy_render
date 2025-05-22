from flask import Flask, render_template_string
import os
import json
from urllib.parse import unquote
import html

app = Flask(__name__)
ARQUIVO_USADOS = "usados.json"

# Cria arquivo se não existir
if not os.path.exists(ARQUIVO_USADOS):
    with open(ARQUIVO_USADOS, "w") as f:
        json.dump([], f)

@app.route("/")
def home():
    html_content = """[... seu HTML permanece igual, omitido por brevidade ...]"""
    return html_content

@app.route("/validar/<codigo>")
def validar_qrcode(codigo):
    with open(ARQUIVO_USADOS, "r") as f:
        usados = json.load(f)

    # Decodifica e tenta interpretar como JSON
    try:
        codigo_decodificado = unquote(codigo)
        dados = json.loads(codigo_decodificado)

        tipo = dados.get("tipo", "N/A").capitalize()
        acompanhante = dados.get("nome_acompanhante", "N/A")
        titular = dados.get("nome_titular", "N/A")

        dados_formatados = f"Tipo: {tipo} | Acompanhante: {acompanhante} | Titular: {titular}"

        mensagem_detalhes = f"""
        <b>👤 Tipo:</b> {html.escape(tipo)}<br>
        <b>🙋‍♂️ Acompanhante:</b> {html.escape(acompanhante)}<br>
        <b>🎟️ Titular:</b> {html.escape(titular)}
        """
    except Exception:
        # Se não for JSON
        dados_formatados = codigo
        mensagem_detalhes = f"<b>Conteúdo do QR Code:</b><br>{html.escape(codigo)}"

    if dados_formatados in usados:
        mensagem = "⚠️ QRCODE JÁ USADO!<br><small>Este código já foi validado anteriormente.</small>"
        cor = "#ff4d4d"
    else:
        mensagem = "✅ QRCODE VÁLIDO!<br><small>Bem-vindo ao evento 🎉</small>"
        usados.append(dados_formatados)
        with open(ARQUIVO_USADOS, "w") as f:
            json.dump(usados, f, indent=4)
        cor = "#4CAF50"

    html_resultado = f"""
    <div style="background:{cor};padding:20px;border-radius:10px;color:white;font-size:20px;max-width:600px;margin:20px auto;text-align:left;">
        {mensagem}<hr>{mensagem_detalhes}
    </div>
    """
    return html_resultado

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

    for item in usados:
        html += f"""
        <li class="qrcode-card">
            <span class="icon">✅</span> {html.escape(item)}
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
