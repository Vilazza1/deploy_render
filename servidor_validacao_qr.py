from flask import send_file
import pandas as pd
from openpyxl import load_workbook
from io import BytesIO

@app.route("/exportar")
def exportar_excel():
    if not os.path.exists(ARQUIVO_USADOS):
        return "Nenhum dado para exportar."

    with open(ARQUIVO_USADOS, "r") as f:
        usados = json.load(f)

    dados_formatados = []

    for item in usados:
        try:
            d = json.loads(item)
            dados_formatados.append({
                "Nome": d.get("nome", ""),
                "Tipo": d.get("tipo", ""),
                "Documento": d.get("documento", ""),
                "Email": d.get("email", ""),
                "Telefone": d.get("telefone", "")
            })
        except:
            continue

    df = pd.DataFrame(dados_formatados)

    # Carrega modelo e escreve os dados
    modelo_path = "modelo.xlsx"
    wb = load_workbook(modelo_path)
    ws = wb.active

    # Escreve os dados começando da linha 2 (assumindo linha 1 com cabeçalhos)
    for idx, row in df.iterrows():
        for col_idx, value in enumerate(row.values, start=1):
            ws.cell(row=idx + 2, column=col_idx, value=value)

    # Salva para memória e envia para download
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="qrcodes_exportados.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
