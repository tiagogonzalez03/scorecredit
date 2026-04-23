from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

@app.route('/api/consulta')
def consulta():
    try:
        ticker = request.args.get('empresa', '').upper()
        
        # Caminho do CSV
        api_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(api_dir, '..', 'data', 'SPGlobal_Export_4-14-2026_FinalVersion.xlsx - Sheet1.csv')
        
        df = pd.read_csv(csv_path, skiprows=4)
        # Busca simples que contém o Ticker (ex: MMM)
        resultado = df[df.iloc[:, 0].str.contains(ticker, na=False, case=False)]

        if not resultado.empty:
            row = resultado.iloc[0]
            divida = pd.to_numeric(str(row.iloc[3]).replace(',', ''), errors='coerce')
            ebitda = pd.to_numeric(str(row.iloc[9]).replace(',', ''), errors='coerce')
            alav = round(divida / ebitda, 2) if ebitda > 0 else 0
            
            return jsonify({
                "Empresa": row.iloc[0],
                "Alavancagem": alav,
                "Rating": "🟢 BAIXO RISCO" if alav < 2 else "🔴 ALTO RISCO"
            })
        
        return jsonify({"erro": "Não encontrado"}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
