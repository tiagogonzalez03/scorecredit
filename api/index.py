from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

def carregar_dados():
    # Encontra o caminho correto do arquivo no Vercel
    api_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(api_dir, '..', 'data', 'SPGlobal_Export_4-14-2026_FinalVersion.xlsx - Sheet1.csv')
    
    # Lê o CSV
    df_raw = pd.read_csv(file_path, skiprows=4)
    df_raw = df_raw.iloc[1:].reset_index(drop=True)
    
    df = pd.DataFrame()
    # Mantém o formato original (ex: NYSE:MMM)
    df['Empresa'] = df_raw.iloc[:, 0].astype(str).str.strip()
    
    # Tratamento de números
    df['Divida_2024'] = pd.to_numeric(df_raw.iloc[:, 3].astype(str).str.replace(',', ''), errors='coerce')
    df['EBITDA_2024'] = pd.to_numeric(df_raw.iloc[:, 9].astype(str).str.replace(',', ''), errors='coerce')
    
    # Calcula a Alavancagem
    df['Alavancagem'] = (df['Divida_2024'] / df['EBITDA_2024'].replace(0, np.nan)).round(2)
    
    # Define o Rating
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
        query = request.args.get('empresa', '').strip().upper()
        df = carregar_dados()
        
        if query:
            # Busca o texto ignorando maiúsculas e minúsculas
            resultado = df[df['Empresa'].str.upper().str.contains(query, na=False)]
            
            if not resultado.empty:
                return resultado.iloc[0].to_json(force_ascii=False)
            
            return jsonify({"erro": f"Ticker ou Empresa '{query}' não encontrado."}), 404
            
        return jsonify({"status": "online", "mensagem": "API Funcionando!"})
    except Exception as e:
        return jsonify({"erro_interno": str(e)}), 500

# Esta linha final é OBRIGATÓRIA para o Vercel rodar o Flask
app = app
