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
            li { background: white; margin: 5px 0; padding: 12px 20px; border-radius: 8px; font-size: 18px; text-align: left; }
            a { display: block; max-width: 200px; margin: 20px auto; text-align: center; text-decoration: none; color: #007bff; }
            a:hover { text-decoration: underline; }
            .campo { font-weight: bold; }
            .valor { margin-left: 5px; }
        </style>
    </head>
    <body>
        <h1>QR Codes Escaneados</h1>
        <ul>
    """

    for codigo in usados:
        try:
            dados = json.loads(codigo)
            if dados.get("tipo") == "titular":
                nome = dados.get("nome", "N/A")
                cnpj = dados.get("cnpj", "N/A")
                razao = dados.get("razao_social", "N/A")
                html += f"<li><div><span class='campo'>Titular:</span> <span class='valor'>{nome}</span></div>"
                html += f"<div><span class='campo'>CNPJ:</span> <span class='valor'>{cnpj}</span></div>"
                html += f"<div><span class='campo'>Razão Social:</span> <span class='valor'>{razao}</span></div></li>"
            elif dados.get("tipo") == "acompanhante":
                nome_acomp = dados.get("nome_acompanhante", "N/A")
                nome_titular = dados.get("nome_titular", "N/A")
                html += f"<li><div><span class='campo'>Acompanhante:</span> <span class='valor'>{nome_acomp}</span></div>"
                html += f"<div><span class='campo'>Titular:</span> <span class='valor'>{nome_titular}</span></div></li>"
            else:
                # Se não for JSON esperado, só mostrar o texto
                html += f"<li>{codigo}</li>"
        except json.JSONDecodeError:
            # Se não for JSON válido, mostrar o texto cru
            html += f"<li>{codigo}</li>"

    html += """
        </ul>
        <a href="/">Voltar para a página inicial</a>
    </body>
    </html>
    """
    return html
