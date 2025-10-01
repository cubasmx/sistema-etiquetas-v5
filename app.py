# app.py
# -*- coding: utf-8 -*-
import os
import json
import socket
import ast
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Reusa tus clientes
from odoo_client import OdooClient
from src.utils.mysql_client import MysqlClient

APP_DIR = Path(__file__).parent
PRINTER_CFG_PATH = APP_DIR / "printer_config.json"
ODOO_CFG_PATH = APP_DIR / "odoo_config.py"

# ---------- Utilidades ----------
def load_printer_cfg() -> dict:
    if PRINTER_CFG_PATH.exists():
        try:
            return json.loads(PRINTER_CFG_PATH.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[WARN] Error cargando printer_config.json: {e}")
    return {
        "printer_ip": "10.10.2.23",
        "printer_port": 6101,
        "vertical_offset_dots": 20,
        "horizontal_offset_dots": 10,
    }

def save_printer_cfg(cfg: dict):
    PRINTER_CFG_PATH.write_text(json.dumps(cfg, indent=4), encoding="utf-8")

def load_odoo_cfg() -> dict:
    if ODOO_CFG_PATH.exists():
        content = ODOO_CFG_PATH.read_text(encoding="utf-8")
        start = content.find('{')
        end = content.rfind('}') + 1
        if start > -1 and end > 0:
            try:
                return ast.literal_eval(content[start:end])
            except Exception as e:
                print(f"[WARN] No se pudo parsear odoo_config.py: {e}")
    return {"url": "", "db": "", "username": "", "password": "", "port": 443}

def save_odoo_cfg(cfg: dict):
    content = (
        "# -*- coding: utf-8 -*-\n\n"
        "# Configuración de conexión a Odoo\n"
        f"ODOO_CONFIG = {json.dumps(cfg, indent=4)}\n"
    )
    ODOO_CFG_PATH.write_text(content, encoding="utf-8")

def zpl_send_batch(
    labels: List[str],
    printer_ip: str,
    printer_port: int,
    timeout: int = 5
) -> int:
    """Envía una lista de cadenas ZPL a la impresora RAW. Devuelve cuántas se enviaron."""
    sent = 0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        sock.connect((printer_ip, printer_port))
        for zpl in labels:
            try:
                sock.sendall(zpl.encode("latin1"))
                sent += 1
            except Exception as e:
                print(f"[ERROR] Falló envío ZPL: {e}")
                continue
    return sent

def apply_offsets(x: int, y: int, dx: int, dy: int) -> tuple[int, int]:
    xx = x + dx
    yy = y + dy
    if xx < 0: xx = 0
    if yy < 0: yy = 0
    return xx, yy


# ---------- FastAPI ----------
app = FastAPI(title="Etiquetas Web", version="1.0")

# Si piensas servir desde el mismo host, puedes cerrar CORS. Lo dejo abierto a LAN.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes especificar tus subredes/orígenes
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instancia Odoo al arranque
try:
    odoo_client = OdooClient()
    ODOO_OK = True
except Exception as e:
    print(f"[WARN] Odoo no disponible al arranque: {e}")
    odoo_client = None
    ODOO_OK = False


# ---------- Rutas: UI ----------
@app.get("/", response_class=HTMLResponse)
def index():
    # UI simple (HTML+JS) – SPA minimalista
    return HTMLResponse(content=f"""
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Impresión de Etiquetas (Web)</title>
<style>
body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, 'Helvetica Neue', Arial; margin: 24px; color: #111; }}
h1 {{ font-size: 20px; margin: 0 0 16px; }}
fieldset {{ border: 1px solid #ddd; padding: 12px; border-radius: 8px; margin-bottom: 16px; }}
legend {{ padding: 0 6px; color: #555; }}
label {{ display:block; font-size: 14px; margin: 8px 0 4px; }}
input, button, select {{ font-size: 14px; padding: 8px; }}
input[type="number"] {{ width: 120px; }}
.row {{ display:flex; gap:12px; align-items: center; flex-wrap: wrap; }}
.results {{ border:1px solid #eee; border-radius:6px; padding:8px; max-height: 260px; overflow:auto; }}
.result-item {{ padding:6px; border-bottom:1px dashed #eee; cursor:pointer; }}
.result-item:hover {{ background:#fafafa; }}
.badge {{ display:inline-block; padding:2px 6px; font-size:12px; background:#eef; color:#224; border-radius:4px; margin-left:8px; }}
button.primary {{ background:#111; color:#fff; border:none; border-radius:8px; cursor:pointer; }}
button.secondary {{ background:#f2f2f2; border:1px solid #ddd; border-radius:8px; cursor:pointer; }}
hr {{ border: none; border-top: 1px solid #eee; margin: 16px 0; }}
.small {{ font-size:12px; color:#666; }}
.success {{ color: #0a7d00; }}
.warn {{ color: #ad5e00; }}
.error {{ color: #b00020; }}
code {{ background:#f7f7f7; padding:2px 4px; border-radius:4px; }}
</style>
</head>
<body>
<h1>Impresión de Etiquetas (Web)</h1>

<fieldset>
  <legend>Estado</legend>
  <div id="status"></div>
</fieldset>

<fieldset>
  <legend>Búsqueda de productos (Odoo)</legend>
  <div class="row">
    <label for="q">Buscar ID o nombre</label>
    <input id="q" type="text" placeholder="Ej: 77-521 o percha"/>
    <button class="secondary" onclick="doSearch()">Buscar</button>
    <button class="secondary" onclick="clearResults()">Limpiar</button>
  </div>
  <div id="results" class="results"></div>
  <div id="selected" class="small"></div>
</fieldset>

<fieldset>
  <legend>Datos de la etiqueta</legend>
  <div class="row">
    <div>
      <label>OP</label>
      <input id="op" type="text" placeholder="OP..."/>
    </div>
    <div>
      <label>Versión SGC</label>
      <input id="sgc" type="text" placeholder="V1.0"/>
    </div>
  </div>
  <div class="row">
    <div>
      <label>Cantidad</label>
      <input id="qty" type="number" min="1" max="1000" value="1"/>
    </div>
    <div>
      <label>Total lote</label>
      <input id="total" type="number" min="1" max="10000" value="1"/>
    </div>
    <div>
      <label>Número inicio</label>
      <input id="start" type="number" min="1" max="10000" value="1"/>
    </div>
  </div>
</fieldset>

<fieldset>
  <legend>Impresora</legend>
  <div class="row">
    <div>
      <label>IP</label>
      <input id="p_ip" type="text" placeholder="10.10.2.46"/>
    </div>
    <div>
      <label>Puerto</label>
      <input id="p_port" type="number" min="1" max="65535" value="6101"/>
    </div>
  </div>
  <div class="row">
    <div>
      <label>Ajuste vertical (dots)</label>
      <input id="p_voff" type="number" min="-500" max="500" value="0"/>
    </div>
    <div>
      <label>Ajuste horizontal (dots)</label>
      <input id="p_hoff" type="number" min="-500" max="500" value="0"/>
    </div>
  </div>
  <div class="row">
    <button class="secondary" onclick="loadPrinterCfg()">Cargar config</button>
    <button class="secondary" onclick="savePrinterCfg()">Guardar config</button>
  </div>
  <div id="pcfg_msg" class="small"></div>
</fieldset>

<div class="row">
  <button class="primary" onclick="doPrint()">Imprimir</button>
</div>

<hr/>
<div id="log" class="small"></div>

<script>
let selected = null;

async function checkStatus() {{
  const r = await fetch('/api/health');
  const j = await r.json();
  const s = document.getElementById('status');
  s.innerHTML = `
    Odoo: <span class="${{j.odoo_ok ? 'success' : 'error'}}">${{j.odoo_ok ? 'OK' : 'ERROR'}}</span>
    <span class="badge">MySQL al imprimir</span>
  `;
}}
checkStatus();

function clearResults(){{
  document.getElementById('results').innerHTML = '';
  document.getElementById('selected').innerHTML = '';
  selected = null;
}}

async function doSearch(){{
  const q = document.getElementById('q').value.trim();
  if(!q) return;
  const res = await fetch('/api/search', {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify({{ query: q }})
  }});
  if(!res.ok) {{
    alert('Error buscando productos');
    return;
  }}
  const data = await res.json();
  const cont = document.getElementById('results');
  cont.innerHTML = '';
  data.results.forEach(p => {{
    const div = document.createElement('div');
    div.className = 'result-item';
    div.textContent = `ID: ${{p.id_producto}} — ${{p.nombre}}`;
    div.onclick = () => {{
      selected = p;
      document.getElementById('selected').innerHTML = 'Seleccionado: <code>' + p.id_producto + '</code> — ' + p.nombre;
    }};
    cont.appendChild(div);
  }});
  if(data.results.length === 0){{
    cont.innerHTML = '<div class="small">Sin resultados</div>';
  }}
}}

async function loadPrinterCfg(){{
  const r = await fetch('/api/printer-config');
  const j = await r.json();
  document.getElementById('p_ip').value = j.printer_ip || '10.10.2.46';
  document.getElementById('p_port').value = j.printer_port || 6101;
  document.getElementById('p_voff').value = j.vertical_offset_dots || 0;
  document.getElementById('p_hoff').value = j.horizontal_offset_dots || 0;
  document.getElementById('pcfg_msg').textContent = 'Config cargada';
}}

async function savePrinterCfg(){{
  const payload = {{
    printer_ip: document.getElementById('p_ip').value.trim(),
    printer_port: Number(document.getElementById('p_port').value),
    vertical_offset_dots: Number(document.getElementById('p_voff').value),
    horizontal_offset_dots: Number(document.getElementById('p_hoff').value)
  }};
  const r = await fetch('/api/printer-config', {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify(payload)
  }});
  const j = await r.json();
  document.getElementById('pcfg_msg').textContent = j.message || 'Guardado';
}}

async function doPrint(){{
  if(!selected){{
    alert('Selecciona un producto primero');
    return;
  }}
  const payload = {{
    producto: selected,
    op: document.getElementById('op').value.trim(),
    versionsgc: document.getElementById('sgc').value.trim(),
    cantidad: Number(document.getElementById('qty').value),
    totallote: Number(document.getElementById('total').value),
    numinicio: Number(document.getElementById('start').value),
    printer_ip: document.getElementById('p_ip').value.trim(),
    printer_port: Number(document.getElementById('p_port').value),
    vertical_offset_dots: Number(document.getElementById('p_voff').value),
    horizontal_offset_dots: Number(document.getElementById('p_hoff').value)
  }};
  const res = await fetch('/api/print', {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify(payload)
  }});
  const j = await res.json();
  const log = document.getElementById('log');
  if(res.ok){{
    log.innerHTML = '<span class="success">OK</span>: ' + (j.message || '');
  }} else {{
    log.innerHTML = '<span class="error">ERROR</span>: ' + (j.detail || JSON.stringify(j));
  }}
}}
</script>
</body>
</html>
    """)

# ---------- API ----------
@app.get("/api/health")
def health():
    global ODOO_OK, odoo_client
    # Intento perezoso de reintentar Odoo si no estaba.
    if not ODOO_OK:
        try:
            odoo_client = OdooClient()
            ODOO_OK = True
        except Exception as e:
            print(f"[WARN] Odoo sigue no disponible: {e}")
            ODOO_OK = False
    return {"odoo_ok": ODOO_OK}

@app.post("/api/search")
def api_search(payload: Dict[str, Any] = Body(...)):
    if not ODOO_OK or not odoo_client:
        raise HTTPException(status_code=503, detail="Odoo no disponible")
    query = (payload.get("query") or "").strip()
    if not query:
        return {"results": []}
    try:
        products = odoo_client.search_products(query)
        results = []
        for p in (products or []):
            code = p.get("default_code") or "N/A"
            name = p.get("name") or ""
            results.append({"id_producto": code, "nombre": name})
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en búsqueda: {e}")

@app.get("/api/printer-config")
def get_printer_config():
    return load_printer_cfg()

@app.post("/api/printer-config")
def set_printer_config(cfg: Dict[str, Any] = Body(...)):
    current = load_printer_cfg()
    current.update({
        "printer_ip": cfg.get("printer_ip", current["printer_ip"]),
        "printer_port": int(cfg.get("printer_port", current["printer_port"])),
        "vertical_offset_dots": int(cfg.get("vertical_offset_dots", current["vertical_offset_dots"])),
        "horizontal_offset_dots": int(cfg.get("horizontal_offset_dots", current["horizontal_offset_dots"])),
    })
    try:
        save_printer_cfg(current)
        return {"message": "Configuración de impresora guardada.", "config": current}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo guardar: {e}")

@app.post("/api/print")
def api_print(payload: Dict[str, Any] = Body(...)):
    """
    payload:
      producto: {{id_producto, nombre}}
      op, versionsgc, cantidad, totallote, numinicio
      printer_ip, printer_port, vertical_offset_dots, horizontal_offset_dots
    """
    prod = payload.get("producto") or {}
    id_producto = prod.get("id_producto") or "N/A"
    nombre_producto = prod.get("nombre") or "N/A"
    op = payload.get("op") or ""
    versionsgc = payload.get("versionsgc") or ""
    cantidad = int(payload.get("cantidad") or 1)
    totallote = int(payload.get("totallote") or 1)
    numinicio = int(payload.get("numinicio") or 1)

    if numinicio + cantidad - 1 > totallote:
        raise HTTPException(status_code=400, detail="El rango excede el total del lote.")

    # Config de impresora (se permite sobreescribir por payload)
    pcfg = load_printer_cfg()
    printer_ip = payload.get("printer_ip", pcfg["printer_ip"])
    printer_port = int(payload.get("printer_port", pcfg["printer_port"]))
    voff = int(payload.get("vertical_offset_dots", pcfg["vertical_offset_dots"]))
    hoff = int(payload.get("horizontal_offset_dots", pcfg["horizontal_offset_dots"]))

    # 1) Registrar en BD (si está habilitado)
    db_logged = False
    if os.getenv("ETIQUETAS_DISABLE_MYSQL", "0") != "1":
        try:
            mc = MysqlClient()
            connected = False
            try:
                connected = mc.connect()
            except Exception as ce:
                print(f"[ERROR] Conectando MySQL: {ce}")
                connected = False

            if connected:
                try:
                    db_logged = mc.insert_impresion(
                        id_producto=id_producto,
                        user=None,
                        nombre=nombre_producto,
                        op=op,
                        versionsgc=versionsgc,
                        cantidad=cantidad,
                        totallote=totallote,
                        numinicio=numinicio
                    )
                except Exception as ie:
                    print(f"[ERROR] insert_impresion excepción: {ie}")
                    db_logged = False
                finally:
                    try:
                        mc.close()
                    except Exception:
                        pass
            else:
                print("[WARN] MySQL no disponible (connect() False)")
        except Exception as e:
            print(f"[ERROR] Bloque general MySQL: {e}")
            # No levantamos error; continuamos a impresión

    # 2) Construir ZPLs con offsets (igual que tu app)
    def enc_latin1(s: str) -> str:
        return (s or "").encode("latin1", errors="replace").decode("latin1")

    nombre_print = enc_latin1(nombre_producto)
    op_print = enc_latin1(op)
    sgc_print = enc_latin1(versionsgc)
    fecha_print = datetime.now().strftime('%d/%m/%Y')

    # posiciones base
    def pos(x, y): return apply_offsets(x, y, hoff, voff)

    labels = []
    for i in range(numinicio, numinicio + cantidad):
        x1, y1 = pos(20, 5)       # nombre
        x2, y2 = pos(80, 37)      # barcode
        x3, y3 = pos(20, 145)     # OP
        x4, y4 = pos(20, 170)     # i/total
        x5, y5 = pos(200, 170)    # versión
        x6, y6 = pos(200, 145)    # fecha

        zpl = (
            "^XA\n"
            f"^FO{x1},{y1}^A0N,18,18^FD{nombre_print}^FS\n"
            f"^FO{x2},{y2}^BCN,75,Y,N,N^FD{id_producto}^FS\n"
            f"^FO{x3},{y3}^A0N,20,20^FD{op_print}^FS\n"
            f"^FO{x4},{y4}^A0N,18,18^FD{i}/{totallote}^FS\n"
            f"^FO{x5},{y5}^A0N,18,18^FD{sgc_print}^FS\n"
            f"^FO{x6},{y6}^A0N,18,18^FD{fecha_print}^FS\n"
            "^PQ1,1,1,Y^XZ"
        )
        labels.append(zpl)

    # 3) Enviar a impresora
    try:
        sent = zpl_send_batch(labels, printer_ip, printer_port, timeout=int(os.getenv("ETIQUETAS_PRINTER_TIMEOUT", "5")))
    except ConnectionRefusedError:
        raise HTTPException(status_code=503, detail=f"No se pudo conectar a la impresora en {printer_ip}:{printer_port}.")
    except socket.timeout:
        raise HTTPException(status_code=504, detail=f"Tiempo agotado al conectar con la impresora {printer_ip}:{printer_port}.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enviando a impresora: {e}")

    msg = f"Se enviaron {sent}/{len(labels)} etiquetas. " + ("" if db_logged else "(BD no registrada)")
    return {"ok": True, "message": msg}
