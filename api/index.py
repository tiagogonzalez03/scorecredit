from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

@app.route('/api/consulta')
def consulta():
    ticker = request.args.get('empresa', '').upper()
    # Retorno fixo apenas para testar se a página para de dar 404
    return jsonify({
        "Empresa": f"Teste {ticker}",
        "Alavancagem": 1.5,
        "Rating": "🟢 CONECTADO"
    })

app = app
