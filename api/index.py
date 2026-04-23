from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import os

app = Flask(__name__)
CORS(app) # Permite que o app seja consultado por outros sites

def carregar_dados():
    api_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(api_dir, '..', 'data', 'SPGlobal_Export_4-14-2026_FinalVersion.xlsx - Sheet1.csv')
    
    # Lendo o CSV pulando as 4 linhas de cabeçalho da S&P
    df_raw = pd.read_csv(file_path, skiprows=4)
    df_raw = df_raw.iloc[1:].reset_index(drop=True)
    
    df = pd.DataFrame()
    # Mantemos o nome original (ex: NYSE:MMM) para a busca ser precisa
    df['Empresa'] = df_raw.iloc[:, 0].astype(str).str.strip()
    
    # Tratamento de números (Removendo vírgulas de milhares)
    df['Divida_2024'] = pd.to_numeric(df_raw.iloc[:, 3].astype(str).str.replace(',', ''), errors='coerce')
    df['EBITDA_2024'] = pd.to_numeric(df_raw.iloc[:, 9].astype(str).str.replace(',', ''), errors='coerce')
    
    df['Alavancagem'] = (df['Divida_2024'] / df['EBITDA_2024'].replace(0, np.nan)).round(2)
    
    def definir_rating(row):
        if pd.isna(row['Alavancagem']) or row['EBITDA_2024'] <= 0: return '🔴 RISCO CRÍTICO'
        if row['Alavancagem'] > 4.5: return '🔴 ALTO RISCO'
        if row['Alavancagem'] < 2.0: return '🟢 BAIXO RISCO'
        return '🟡 MODERADO'
    
    df['Rating'] = df.apply(definir_rating, axis=1)
    return df

@app.route('/api/consulta')
def home():
    try:
        query = request.args.get('empresa', '').strip().upper() # Transforma busca em MAIÚSCULA
        df = carregar_dados()
        
        if query:
            # A mágica está aqui: ele procura se o que você digitou (Ex: MMM) 
            # está dentro da string da coluna Empresa (Ex: NYSE:MMM)
            resultado = df[df['Empresa'].str.upper().str.contains(query, na=False)]
            
            if not resultado.empty:
                # Pegamos o primeiro match e enviamos
                return resultado.iloc[0].to_json(force_ascii=False)
            
            return jsonify({"erro": f"Ticker ou Empresa '{query}' não encontrado."}), 404
            
        return jsonify({"status": "online"})
    except Exception as e:
        return jsonify({"erro_interno": str(e)}), 500
    
    return jsonify({
        "status": "online",
        "mensagem": "API de Risco de Crédito Ativa. Use ?empresa=NOME para consultar."
    })

# Essencial para o Vercel identificar a função serveless
index = app
