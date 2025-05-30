# 🧾 Sistema de Validação de QR Code com Flask

Este projeto é uma aplicação web simples que permite **validar QR Codes** em eventos. A aplicação registra os códigos validados para evitar duplicidade de uso.

---

## 🚀 Tecnologias Utilizadas

- **Python 3.11**
- **Flask** – microframework web para criação da API e interface.
- **JavaScript + HTML5** – para capturar o QR Code diretamente pela câmera do navegador.
- **LocalStorage (temporário)** – para armazenar códigos já usados em um arquivo JSON simples (`usados.json`).
- **Render.com** – plataforma usada para deploy automático.

---

## 🧠 Lógica do Sistema

### ✅ Validação

1. O usuário acessa a aplicação por um navegador no celular.
2. Clica no botão **"Escanear QR Code"**.
3. A câmera é ativada via `navigator.mediaDevices.getUserMedia`.
4. O código QR é lido em tempo real com a biblioteca **jsQR**.
5. Quando o QR Code é detectado:
   - É enviado para o endpoint `/validar/<codigo>`.
   - O servidor verifica se ele já está no arquivo `usados.json`.
   - Se for **novo**, é marcado como **válido** e registrado no arquivo.
   - Se for **repetido**, mostra um alerta de que o código já foi usado.

---

## 📁 Estrutura de Arquivos

├── servidor_validacao_qr.py # Código principal do Flask
├── usados.json # Armazena os QR Codes já validados
├── requirements.txt # Dependências do projeto
├── static/
│ └── jsQR.js # Biblioteca JS para leitura do QRCode


---

## 🛠️ Como Rodar Localmente

1. Clone o projeto:
   
   ```bash
   git clone https://github.com/Vilazza1/deploy_render.git
   cd deploy_render


2. Crie e ative um ambiente virtual:

    python -m venv venv
    source venv/bin/activate     # Linux/macOS
    .\venv\Scripts\activate      # Windows

3. Instale as dependências:

    pip install -r requirements.txt

4. Execute o servidor:

    python servidor_validacao_qr.py

5. Acesse: http://127.0.0.1:5000

🌐 Deploy na Render

    1. Crie um repositório no GitHub com todos os arquivos.

    2. Vá até Render.com e:

        Crie um novo serviço Web Service.

        Conecte seu repositório.

        Configure o build command como:

        pip install -r requirements.txt

    3. Espere o deploy finalizar.

🔒 Observações

    O sistema não tem autenticação — qualquer pessoa com acesso ao link pode escanear.

    O banco de dados usado é apenas um arquivo JSON (usados.json). Para uso em produção, recomenda-se um banco como SQLite, PostgreSQL ou Redis.

    A câmera funciona apenas em HTTPS ou localhost. Render já fornece HTTPS.

📦 Futuras Melhorias

    Autenticação de administradores.

    Painel para visualizar todos os códigos validados.

    Exportação de lista para Excel.

    Banco de dados persistente (PostgreSQL ou SQLite).

    Design aprimorado com TailwindCSS ou Bootstrap.

🧑‍💻 Autor

    Vinicius Vilaça

    GitHub: @Vilazza1

    LinkedIn: Vinicius Vilaça

