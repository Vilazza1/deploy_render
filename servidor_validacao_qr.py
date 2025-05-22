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

@app.route("/exportar_excel")
def exportar_excel():
    # Verifica se os arquivos necessários existem
    if not os.path.exists(ARQUIVO_USADOS):
        return "Nenhum dado para exportar", 404
    if not os.path.exists(MODELO_XLSX):
        return "Modelo de planilha não encontrado", 404

    # Lê os dados do arquivo JSON
    with open(ARQUIVO_USADOS, "r") as f:
        usados = json.load(f)

    try:
        # Carrega o modelo de planilha
        wb = load_workbook(MODELO_XLSX)
        ws = wb.active

        # Insere os dados a partir da linha 2
        for idx, item in enumerate(usados, start=2):
            dados = json.loads(item)
            tipo = dados.get("tipo", "").lower()

            # Define os dados com base no tipo
            if tipo == "acompanhante":
                nome = dados.get("nome_acompanhante", "")
                titular = dados.get("nome_titular", "")
                cnpj = ""
                razao = ""
            else:
                nome = dados.get("nome", "")
                titular = ""
                cnpj = dados.get("cnpj", "")
                razao = dados.get("razao_social", "")

            # Preenche as células
            ws.cell(row=idx, column=1, value=nome)
            ws.cell(row=idx, column=2, value=tipo)
            ws.cell(row=idx, column=3, value=cnpj)
            ws.cell(row=idx, column=4, value=razao)
            ws.cell(row=idx, column=5, value=titular)

    except Exception as e:
        return f"Erro ao exportar planilha: {e}", 500

    # Prepara o arquivo para download
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
