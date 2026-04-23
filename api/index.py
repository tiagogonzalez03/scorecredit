from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app) # Isso resolve qualquer problema de conexão entre HTML e Python

def carregar_dados_e_buscar(ticker):
    # Caminho exato do seu arquivo
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "..", "data", "SPGlobal_Export_4-14-2026_FinalVersion.csv")
    
    if not os.path.exists(csv_path):
        return {"erro": "Arquivo CSV não encontrado no servidor."}

    # Lendo o CSV pulando as 4 linhas de cabeçalho da S&P
    df = pd.read_csv(csv_path, skiprows=4)
    
    # Busca o ticker (ex: MMM) dentro da string da 1ª coluna (ex: NYSE:MMM)
    # Convertemos tudo para string e maiúsculo para não ter erro
    resultado = df[df.iloc[:, 0].astype(str).str.upper().str.contains(ticker.upper(), na=False)]
    
    if resultado.empty:
        return {"erro": f"Ticker {ticker} não encontrado."}
    
    row = resultado.iloc[0]
    
    # Tratamento de valores (removendo vírgulas de milhares)
    try:
        divida = float(str(row.iloc[3]).replace(',', ''))
        ebitda = float(str(row.iloc[9]).replace(',', ''))
        alavancagem = round(divida / ebitda, 2) if ebitda > 0 else 0
    except:
        alavancagem = 0
        
    rating = "🟢 BAIXO RISCO" if alavancagem < 2.5 else "🟡 RISCO MODERADO" if alavancagem < 4.5 else "🔴 ALTO RISCO"
    
    return {
        "Empresa": str(row.iloc[0]),
        "Alavancagem": alavancagem,
        "Rating": rating
    }

@app.route('/api/consulta')
def consulta():
    ticker = request.args.get('empresa', '').strip()
    if not ticker:
        return jsonify({"erro": "Digite um ticker"}), 400
    
    res = carregar_dados_e_buscar(ticker)
    status = 404 if "erro" in res and "não encontrado" in res["erro"] else (500 if "erro" in res else 200)
    return jsonify(res), status

# Rota de teste: se você acessar /api/health no navegador e ler "OK", o Python está vivo!
@app.route('/api/health')
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run()
