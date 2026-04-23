from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

@app.route('/api/consulta')
def consulta():
    try:
        ticker = request.args.get('empresa', '').strip().upper()
        if not ticker:
            return jsonify({"erro": "Digite um ticker"}), 400

        # CAMINHO CORRIGIDO COM O NOME QUE VOCÊ PASSOU
        api_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(api_dir, '..', 'data', 'SPGlobal_Export_4-14-2026_FinalVersion.csv')

        if not os.path.exists(csv_path):
            return jsonify({"erro": "Arquivo CSV nao encontrado. Verifique a pasta data."}), 500

        # Leitura do CSV (S&P costuma ter 4 linhas de lixo no topo)
        df = pd.read_csv(csv_path, skiprows=4)
        
        # Busca o ticker dentro da primeira coluna (Ex: busca MMM em NYSE:MMM)
        resultado = df[df.iloc[:, 0].str.contains(ticker, na=False, case=False)]

        if not resultado.empty:
            row = resultado.iloc[0]
            divida = pd.to_numeric(str(row.iloc[3]).replace(',', ''), errors='coerce')
            ebitda = pd.to_numeric(str(row.iloc[9]).replace(',', ''), errors='coerce')
            alav = round(divida / ebitda, 2) if ebitda and ebitda > 0 else 0
            
            return jsonify({
                "Empresa": str(row.iloc[0]),
                "Alavancagem": alav,
                "Rating": "🟢 BAIXO RISCO" if alav < 2.5 else "🟡 MODERADO" if alav < 4.5 else "🔴 ALTO RISCO"
            })
        
        return jsonify({"erro": f"Ticker '{ticker}' nao encontrado."}), 404
    except Exception as e:
        return jsonify({"erro_sistema": str(e)}), 500

app = app
