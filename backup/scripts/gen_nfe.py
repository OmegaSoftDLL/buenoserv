#!/usr/bin/env python3
"""Gerador de NF-e (nota fiscal eletrônica) — estrutura para integração SEFAZ"""
import json, os, sys, datetime

STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")

def carregar():
    with open(STATE_FILE) as f:
        return json.load(f)

def gerar_xml_nfe(cliente, cpf_cnpj, valor, descricao, saida=None):
    """Gera estrutura XML da NF-e (modelo de dados para integração SEFAZ)"""
    import xml.etree.ElementTree as ET
    from xml.dom import minidom

    nfe = ET.Element("NFe", xmlns="http://www.portalfiscal.inf.br/nfe")
    infNFe = ET.SubElement(nfe, "infNFe", versao="4.00", Id=f"NFe{datetime.date.today():%Y%m}00000001")

    ide = ET.SubElement(infNFe, "ide")
    ET.SubElement(ide, "cUF").text = "35"  # SP
    ET.SubElement(ide, "cNF").text = "00000001"
    ET.SubElement(ide, "natOp").text = "PRESTACAO DE SERVICO"
    ET.SubElement(ide, "mod").text = "55"
    ET.SubElement(ide, "serie").text = "1"
    ET.SubElement(ide, "nNF").text = "1"
    ET.SubElement(ide, "dhEmi").text = datetime.datetime.now().isoformat()
    ET.SubElement(ide, "tpNF").text = "1"
    ET.SubElement(ide, "cMunFG").text = "3526700"  # Leme-SP

    emit = ET.SubElement(infNFe, "emit")
    ET.SubElement(emit, "CNPJ").text = "60490193000138"
    ET.SubElement(emit, "xNome").text = "BUENOSERV SERVICOS DE ENGENHARIA LTDA"
    ET.SubElement(emit, "xFant").text = "BUENOSERV"
    enderEmit = ET.SubElement(emit, "enderEmit")
    ET.SubElement(enderEmit, "xLgr").text = "Rua Giacomo Fior"
    ET.SubElement(enderEmit, "nro").text = "427"
    ET.SubElement(enderEmit, "xBairro").text = "Centro"
    ET.SubElement(enderEmit, "cMun").text = "3526700"
    ET.SubElement(enderEmit, "xMun").text = "Leme"
    ET.SubElement(enderEmit, "UF").text = "SP"
    ET.SubElement(enderEmit, "CEP").text = "13610000"
    ET.SubElement(enderEmit, "cPais").text = "1058"
    ET.SubElement(enderEmit, "xPais").text = "BRASIL"
    ET.SubElement(emit, "IE").text = "ISENTO"  # Simples Nacional
    ET.SubElement(emit, "CRT").text = "1"  # Simples Nacional

    dest = ET.SubElement(infNFe, "dest")
    if len(cpf_cnpj) > 11:
        ET.SubElement(dest, "CNPJ").text = cpf_cnpj.replace(".","").replace("/","").replace("-","")
    else:
        ET.SubElement(dest, "CPF").text = cpf_cnpj.replace(".","").replace("-","")
    ET.SubElement(dest, "xNome").text = cliente
    ET.SubElement(dest, "indIEDest").text = "9"

    det = ET.SubElement(infNFe, "det", nItem="1")
    prod = ET.SubElement(det, "prod")
    ET.SubElement(prod, "cProd").text = "0001"
    ET.SubElement(prod, "xProd").text = descricao[:120]
    ET.SubElement(prod, "NCM").text = "49111090"
    ET.SubElement(prod, "CFOP").text = "5933"
    ET.SubElement(prod, "uCom").text = "UND"
    ET.SubElement(prod, "qCom").text = "1"
    ET.SubElement(prod, "vUnCom").text = f"{valor:.2f}"
    ET.SubElement(prod, "vProd").text = f"{valor:.2f}"

    imposto = ET.SubElement(det, "imposto")
    # Simples Nacional - ISS
    issqn = ET.SubElement(imposto, "ISSQN")
    ET.SubElement(issqn, "vBC").text = f"{valor:.2f}"
    ET.SubElement(issqn, "vISS").text = f"{valor * 0.05:.2f}"
    ET.SubElement(issqn, "cMunFG").text = "3526700"
    ET.SubElement(issqn, "cListServ").text = "17.02"

    total = ET.SubElement(infNFe, "total")
    ICMSTot = ET.SubElement(total, "ICMSTot")
    ET.SubElement(ICMSTot, "vProd").text = f"{valor:.2f}"
    ET.SubElement(ICMSTot, "vNF").text = f"{valor:.2f}"

    pag = ET.SubElement(infNFe, "pag")
    detPag = ET.SubElement(pag, "detPag")
    ET.SubElement(detPag, "indPag").text = "0"
    ET.SubElement(detPag, "tPag").text = "01"
    ET.SubElement(detPag, "vPag").text = f"{valor:.2f}"

    # Pretty print
    rough = ET.tostring(nfe, encoding="unicode")
    xml_str = minidom.parseString(rough.encode()).toprettyxml(indent="  ")

    saida = saida or os.path.expanduser(f"~/Desktop/NFE_{cliente.replace(' ','_')}.xml")
    with open(saida, 'w') as f:
        f.write(xml_str)
    print(f"✅ XML NF-e gerado: {saida}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: gen_nfe.py <cliente> <cpf_cnpj> <valor> [descricao]")
        sys.exit(1)
    desc = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else "Servicos de engenharia"
    gerar_xml_nfe(sys.argv[1], sys.argv[2], float(sys.argv[3]), desc)
