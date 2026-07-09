#!/usr/bin/env python3
"""Gerador de desenhos de engenharia (DXF/DWG) — diagramas unifilares, blocos, layouts"""
import sys, os, json, datetime
from pathlib import Path

try:
    import ezdxf
    from ezdxf.enums import TextEntityAlignment
except ImportError:
    print("❌ ezdxf necessário. Instale: pip install ezdxf")
    sys.exit(1)

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")

def carregar_estado():
    with open(STATE_FILE) as f:
        return json.load(f)

# ─── Diagrama Unifilar Simplificado ─────────────────────────────────────────

def gerar_unifilar_se(nome_arquivo, tensao="138kV", barramentos=2, equipamentos=None):
    """Gera diagrama unifilar de subestação simplificado"""
    doc = ezdxf.new("R2010")
    doc.units = 4
    msp = doc.modelspace()
    doc.layers.new("EQUIP", dxfattribs={"color": 3})
    doc.layers.new("TEXTO", dxfattribs={"color": 7})
    doc.layers.new("LINHA", dxfattribs={"color": 5})

    x0, y0 = 50, 150
    esp = 60

    # Barramento
    bx = x0 + 20
    doc.layers.new("BARRA", dxfattribs={"color": 2})
    msp.add_line((bx, y0 - 20), (bx + (barramentos-1)*esp + 40, y0 - 20), dxfattribs={"layer": "BARRA"})
    msp.add_text(f"Barra {tensao}", dxfattribs={"layer": "TEXTO", "height": 3}).set_placement((bx, y0 - 27), align=TextEntityAlignment.LEFT)

    # Equipamentos
    if equipamentos:
        for i, eq in enumerate(equipamentos):
            x = bx + 20 + i * esp
            y = y0
            msp.add_circle((x, y), 6, dxfattribs={"layer": "EQUIP"})
            msp.add_text(eq[:10], dxfattribs={"layer": "TEXTO", "height": 2.5}).set_placement((x, y - 12), align=TextEntityAlignment.CENTER)
            msp.add_line((x, y + 6), (x, y0 - 20), dxfattribs={"layer": "LINHA"})

    # Legenda
    leg_y = y0 - 50
    msp.add_text(f"Diagrama Unifilar - SE {tensao}", dxfattribs={"layer": "TEXTO", "height": 4}).set_placement((x0, leg_y), align=TextEntityAlignment.LEFT)
    msp.add_text(f"Gerado em: {datetime.date.today():%d/%m/%Y}", dxfattribs={"layer": "TEXTO", "height": 2.5}).set_placement((x0, leg_y - 8), align=TextEntityAlignment.LEFT)

    doc.saveas(nome_arquivo)
    return nome_arquivo

# ─── Diagrama de Blocos Telecom ─────────────────────────────────────────────

def gerar_bloco_telecom(nome_arquivo, title="Arquitetura Telecom - SE"):
    """Gera diagrama de blocos de telecomunicações"""
    doc = ezdxf.new("R2010")
    doc.units = 4
    msp = doc.modelspace()
    doc.layers.new("BLOCO", dxfattribs={"color": 4})
    doc.layers.new("TEXTO", dxfattribs={"color": 7})
    doc.layers.new("LIGACAO", dxfattribs={"color": 5})

    blocos = [
        ("SDH/DWDM", 30, 200),
        ("MPLS-TP", 130, 200),
        ("SCADA", 230, 200),
        ("Teleproteção", 30, 120),
        ("Rádio", 130, 120),
        ("NMS", 230, 120),
    ]

    for nome, x, y in blocos:
        msp.add_rectangle((x, y), 80, 40, dxfattribs={"layer": "BLOCO"})
        msp.add_text(nome, dxfattribs={"layer": "TEXTO", "height": 3}).set_placement((x + 40, y + 20), align=TextEntityAlignment.CENTER)

    # Ligações
    ligacoes = [
        (30+80, 200+20, 130, 200+20),
        (30+80, 200, 130, 200),
        (130+80, 200+20, 230, 200+20),
        (130+80, 200, 230, 200),
        (30+40, 120+40, 30+40, 200),
        (130+40, 120+40, 130+40, 200),
        (230+40, 120+40, 230+40, 200),
    ]
    for x1, y1, x2, y2 in ligacoes:
        msp.add_line((x1, y1), (x2, y2), dxfattribs={"layer": "LIGACAO"})

    msp.add_text(title, dxfattribs={"layer": "TEXTO", "height": 4}).set_placement((30, 260), align=TextEntityAlignment.LEFT)

    doc.saveas(nome_arquivo)
    return nome_arquivo

# ─── Layout de Rack ─────────────────────────────────────────────────────────

def gerar_layout_rack(nome_arquivo, rack_id="RACK-001", altura_u=44):
    """Gera layout frontal de rack telecom"""
    doc = ezdxf.new("R2010")
    doc.units = 4
    msp = doc.modelspace()
    doc.layers.new("RACK", dxfattribs={"color": 7})
    doc.layers.new("EQUIP", dxfattribs={"color": 3})
    doc.layers.new("TEXTO", dxfattribs={"color": 7})

    x0, y0 = 50, 50
    larg = 60
    alt_u = 12  # mm por U

    # Contorno rack
    msp.add_rectangle((x0, y0), larg, altura_u * alt_u, dxfattribs={"layer": "RACK"})

    # Réguas U
    for u in range(altura_u + 1):
        y = y0 + u * alt_u
        msp.add_line((x0, y), (x0 + larg, y), dxfattribs={"layer": "RACK"})

    # Numeração U
    for u in range(altura_u):
        msp.add_text(str(altura_u - u), dxfattribs={"layer": "TEXTO", "height": 2}).set_placement((x0 - 8, y0 + u * alt_u + 3), align=TextEntityAlignment.MIDDLE_RIGHT)

    msp.add_text(rack_id, dxfattribs={"layer": "TEXTO", "height": 4}).set_placement((x0, y0 + altura_u * alt_u + 5), align=TextEntityAlignment.LEFT)

    doc.saveas(nome_arquivo)
    return nome_arquivo

# ─── Diagrama de Fibra Óptica ───────────────────────────────────────────────

def gerar_diagrama_fibra(nome_arquivo, title="Rede de Fibra Óptica"):
    """Gera diagrama de rede de fibra óptica"""
    doc = ezdxf.new("R2010")
    doc.units = 4
    msp = doc.modelspace()
    doc.layers.new("FIBRA", dxfattribs={"color": 2})
    doc.layers.new("NOH", dxfattribs={"color": 4})
    doc.layers.new("TEXTO", dxfattribs={"color": 7})

    nos = [
        ("SE-Alfa", 50, 180),
        ("SE-Beta", 200, 200),
        ("SE-Gama", 200, 100),
        ("Centro-Ops", 350, 150),
    ]

    for nome, x, y in nos:
        msp.add_circle((x, y), 15, dxfattribs={"layer": "NOH"})
        msp.add_text(nome, dxfattribs={"layer": "TEXTO", "height": 2.5}).set_placement((x, y - 22), align=TextEntityAlignment.CENTER)

    # Rotas
    rotas = [
        (50, 180, 200, 200, "48F SM G.652D"),
        (50, 180, 200, 100, "24F SM G.655"),
        (200, 200, 350, 150, "96F SM G.652D"),
        (200, 100, 350, 150, "48F SM G.655"),
    ]
    for x1, y1, x2, y2, desc in rotas:
        msp.add_line((x1, y1), (x2, y2), dxfattribs={"layer": "FIBRA"})
        mx, my = (x1+x2)/2, (y1+y2)/2
        msp.add_text(desc, dxfattribs={"layer": "TEXTO", "height": 2}).set_placement((mx, my + 5), align=TextEntityAlignment.CENTER)

    msp.add_text(title, dxfattribs={"layer": "TEXTO", "height": 4}).set_placement((50, 230), align=TextEntityAlignment.LEFT)

    doc.saveas(nome_arquivo)
    return nome_arquivo

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    out = sys.argv[2] if len(sys.argv) > 2 else ""

    if cmd == "unifilar":
        path = out or f"/tmp/opencode/diagrama_unifilar.dxf"
        gerar_unifilar_se(path)
        print(f"✅ Unifilar gerado: {path}")

    elif cmd == "telecom":
        path = out or f"/tmp/opencode/diagrama_telecom.dxf"
        gerar_bloco_telecom(path)
        print(f"✅ Diagrama telecom gerado: {path}")

    elif cmd == "rack":
        rack_id = sys.argv[3] if len(sys.argv) > 3 else "RACK-001"
        path = out or f"/tmp/opencode/layout_{rack_id}.dxf"
        gerar_layout_rack(path, rack_id)
        print(f"✅ Layout rack gerado: {path}")

    elif cmd == "fibra":
        path = out or f"/tmp/opencode/diagrama_fibra.dxf"
        gerar_diagrama_fibra(path)
        print(f"✅ Diagrama fibra gerado: {path}")

    elif cmd == "a3":
        sys.path.insert(0, os.path.expanduser("~/.config/opencode/scripts"))
        from a3_template_gen import generate_a3_template
        path = out or f"/tmp/opencode/template_a3.dxf"
        generate_a3_template(path)
        print(f"✅ Template A3 gerado: {path}")

    else:
        print("""Uso: gen_dwg.py <comando> [arquivo.dxf] [params]

Comandos:
  unifilar             Diagrama unifilar de SE
  telecom              Diagrama de blocos telecom
  rack <id>            Layout frontal de rack
  fibra                Diagrama de rede de fibra óptica
  a3                   Template A3 NBR 16752
""")
