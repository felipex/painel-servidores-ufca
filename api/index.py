from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")


# Carrega os dados ao iniciar
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "servidores.csv")
df = pd.read_csv(CSV_PATH, dtype={'siape': str})

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/buscar")
async def buscar_servidor(request: Request):
    form_data = await request.form()
    siape_buscado = form_data.get("siape")
    
    # Filtra o servidor pelo SIAPE
    servidor = df[df['siape'] == siape_buscado]
    
    if servidor.empty:
        return HTMLResponse("<div class='error'>Servidor não encontrado.</div>")
    
    dados = servidor.iloc[0].to_dict()
    
    # Retorna apenas o pedaço de HTML que o HTMX vai injetar
    return f"""<div class="result-card">
        <p><strong>Nome:</strong> {dados['nome']}</p>
        <p><strong>Setor:</strong> {dados['setor']}</p>
        <p><strong>Escolaridade:</strong> {dados['escolaridade']}</p>
        <p><strong>Data de Ingresso:</strong> {dados['data_ingresso']}</p>
        <p><strong>Gratificação:</strong> R$ {dados['gratificacao'] if pd.notna(dados['gratificacao']) else '0,00'}</p>
    </div>""".replace("\n", "")
    

# Adicione esta URL da sua planilha (substitua pelo link que você copiou)
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTH0uukZzqz3Vahb3jBDtyd2Q4jwXJaEAal5Lb4ucmFmlFtcehT751_MCeBPwN2lML1o6TpkJ8ziNPt/pub?gid=337243754&single=true&output=csv"

@app.post("/buscar-google")
async def buscar_google(request: Request):
    form_data = await request.form()
    siape_buscado = form_data.get("siape")
    
    try:
        # O Pandas consegue ler diretamente da URL do Google
        df_google = pd.read_csv(GOOGLE_SHEET_CSV_URL, dtype={'siape': str})
        
        servidor = df_google[df_google['siape'] == siape_buscado]
        
        if servidor.empty:
            return HTMLResponse("<div class='error'>Servidor não encontrado na Planilha Google.</div>")
        
        dados = servidor.iloc[0].to_dict()
        
        return f"""
        <div class="result-card" style="border-left-color: #28a745; background: #eaffea;">
            <p><strong>Origem:</strong> Planilha Google (Nuvem)</p>
            <p><strong>Nome:</strong> {dados['nome']}</p>
            <p><strong>Setor:</strong> {dados['setor']}</p>
            <p><strong>Status:</strong> Dados atualizados em tempo real</p>
        </div>
        """
    except Exception as e:
        return HTMLResponse(f"<div class='error'>Erro ao conectar com o Google Sheets: {str(e)}</div>")
