# Manual do Adaptador de Template (template-adapter)

## Ferramentas de Leitura DWG/DXF

| Formato | Biblioteca | Limitações |
|---------|-----------|------------|
| DXF (R12-R2018) | ezdxf (nativo) | Completo |
| DWG (R14-R2018) | ezdwg (read-only) | Entidades básicas (LINE, ARC, LWPOLYLINE, TEXT, MTEXT, DIMENSION) |
| DWG (R2000-2018) | ODA File Converter + ezdxf | Conversão para DXF, requer ODA instalado |

## Mapeamento de Cores ACI para RGB

| ACI | Cor | RGB |
|-----|-----|-----|
| 1 | Red | (255,0,0) |
| 2 | Yellow | (255,255,0) |
| 3 | Green | (0,255,0) |
| 4 | Cyan | (0,255,255) |
| 5 | Blue | (0,0,255) |
| 6 | Magenta | (255,0,255) |
| 7 | White/Black | (255,255,255) |
| 8 | Dark Gray | (128,128,128) |
| 9 | Light Gray | (192,192,192) |
| 10-249 | Variável | Tabela ACI |

## Convenções de Nomes de Blocos de Carimbo

| Nome Comum | Provável função |
|------------|----------------|
| CARIMBO | Carimbo/legenda padrão |
| LEGENDA | Legenda/carimbo |
| TITLE_BLOCK | Title block (padrão internacional) |
| STAMP | Carimbo genérico |
| PRANCHA | Bloco de prancha |
| ABNT_CARIMBO | Carimbo conforme NBR |

## Atributos Típicos de Carimbo

| TAG | Campo esperado |
|-----|----------------|
| PROJETO | Nome do projeto |
| CLIENTE | Contratante |
| PRANCHA | Número da prancha |
| REV | Revisão |
| ESCALA | Escala do desenho |
| DATA | Data |
| AUTOR | Autor/projetista |
| VERIF | Verificado por |
| APROV | Aprovado por |
| CONTEUDO | Conteúdo da prancha |

## Script de Extração Rápida

```python
import ezdxf, json

def extract_profile(path):
    doc = ezdxf.readfile(path)
    prof = {
        "header": {v: doc.header.get(v) for v in ["$ACADVER", "$INSUNITS", "$MEASUREMENT", "$TDCREATE", "$TDUPDATE", "$EXTMIN", "$EXTMAX"]},
        "layers": [{k: getattr(l.dxf, k, None) for k in ["name","color","linetype","lineweight"]} for l in doc.layers],
        "text_styles": [{k: getattr(s.dxf, k, None) for k in ["name","font","textsize","width","oblique"]} for s in doc.styles],
        "linetypes": [{k: getattr(lt.dxf, k, None) for k in ["name","description"}] for lt in doc.linetypes],
        "blocks": [{"name": b.name, "entities": len(b)} for b in doc.blocks],
        "layouts": [{"name": l.name, "width": l.dxf.get("plot_paper_width",0), "height": l.dxf.get("plot_paper_height",0)} for l in doc.layouts],
    }
    return prof

if __name__ == "__main__":
    import sys
    prof = extract_profile(sys.argv[1])
    json.dump(prof, open(sys.argv[2] if len(sys.argv)>2 else "template-profile.json", "w"), indent=2)
```
