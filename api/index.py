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
    return f"""
    <div class="result-card">
        <p><strong>Nome:</strong> {dados['nome']}</p>
        <p><strong>Setor:</strong> {dados['setor']}</p>
        <p><strong>Escolaridade:</strong> {dados['escolaridade']}</p>
        <p><strong>Data de Ingresso:</strong> {dados['data_ingresso']}</p>
        <p><strong>Gratificação:</strong> R$ {dados['gratificacao'] if pd.notna(dados['gratificacao']) else '0,00'}</p>
    </div>
    """
