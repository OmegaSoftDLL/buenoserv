#!/usr/bin/env python3
"""gen_openapi.py — Gera e serve documentação OpenAPI 3.0 do ecossistema BUENOSERV."""
import json, os
from flask import Flask, jsonify, Response

app = Flask(__name__)

SWAGGER_UI_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>BUENOSERV — API Docs</title>
<style>
  html { box-sizing: border-box; overflow-y: scroll; }
  *, *::before, *::after { box-sizing: inherit; }
  body { margin: 0; background: #fafafa; font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif; }
  #swagger-ui { max-width: 1460px; margin: 0 auto; padding: 20px; }
  .topbar { background: #1a1a2e; padding: 15px 0; }
  .topbar-wrapper { max-width: 1460px; margin: 0 auto; display: flex; align-items: center; padding: 0 20px; }
  .topbar-wrapper img { height: 36px; margin-right: 12px; }
  .topbar-wrapper span { color: #fff; font-size: 22px; font-weight: 600; }
  .info hgroup.main h2 { font-size: 28px; font-weight: 700; color: #1a1a2e; margin: 0 0 5px; }
  .info hgroup.main h4 { font-size: 14px; font-weight: 400; color: #666; margin: 0; }
  .scheme-container { background: #fff; border-radius: 8px; padding: 15px 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,.08); }
  .btn.authorize { background: #4a90d9; color: #fff; padding: 8px 18px; font-size: 14px; font-weight: 600; border-radius: 4px; cursor: pointer; border: none; text-decoration: none; display: inline-block; }
  .opblock-tag { padding: 12px 20px; background: #fff; border-radius: 8px; margin-bottom: 8px; box-shadow: 0 1px 4px rgba(0,0,0,.06); cursor: pointer; display: flex; align-items: center; justify-content: space-between; }
  .opblock-tag:hover { background: #f5f7fa; }
  .opblock-tag .tag__name { font-size: 18px; font-weight: 600; color: #1a1a2e; }
  .opblock { margin-bottom: 8px; border-radius: 6px; overflow: hidden; border: 1px solid #e4e6ef; }
  .opblock-summary { padding: 10px 15px; display: flex; align-items: center; gap: 12px; cursor: pointer; }
  .opblock-summary:hover { background: #f5f7fa; }
  .opblock-summary-method { font-size: 12px; font-weight: 700; text-transform: uppercase; padding: 4px 10px; border-radius: 3px; color: #fff; min-width: 60px; text-align: center; }
  .opblock-summary-path { font-size: 15px; font-weight: 600; color: #333; font-family: monospace; }
  .opblock-summary-summary { font-size: 13px; color: #888; margin-left: auto; }
  .opblock-body { padding: 0 15px 15px; display: none; }
  .method-get .opblock-summary-method { background: #61affe; }
  .method-post .opblock-summary-method { background: #49cc90; }
  .method-body { margin-top: 10px; }
  pre { background: #1e1e2e; color: #cdd6f4; padding: 14px; border-radius: 6px; overflow-x: auto; font-size: 13px; }
</style>
</head>
<body>
<div class="topbar"><div class="topbar-wrapper"><span>BUENOSERV API</span></div></div>
<div id="swagger-ui">
  <div class="info">
    <hgroup class="main"><h2>BUENOSERV OpenAPI 3.0</h2><h4>Ecossistema de Engenharia — Todos os endpoints documentados</h4></hgroup>
  </div>
  <div class="scheme-container">
    <div class="schemes">
      <label>Schema:</label>
      <a href="/openapi.json" target="_blank" class="btn authorize">openapi.json</a>
    </div>
  </div>
</div>
<script>
fetch('/openapi.json').then(r=>r.json()).then(spec=>{
  const groups={};
  for(const[path,methods]of Object.entries(spec.paths||{}))
    for(const[method,detail]of Object.entries(methods)){
      const tag=(detail.tags||['Geral'])[0];
      if(!groups[tag])groups[tag]={desc:'',endpoints:[]};
      groups[tag].endpoints.push({path,method,...detail});
    }
  for(const t of spec.tags||[])
    if(groups[t.name])groups[t.name].desc=t.description;
  const c=document.getElementById('swagger-ui');
  for(const[tag,data]of Object.entries(groups)){
    const s=document.createElement('div');
    let h='<div class="opblock-tag" onclick="this.nextElementSibling.style.display=this.nextElementSibling.style.display===\'none\'?\'block\':\'none\'"><div><span class="tag__name">'+tag+'</span></div><span>'+data.endpoints.length+' endpoints</span></div><div style="display:none">';
    for(const e of data.endpoints){
      const p=e.parameters||[],ok=e.responses?.['200']||e.responses?.['201']||{},ex=ok?.content?.['application/json']?.schema?.example;
      h+='<div class="opblock method-'+e.method+'"><div class="opblock-summary" onclick="this.nextElementSibling.style.display=this.nextElementSibling.style.display===\'none\'?\'block\':\'none\'"><span class="opblock-summary-method">'+e.method.toUpperCase()+'</span><span class="opblock-summary-path">'+e.path+'</span><span class="opblock-summary-summary">'+(e.summary||'')+'</span></div><div class="opblock-body" style="display:none">';
      if(e.description)h+='<p style="margin:8px 0;font-size:13px;color:#555">'+e.description+'</p>';
      if(p.length){
        h+='<div class="method-get"><strong>Parametros</strong><table><tr><th>Nome</th><th>Tipo</th><th>Obrig.</th></tr>';
        for(const q of p)h+='<tr><td><code>'+q.name+'</code></td><td><span>'+(q.schema?.type||'string')+'</span></td><td>'+(q.required?'Sim':'Nao')+'</td></tr>';
        h+='</table></div>';
      }
      if(ex)h+='<div class="method-get"><strong>Exemplo Resposta</strong><pre>'+JSON.stringify(ex,null,2)+'</pre></div>';
      h+='</div></div>';
    }
    h+='</div>';
    s.innerHTML=h;
    c.appendChild(s);
  }
});
</script>
</body>
</html>"""

def ep(method, tags, summary, desc, params=None, req_body=None, ex=None):
    entry = {"tags": tags, "summary": summary, "description": desc}
    entry["responses"] = {"200": {"description": "OK"}}
    if ex is not None:
        entry["responses"]["200"]["content"] = {"application/json": {"schema": {"type": "object", "example": ex}}}
    if params:
        entry["parameters"] = params
    if req_body:
        entry["requestBody"] = {"content": {"application/json": {"schema": {"type": "object", "properties": req_body[0], "example": req_body[1]}}, "required": req_body[2]}}
    return {method: entry}

def gp(name, req=True):
    return {"name": name, "in": "path", "required": req, "schema": {"type": "string"}, "description": name}

spec_data = None
def get_spec():
    global spec_data
    if spec_data:
        return spec_data
    spec_data = {
        "openapi": "3.0.3",
        "info": {"title": "BUENOSERV API — Ecossistema de Engenharia", "version": "1.0.0", "description": "API REST do ecossistema BUENOSERV: API Central, Departamentos, CAD/DWG, MCP, AI Engine e WhatsApp Bot."},
        "servers": [{"url": "http://localhost:8570"}, {"url": "/"}],
        "tags": [
            {"name": "API Central", "description": "Endpoints principais"},
            {"name": "Departamentos", "description": "Agentes de engenharia"},
            {"name": "CAD/DWG", "description": "Diagramas tecnicos"},
            {"name": "MCP Server", "description": "Model Context Protocol"},
            {"name": "AI Engine", "description": "Motor de IA com GPU"},
            {"name": "WhatsApp Bot", "description": "Bot WhatsApp integrado"},
        ],
        "paths": {}
    }
    p = spec_data["paths"]
    api_ex = {"agent_count": 81, "tasks": {}, "dre": {}, "projects": [], "scripts_disponiveis": [], "schedule": {}, "last_update": "2025-01-01T00:00:00"}
    p["/api/state"] = ep("get", ["API Central"], "Estado completo do ecossistema", "Retorna o agent_state.json com tasks, DRE, schedule, projetos e agentes.", ex=api_ex)
    p["/api/pipeline"] = ep("get", ["API Central"], "Pipeline comercial", "Extrai oportunidades comerciais das tasks com valores.", ex={"pipeline": [{"projeto":"Obra A","status":"negociacao","observacao":"R$ 500k","valor_extraido":500000.0}],"total_value":500000.0,"deals_count":1})
    p["/api/dre"] = ep("get", ["API Central"], "DRE financeiro", "Demonstrativo de Resultados por mes e acumulado.", ex={"ano":2025,"meses":{"1":{"receita_bruta":100000.0,"lucro_liquido":25000.0}},"totais":{"receita_bruta":100000.0}})
    p["/api/agents"] = ep("get", ["API Central"], "Lista de agentes", "Agentes com status e ultima atividade.", ex={"agent_count":200,"agents":[{"agente":"comercial","status":"ativo","ultima_atividade":"2025-01-01T10:00:00"}]})
    p["/api/scripts"] = ep("get", ["API Central"], "Scripts disponiveis", "Lista de scripts Python.", ex={"scripts_count":50,"scripts":["gen_api.py","gen_dre.py"]})
    p["/api/projects"] = ep("get", ["API Central"], "Projetos ativos", "Lista de projetos registrados.", ex={"projects_count":5,"projects":[{"nome":"Obra A","status":"em_andamento"}]})
    p["/api/cron"] = ep("get", ["API Central"], "Jobs cron", "Agendamentos por frequencia.", ex={"cron_jobs":[{"frequencia":"diario","job":"gen_backup.py"}]})
    p["/api/health"] = ep("get", ["API Central"], "Healthcheck", "Verifica arquivos criticos e state.", ex={"status":"healthy","checks":{"agent_state.json":"pass"},"timestamp":"2025-01-01T00:00:00"})
    p["/api/market"] = ep("get", ["API Central"], "Oportunidades de mercado", "Oportunidades extraidas de market intel.", ex={"fonte":"oportunidades.json","oportunidades":[]})
    p["/api/summary"] = ep("get", ["API Central"], "Sumario executivo", "Visao consolidada do ecossistema.", ex={"agent_count":200,"total_pipeline_value":500000.0,"pipeline_deals":3,"scripts_count":50,"projects_count":5,"status":"healthy"})

    p["/"] = ep("get", ["Departamentos"], "Info do departamento", "Nome, agentes e status.", ex={"servico":"BUENOSERV - Departamento ENGENHARIA","agentes":30,"status":"operacional"})
    p["/agentes"] = ep("get", ["Departamentos"], "Agentes do departamento", "Lista agentes filtrados por padroes.", ex=[{"nome":"telecom","descricao":"Telecom","modo":"auto","tamanho":2048}])
    p["/agentes/{nome}"] = ep("get", ["Departamentos"], "Agente especifico", "Conteudo completo do agente.", params=[gp("nome")])
    p["/buscar"] = ep("post", ["Departamentos"], "Buscar nos agentes", "Busca texto nos agentes.", req_body=[{"q":{"type":"string"}}, {"q":"fibra"}, ["q"]], ex={"resultados":[{"agente":"fibra","linha":42,"texto":"..."}],"total":1})
    p["/state"] = ep("get", ["Departamentos"], "Estado do departamento", "agent_state.json bruto.", ex={})
    p["/saude"] = ep("get", ["Departamentos"], "Saude do departamento", "Agentes e memoria.", ex={"departamento":"ENGENHARIA","agentes_carregados":30,"memoria_mb":120})

    p["/cad"] = ep("get", ["CAD/DWG"], "Info CAD", "Nome, versao, comandos.", ex={"servico":"BUENOSERV CAD/DWG Service","versao":"1.0","comandos":["unifilar","telecom","rack","fibra"]})
    p["/cad/gerar/{tipo}"] = ep("post", ["CAD/DWG"], "Gerar diagrama", "Gera DWG (unifilar, telecom, rack, fibra).", params=[gp("tipo")], req_body=[{"projeto":{"type":"string"},"tensao":{"type":"string"},"barramentos":{"type":"integer"}}, {"projeto":"SE_Exemplo","tensao":"138kV","barramentos":4}, []])
    p["/cad/gerar"] = ep("post", ["CAD/DWG"], "Gerar personalizado", "Tipo no body.", req_body=[{"tipo":{"type":"string","enum":["unifilar","telecom","rack","fibra"]}}, {"tipo":"unifilar","projeto":"ObraX"}, []])
    p["/cad/listar"] = ep("get", ["CAD/DWG"], "Listar arquivos", "Arquivos .dwg .dxf .pdf.", ex={"arquivos":["projeto_unifilar.dwg"],"total":1})

    p["/mcp"] = ep("get", ["MCP Server"], "Info MCP", "Nome, versao, tools.", ex={"nome":"BUENOSERV MCP Server","versao":"1.0","protocolo":"Model Context Protocol","total_tools":8})
    p["/mcp/tools"] = ep("get", ["MCP Server"], "Ferramentas MCP", "Detalhes com parametros.", ex={"consultar_state":{"descricao":"Consulta estado","parametros":{"chave":"opcional"}}})
    p["/mcp/call"] = ep("post", ["MCP Server"], "Chamar ferramenta", "Executa tool no MCP.", req_body=[{"tool":{"type":"string"},"params":{"type":"object"}}, {"tool":"consultar_state","params":{}}, ["tool","params"]])
    p["/mcp/agents"] = ep("get", ["MCP Server"], "Agentes MCP", "Lista agentes .md.", ex={"total":200,"agentes":["telecom","comercial"]})

    p["/health"] = ep("get", ["WhatsApp Bot"], "Saude do servico", "Status operacional.", ex={"status":"ok"})

    p["/ai"] = ep("get", ["AI Engine"], "Info motor IA", "GPUs e modelos.", ex={"servico":"BUENOSERV AI Engine - IA","gpus_disponiveis":1,"gpus":["NVIDIA A100"],"modelos":["engenharia-llm"]})
    p["/gpu"] = ep("get", ["AI Engine"], "Status GPUs", "nvidia-smi metrics.", ex={"gpus":[{"index":"0","name":"NVIDIA A100","temp":"45","util":"10","mem_used":"2048","mem_total":"40960"}],"total":1})
    p["/inferir/{modelo}"] = ep("post", ["AI Engine"], "Inferencia", "Inferencia simulada em GPU.", params=[gp("modelo")], req_body=[{"prompt":{"type":"string"}}, {"prompt":"Descreva unifilar"}, ["prompt"]], ex={"modelo":"engenharia-llm","prompt":"Descreva...","resposta":"Processado via GPU","tempo_segundos":0.5,"gpu_utilizada":"NVIDIA A100"})
    p["/treinar"] = ep("post", ["AI Engine"], "Treinamento", "Fine-tuning simulado.", req_body=[{"dataset":{"type":"string"},"epocas":{"type":"integer"}}, {"dataset":"engenharia","epocas":3}, []], ex={"status":"simulado","dataset":"engenharia","epocas":3})
    p["/modelos"] = ep("get", ["AI Engine"], "Modelos disponiveis", "Nome e tamanho dos modelos.", ex={"modelos":[{"nome":"engenharia-llm","tamanho_mb":2048.0}]})

    p["/webhook"] = ep("post", ["WhatsApp Bot"], "Webhook", "Recebe mensagens WhatsApp.", req_body=[{"from":{"type":"string"},"text":{"type":"string"}}, {"from":"551999999999","text":"/status"}, []], ex={"status":"ok"})
    p["/enviar"] = ep("post", ["WhatsApp Bot"], "Enviar mensagem", "Envia via Evolution API ou simulado.", req_body=[{"numero":{"type":"string"},"mensagem":{"type":"string"}}, {"numero":"551999999999","mensagem":"Ola!"}, ["numero","mensagem"]], ex={"status":"enviado"})
    p["/log"] = ep("get", ["WhatsApp Bot"], "Log mensagens", "Ultimas 100 mensagens.", ex=[{"direcao":"recebido","numero":"551999999999","mensagem":"/status","data":"2025-01-01T00:00:00"}])
    p["/status"] = ep("get", ["WhatsApp Bot"], "Status bot", "Modo e configuracao.", ex={"modo":"simulado","instancia":"buenoserv","evo_api_url":"nao configurado"})

    return spec_data

@app.route("/openapi.json")
def openapi_json():
    return jsonify(get_spec())

@app.route("/docs")
def docs():
    return Response(SWAGGER_UI_HTML, mimetype="text/html")

@app.route("/")
def root():
    return Response(SWAGGER_UI_HTML, mimetype="text/html")

if __name__ == "__main__":
    print("BUENOSERV OpenAPI Docs")
    print(f"  Swagger UI: http://localhost:8570/docs")
    print(f"  Schema:    http://localhost:8570/openapi.json")
    app.run(host="0.0.0.0", port=8570, debug=False)