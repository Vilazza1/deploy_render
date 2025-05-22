from flask import Flask, request, send_file
import os
import json
from io import BytesIO
from openpyxl import load_workbook

app = Flask(__name__)

ARQUIVO_USADOS = "usados.json"
MODELO_XLSX = "modelo.xlsx"

# Cria o arquivo JSON se não existir
if not os.path.exists(ARQUIVO_USADOS):
    with open(ARQUIVO_USADOS, "w") as f:
        json.dump([], f)

@app.route("/")
def home():
    return "<h1>API de Validação QRCode</h1>"

@app.route("/validar", methods=["POST"])
def validar_qrcode():
    data = request.get_json()
    codigo = data.get("codigo", "")

    try:
        dados = json.loads(codigo)

        with open(ARQUIVO_USADOS, "r") as f:
            usados = json.load(f)

        if codigo in usados:
            return "QR Code já foi usado.", 200
        else:
            usados.append(codigo)
            with open(ARQUIVO_USADOS, "w") as f:
                json.dump(usados, f, indent=4)
            return "QR Code válido!", 200
    except json.JSONDecodeError:
        return "Erro: QRCode inválido.", 400

@app.route("/exportar_excel")
def exportar_excel():
    if not os.path.exists(ARQUIVO_USADOS):
        return "Nenhum dado para exportar", 404
    if not os.path.exists(MODELO_XLSX):
        return "Modelo de planilha não encontrado", 404

    with open(ARQUIVO_USADOS, "r") as f:
        usados = json.load(f)

    try:
        wb = load_workbook(MODELO_XLSX)
        ws = wb.active

        # Escreve cabeçalhos (opcional se modelo não tiver)
        ws.cell(row=1, column=1, value="Nome")
        ws.cell(row=1, column=2, value="Tipo")
        ws.cell(row=1, column=3, value="Nome Titular")
        ws.cell(row=1, column=4, value="Documento")
        ws.cell(row=1, column=5, value="Email")
        ws.cell(row=1, column=6, value="Telefone")

        for idx, item in enumerate(usados, start=2):
            dados = json.loads(item)
            tipo = dados.get("tipo", "").lower()

            if tipo == "acompanhante":
                nome = dados.get("nome_acompanhante", "")
                nome_titular = dados.get("nome_titular", "")
            else:
                nome = dados.get("nome", "")
                nome_titular = ""

            ws.cell(row=idx, column=1, value=nome)
            ws.cell(row=idx, column=2, value=tipo)
            ws.cell(row=idx, column=3, value=nome_titular)
            ws.cell(row=idx, column=4, value=dados.get("documento", ""))
            ws.cell(row=idx, column=5, value=dados.get("email", ""))
            ws.cell(row=idx, column=6, value=dados.get("telefone", ""))
    except Exception as e:
        return f"Erro ao exportar planilha: {e}", 500

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="qrcodes_exportados.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
