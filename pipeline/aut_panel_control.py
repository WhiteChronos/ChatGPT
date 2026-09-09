#!/usr/bin/env python3
"""AUT Panel Control.

Valida o modelo canônico, aplica as Regras de Ouro dimensionais, gera
Data Sheet, Data Center SQLite, layout SVG proporcional, relatório de QA
e manifesto SHA-256 para uso no GitHub Actions.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import sqlite3
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from jsonschema import Draft202012Validator

APROVADO = "APROVADO"
CONDICIONADO = "CONDICIONADO"
HOLD = "HOLD"
REPROVADO = "REPROVADO"


@dataclass(frozen=True)
class Resultado:
    regra: str
    resultado: str
    severidade: str
    mensagem: str
    evidencia: dict[str, Any]


@dataclass(frozen=True)
class Retangulo:
    instancia: str
    superficie: str
    x: float
    y: float
    largura: float
    altura: float

    @property
    def direita(self) -> float:
        return self.x + self.largura

    @property
    def topo(self) -> float:
        return self.y + self.altura


def agora_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def carregar_json(caminho: Path) -> dict[str, Any]:
    with caminho.open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    if not isinstance(dados, dict):
        raise ValueError(f"A raiz JSON deve ser um objeto: {caminho}")
    return dados


def salvar_json(caminho: Path, dados: Mapping[str, Any]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256(caminho: Path) -> str:
    resumo = hashlib.sha256()
    with caminho.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            resumo.update(bloco)
    return resumo.hexdigest()


def obter(dados: Mapping[str, Any], caminho: str, padrao: Any = None) -> Any:
    atual: Any = dados
    for parte in caminho.split("."):
        if not isinstance(atual, Mapping) or parte not in atual:
            return padrao
        atual = atual[parte]
    return atual


def indice_catalogo(catalogo: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {str(item["catalog_id"]): item for item in catalogo.get("components", [])}


def dimensoes(item: Mapping[str, Any], rotacao: int = 0) -> tuple[float, float, float] | None:
    bruto = item.get("dimensions_mm")
    if not isinstance(bruto, Mapping):
        return None
    valores = (bruto.get("width"), bruto.get("height"), bruto.get("depth"))
    if not all(isinstance(v, (int, float)) and v > 0 for v in valores):
        return None
    largura, altura, profundidade = map(float, valores)
    if rotacao % 180 == 90:
        largura, altura = altura, largura
    return largura, altura, profundidade


def expandir(ret: Retangulo, item: Mapping[str, Any]) -> Retangulo:
    folga = item.get("clearance_mm") or {}
    esquerda = float(folga.get("left", 0) or 0)
    direita = float(folga.get("right", 0) or 0)
    inferior = float(folga.get("bottom", 0) or 0)
    superior = float(folga.get("top", 0) or 0)
    return Retangulo(
        ret.instancia,
        ret.superficie,
        ret.x - esquerda,
        ret.y - inferior,
        ret.largura + esquerda + direita,
        ret.altura + inferior + superior,
    )


def sobrepoe(a: Retangulo, b: Retangulo) -> bool:
    return not (a.direita <= b.x or b.direita <= a.x or a.topo <= b.y or b.topo <= a.y)


def regra_vista(regra: str, nome: str, atual: Mapping[str, Any], largura: float, altura: float) -> Resultado:
    ok = atual.get("width") == largura and atual.get("height") == altura
    return Resultado(
        regra,
        "PASS" if ok else "FAIL",
        "INFO" if ok else REPROVADO,
        f"{nome}: {atual.get('width')} x {atual.get('height')} mm; esperado {largura} x {altura} mm.",
        {"atual": atual, "esperado": {"width": largura, "height": altura}},
    )


def status_final(resultados: Iterable[Resultado]) -> str:
    resultados = list(resultados)
    if any(r.resultado == "FAIL" and r.severidade == REPROVADO for r in resultados):
        return REPROVADO
    if any(r.resultado in {"FAIL", "HOLD"} and r.severidade == HOLD for r in resultados):
        return HOLD
    if any(r.resultado == "FAIL" and r.severidade == "WARNING" for r in resultados):
        return CONDICIONADO
    return APROVADO


def validar_schema(instancia: Mapping[str, Any], esquema: Mapping[str, Any]) -> list[Resultado]:
    saida: list[Resultado] = []
    for erro in sorted(Draft202012Validator(esquema).iter_errors(instancia), key=lambda e: list(e.absolute_path)):
        local = ".".join(map(str, erro.absolute_path)) or "$"
        saida.append(Resultado("QA-SCHEMA", "FAIL", REPROVADO, f"{local}: {erro.message}", {"json_path": local}))
    return saida


def avaliar(projeto: Mapping[str, Any], catalogo: Mapping[str, Any]) -> list[Resultado]:
    r: list[Resultado] = []
    indice = indice_catalogo(catalogo)
    externo = obter(projeto, "enclosure.external_mm", {})
    placa = obter(projeto, "enclosure.mounting_plate_mm", {})
    largura = externo.get("width")
    altura = externo.get("height")
    profundidade = externo.get("depth")
    largura_placa = placa.get("width")
    altura_placa = placa.get("height")

    r.append(regra_vista("GR-021", "Vista frontal externa", obter(projeto, "views.front_external_mm", {}), largura, altura))
    r.append(regra_vista("GR-022", "Vista interna frontal", obter(projeto, "views.front_internal_mm", {}), largura, altura))
    r.append(regra_vista("GR-023", "Vista lateral", obter(projeto, "views.side_external_mm", {}), profundidade, altura))

    render = projeto.get("render") or {}
    escala_ok = (
        isinstance(render.get("px_per_mm"), (int, float))
        and render.get("px_per_mm") > 0
        and render.get("single_global_scale") is True
        and "per_view_scale" not in render
    )
    r.append(Resultado("GR-024", "PASS" if escala_ok else "FAIL", "INFO" if escala_ok else REPROVADO,
                       "Escala global única validada." if escala_ok else "Escala global inválida ou escala por vista detectada.",
                       {"px_per_mm": render.get("px_per_mm"), "single_global_scale": render.get("single_global_scale")}))

    aspecto_ok = render.get("aspect_equal") is True and render.get("allow_component_scale_override") is False
    r.append(Resultado("GR-025", "PASS" if aspecto_ok else "FAIL", "INFO" if aspecto_ok else REPROVADO,
                       "Aspecto 1:1 e escala individual proibida." if aspecto_ok else "Aspecto não travado ou escala individual permitida.", {}))

    canvas_ok = render.get("canvas_policy") == "grow_only" and render.get("allow_stretch") is False
    r.append(Resultado("GR-026", "PASS" if canvas_ok else "HOLD", "INFO" if canvas_ok else HOLD,
                       "Canvas cresce sem compressão." if canvas_ok else "Canvas deve usar grow_only e allow_stretch=false.", {}))

    placa_ok = all(isinstance(v, (int, float)) and v > 0 for v in (largura, altura, largura_placa, altura_placa)) and largura_placa < largura and altura_placa < altura
    r.append(Resultado("GR-008", "PASS" if placa_ok else "FAIL", "INFO" if placa_ok else REPROVADO,
                       "Placa de montagem interna e menor que o gabinete." if placa_ok else "Placa deve ser menor que o contorno externo.", {}))

    id_gabinete = obter(projeto, "enclosure.catalog_id")
    gabinete = indice.get(str(id_gabinete))
    dimensao_gabinete = dimensoes(gabinete or {})
    gabinete_ok = gabinete is not None and gabinete.get("engineering_status") == "VALIDATED" and dimensao_gabinete == (float(largura), float(altura), float(profundidade))
    r.append(Resultado("GR-011", "PASS" if gabinete_ok else "HOLD", "INFO" if gabinete_ok else HOLD,
                       "Gabinete comercial validado." if gabinete_ok else "Gabinete comercial/código exato ainda pendente.",
                       {"catalog_id": id_gabinete, "dimensions_match": gabinete_ok}))

    zona = obter(projeto, "layout.bottom_zone", {})
    necessario = sum(float(zona.get(k, 0) or 0) for k in ("cable_exit_height_mm", "lower_wireway_height_mm", "minimum_bend_clearance_mm"))
    limite = zona.get("terminal_zone_bottom_y_mm")
    prensa = zona.get("cable_glands_count")
    inferior_ok = isinstance(limite, (int, float)) and limite >= necessario and isinstance(prensa, int) and prensa > 0
    r.append(Resultado("GR-027", "PASS" if inferior_ok else "HOLD", "INFO" if inferior_ok else HOLD,
                       "Bornes, canaleta, curvatura e prensa-cabos separados." if inferior_ok else "Zona inferior insuficiente.",
                       {"required_mm": necessario, "terminal_bottom_mm": limite, "cable_glands": prensa}))

    pendentes: list[str] = []
    sem_referencia: list[str] = []
    retangulos: list[tuple[Retangulo, Mapping[str, Any]]] = []
    for posicao in projeto.get("placements", []):
        instancia = str(posicao.get("instance_id"))
        item = indice.get(str(posicao.get("catalog_id")))
        if item is None or item.get("engineering_status") != "VALIDATED":
            pendentes.append(instancia)
        if item and item.get("engineering_status") == "VALIDATED" and not item.get("references"):
            sem_referencia.append(instancia)
        dim = dimensoes(item or {}, int(posicao.get("rotation_deg", 0) or 0))
        if dim:
            retangulos.append((Retangulo(instancia, str(posicao.get("surface")), float(posicao.get("x_mm", 0)), float(posicao.get("y_mm", 0)), dim[0], dim[1]), item or {}))

    evid_ok = not pendentes and not sem_referencia
    r.append(Resultado("GR-001", "PASS" if evid_ok else "HOLD", "INFO" if evid_ok else HOLD,
                       "Componentes e evidências completos." if evid_ok else "Há componente/modelo/evidência pendente.",
                       {"pending_instances": sorted(set(pendentes)), "missing_references": sorted(set(sem_referencia))}))

    erros_geometria: list[str] = []
    for ret, item in retangulos:
        efetivo = expandir(ret, item)
        if ret.superficie == "mounting_plate":
            max_l, max_a = largura_placa, altura_placa
        elif ret.superficie == "door":
            max_l, max_a = largura, altura
        else:
            erros_geometria.append(f"{ret.instancia}: superfície inválida")
            continue
        if efetivo.x < 0 or efetivo.y < 0 or efetivo.direita > max_l or efetivo.topo > max_a:
            erros_geometria.append(f"{ret.instancia}: envelope/folga fora de {ret.superficie}")
    for i, (a, item_a) in enumerate(retangulos):
        for b, item_b in retangulos[i + 1:]:
            if a.superficie == b.superficie and sobrepoe(expandir(a, item_a), expandir(b, item_b)):
                erros_geometria.append(f"Colisão: {a.instancia} x {b.instancia}")
    geometria_ok = not erros_geometria
    r.append(Resultado("GR-018", "PASS" if geometria_ok else "FAIL", "INFO" if geometria_ok else REPROVADO,
                       "Layout sem colisões e dentro dos limites." if geometria_ok else "Colisão, keep-out ou limite violado.",
                       {"errors": erros_geometria}))

    area_placa = float(largura_placa or 0) * float(altura_placa or 0)
    area_componentes = sum(ret.largura * ret.altura for ret, _ in retangulos if ret.superficie == "mounting_plate")
    area_fixa = float(obter(projeto, "layout.fixed_occupied_area_mm2", 0) or 0)
    reserva = 100.0 if area_placa <= 0 else max(0.0, 100 * (area_placa - area_componentes - area_fixa) / area_placa)
    meta = float(obter(projeto, "enclosure.minimum_free_reserve_percent", 0) or 0)
    reserva_ok = reserva >= meta
    r.append(Resultado("GR-010", "PASS" if reserva_ok else "HOLD", "INFO" if reserva_ok else HOLD,
                       f"Reserva preliminar {reserva:.2f}% (meta {meta:.2f}%).", {"free_percent": round(reserva, 3)}))

    arquitetura = projeto.get("architecture") or {}
    if arquitetura.get("controller_type") == "RTU":
        controlador = indice.get(str(arquitetura.get("controller_catalog_id")))
        modulos = [indice.get(str(x)) for x in arquitetura.get("io_catalog_ids", [])]
        completos = controlador is not None and all(modulos)
        validados = completos and controlador.get("engineering_status") == "VALIDATED" and all(m.get("engineering_status") == "VALIDATED" for m in modulos)
        grupo = controlador.get("compatibility_group") if controlador else None
        compativeis = completos and all(m.get("compatibility_group") == grupo or controlador.get("catalog_id") in m.get("compatible_controllers", []) for m in modulos)
        utr_ok = bool(validados and compativeis)
        r.append(Resultado("GR-013", "PASS" if utr_ok else "HOLD", "INFO" if utr_ok else HOLD,
                           "UTR e cartões validados e compatíveis." if utr_ok else "UTR/cartões ou compatibilidade pendentes.",
                           {"validated": bool(validados), "compatible": bool(compativeis)}))

    lifecycle = [item.get("catalog_id") for item in indice.values() if item.get("engineering_status") == "VALIDATED" and item.get("lifecycle_status") not in {"ACTIVE", "VALIDATED_FOR_PROJECT"}]
    r.append(Resultado("GR-015", "PASS" if not lifecycle else "HOLD", "INFO" if not lifecycle else HOLD,
                       "Lifecycle e canal oficial confirmados." if not lifecycle else "Reverificação comercial pendente.", {"catalog_ids": lifecycle}))
    return r


def proveniencia_github() -> dict[str, Any]:
    chaves = ["GITHUB_REPOSITORY", "GITHUB_SHA", "GITHUB_REF", "GITHUB_WORKFLOW", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_ACTOR"]
    return {chave.lower(): os.getenv(chave) for chave in chaves}


def gerar_datasheet(projeto: Mapping[str, Any], catalogo: Mapping[str, Any], resultados: list[Resultado], hash_projeto: str, hash_catalogo: str) -> dict[str, Any]:
    indice = indice_catalogo(catalogo)
    instancias = []
    referencias: set[str] = set()
    for posicao in projeto.get("placements", []):
        item = indice.get(str(posicao.get("catalog_id")))
        instancias.append({"placement": posicao, "catalog_record": item})
        if item:
            referencias.update(ref["reference_id"] for ref in item.get("references", []) if ref.get("reference_id"))
    return {
        "schema_version": "1.0",
        "generated_at": agora_utc(),
        "project": projeto.get("project"),
        "enclosure": projeto.get("enclosure"),
        "render_contract": projeto.get("render"),
        "views": projeto.get("views"),
        "layout": projeto.get("layout"),
        "architecture": projeto.get("architecture"),
        "component_instances": instancias,
        "reference_ids": sorted(referencias),
        "quality": {"status": status_final(resultados), "rules": [asdict(x) for x in resultados]},
        "provenance": {"project_sha256": hash_projeto, "catalog_sha256": hash_catalogo, "github": proveniencia_github()},
    }


def gerar_relatorio(saida: Path, projeto: Mapping[str, Any], resultados: list[Resultado]) -> tuple[Path, Path]:
    estado = status_final(resultados)
    dados = {"generated_at": agora_utc(), "project_id": obter(projeto, "project.id"), "status": estado, "github": proveniencia_github(), "rules": [asdict(x) for x in resultados]}
    json_path = saida / "qa_report.json"
    salvar_json(json_path, dados)
    linhas = [f"# AUT Panel Quality — {estado}", "", f"Projeto: `{obter(projeto, 'project.id')}`", "", "| Regra | Resultado | Severidade | Mensagem |", "|---|---|---|---|"]
    for x in resultados:
        linhas.append(f"| {x.regra} | {x.resultado} | {x.severidade} | {x.mensagem.replace('|', '\\|')} |")
    md_path = saida / "qa_report.md"
    md_path.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return json_path, md_path


def gerar_sqlite(catalogo: Mapping[str, Any], caminho: Path) -> None:
    if caminho.exists():
        caminho.unlink()
    with sqlite3.connect(caminho) as banco:
        banco.executescript("""
        PRAGMA foreign_keys=ON;
        CREATE TABLE manufacturers(id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL);
        CREATE TABLE products(id INTEGER PRIMARY KEY, catalog_id TEXT UNIQUE NOT NULL, manufacturer_id INTEGER NOT NULL REFERENCES manufacturers(id), family TEXT, model TEXT NOT NULL, category TEXT NOT NULL, engineering_status TEXT NOT NULL, lifecycle_status TEXT NOT NULL, width_mm REAL, height_mm REAL, depth_mm REAL, compatibility_group TEXT);
        CREATE TABLE references_docs(id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL REFERENCES products(id), reference_id TEXT NOT NULL, document_type TEXT NOT NULL, title TEXT NOT NULL, document_code TEXT, revision TEXT, publication_date TEXT, page_section TEXT NOT NULL, source_tier TEXT NOT NULL, official_url TEXT, consultation_date TEXT NOT NULL, validation_status TEXT NOT NULL);
        CREATE TABLE supplier_channels(id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL REFERENCES products(id), company TEXT NOT NULL, authorized_status TEXT NOT NULL, region TEXT, site TEXT, product_page TEXT, support_channel TEXT, last_verified TEXT);
        """)
        fabricantes: dict[str, int] = {}
        for item in catalogo.get("components", []):
            nome = str(item.get("manufacturer"))
            if nome not in fabricantes:
                fabricantes[nome] = banco.execute("INSERT INTO manufacturers(name) VALUES(?)", (nome,)).lastrowid
            dim = item.get("dimensions_mm") or {}
            produto_id = banco.execute("INSERT INTO products(catalog_id,manufacturer_id,family,model,category,engineering_status,lifecycle_status,width_mm,height_mm,depth_mm,compatibility_group) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (item.get("catalog_id"), fabricantes[nome], item.get("family"), item.get("model"), item.get("category"), item.get("engineering_status"), item.get("lifecycle_status"), dim.get("width"), dim.get("height"), dim.get("depth"), item.get("compatibility_group"))).lastrowid
            for ref in item.get("references", []):
                banco.execute("INSERT INTO references_docs(product_id,reference_id,document_type,title,document_code,revision,publication_date,page_section,source_tier,official_url,consultation_date,validation_status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                    (produto_id, ref.get("reference_id"), ref.get("document_type"), ref.get("title"), ref.get("document_code"), ref.get("revision"), ref.get("publication_date"), ref.get("page_section"), ref.get("source_tier"), ref.get("official_url"), ref.get("consultation_date"), ref.get("validation_status")))
            for fornecedor in item.get("supplier_channels", []):
                banco.execute("INSERT INTO supplier_channels(product_id,company,authorized_status,region,site,product_page,support_channel,last_verified) VALUES(?,?,?,?,?,?,?,?)",
                    (produto_id, fornecedor.get("company"), fornecedor.get("authorized_status"), fornecedor.get("region"), fornecedor.get("site"), fornecedor.get("product_page"), fornecedor.get("support_channel"), fornecedor.get("last_verified")))


def gerar_svg(projeto: Mapping[str, Any], catalogo: Mapping[str, Any], caminho: Path) -> None:
    ext = obter(projeto, "enclosure.external_mm")
    placa = obter(projeto, "enclosure.mounting_plate_mm")
    largura, altura, profundidade = map(float, (ext["width"], ext["height"], ext["depth"]))
    placa_l, placa_a = map(float, (placa["width"], placa["height"]))
    escala = float(obter(projeto, "render.px_per_mm"))
    margem, intervalo, titulo = 30.0, 40.0, 30.0
    canvas_l = margem * 2 + largura + intervalo + max(largura, profundidade)
    canvas_a = margem * 2 + titulo + altura + intervalo + altura
    px_l, px_a = round(canvas_l * escala), round(canvas_a * escala)
    fx, fy = margem, margem + titulo
    dx, dy = margem + largura + intervalo, fy
    sx, sy = dx, fy + altura + intervalo
    px0, py0 = fx + (largura - placa_l) / 2, fy + (altura - placa_a) / 2
    indice = indice_catalogo(catalogo)
    e = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{px_l}px" height="{px_a}px" viewBox="0 0 {canvas_l} {canvas_a}">',
         '<style>text{font-family:Arial;fill:#111}.t{font-size:14px;font-weight:bold}.l{font-size:8px}.f{fill:none;stroke:#001f4d;stroke-width:1.4}.p{fill:#f7f7f7;stroke:#666}.c{fill:#e6e6e6;stroke:#111}.h{fill:#fff3cd;stroke:#856404}</style>',
         f'<text class="t" x="{margem}" y="{margem}">PAINEL DE AUTOMAÇÃO E CONTROLE — AUT</text>',
         f'<g id="front-internal" data-width-mm="{largura}" data-height-mm="{altura}"><rect class="f" x="{fx}" y="{fy}" width="{largura}" height="{altura}"/><text class="l" x="{fx}" y="{fy-6}">VISTA INTERNA {largura:.0f} x {altura:.0f} mm</text><rect class="p" x="{px0}" y="{py0}" width="{placa_l}" height="{placa_a}"/></g>',
         f'<g id="front-external" data-width-mm="{largura}" data-height-mm="{altura}"><rect class="f" x="{dx}" y="{dy}" width="{largura}" height="{altura}"/><text class="l" x="{dx}" y="{dy-6}">VISTA FRONTAL EXTERNA {largura:.0f} x {altura:.0f} mm</text></g>',
         f'<g id="side-external" data-width-mm="{profundidade}" data-height-mm="{altura}"><rect class="f" x="{sx}" y="{sy}" width="{profundidade}" height="{altura}"/><text class="l" x="{sx}" y="{sy-6}">VISTA LATERAL {profundidade:.0f} x {altura:.0f} mm</text></g>']
    for pos in projeto.get("placements", []):
        item = indice.get(str(pos.get("catalog_id")))
        dim = dimensoes(item or {}, int(pos.get("rotation_deg", 0) or 0))
        if not dim:
            continue
        if pos.get("surface") == "mounting_plate":
            x = px0 + float(pos["x_mm"]); y = py0 + placa_a - float(pos["y_mm"]) - dim[1]
        else:
            x = dx + float(pos["x_mm"]); y = dy + altura - float(pos["y_mm"]) - dim[1]
        classe = "c" if item.get("engineering_status") == "VALIDATED" else "h"
        rotulo = html.escape(f"{pos['instance_id']} — {item.get('model')}")
        e += [f'<rect class="{classe}" x="{x}" y="{y}" width="{dim[0]}" height="{dim[1]}"/>', f'<text class="l" x="{x+2}" y="{y+10}">{rotulo}</text>']
    e.append('</svg>')
    caminho.write_text("\n".join(e) + "\n", encoding="utf-8")


def manifesto(saida: Path, entradas: list[Path], artefatos: list[Path], estado: str) -> Path:
    dados = {"generated_at": agora_utc(), "status": estado, "github": proveniencia_github(), "inputs": [{"path": str(x), "sha256": sha256(x)} for x in entradas], "outputs": [{"path": x.name, "sha256": sha256(x)} for x in artefatos]}
    caminho = saida / "manifest.json"; salvar_json(caminho, dados); return caminho


def verificar_manifesto(caminho: Path, saida: Path) -> None:
    dados = carregar_json(caminho)
    erros = []
    for item in dados.get("outputs", []):
        arquivo = saida / item["path"]
        if not arquivo.exists() or sha256(arquivo) != item["sha256"]:
            erros.append(str(arquivo))
    if erros:
        raise RuntimeError("Artefatos inválidos: " + ", ".join(erros))


def executar(args: argparse.Namespace) -> int:
    projeto_path, catalogo_path = Path(args.project), Path(args.catalog)
    projeto, catalogo = carregar_json(projeto_path), carregar_json(catalogo_path)
    resultados = validar_schema(projeto, carregar_json(Path(args.schema))) + avaliar(projeto, catalogo)
    saida = Path(args.output_dir); saida.mkdir(parents=True, exist_ok=True)
    qa_json, qa_md = gerar_relatorio(saida, projeto, resultados)
    ds = gerar_datasheet(projeto, catalogo, resultados, sha256(projeto_path), sha256(catalogo_path))
    ds_path = saida / "AUT_PANEL_DATASHEET.json"; salvar_json(ds_path, ds)
    db_path = saida / "AUT_PANEL_DATACENTER.sqlite3"; gerar_sqlite(catalogo, db_path)
    svg_path = saida / "AUT_PANEL_LAYOUT.svg"; gerar_svg(projeto, catalogo, svg_path)
    estado = status_final(resultados)
    man = manifesto(saida, [projeto_path, catalogo_path, Path(args.pipeline)], [qa_json, qa_md, ds_path, db_path, svg_path], estado)
    verificar_manifesto(man, saida)
    print(json.dumps({"status": estado, "manifest": str(man)}, ensure_ascii=False))
    if estado == REPROVADO: return 1
    if estado == HOLD and not args.allow_hold: return 2
    return 0


def principal() -> int:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("pipeline")
    for flag in ("project", "catalog", "pipeline", "schema", "output-dir"):
        run.add_argument("--" + flag, required=True)
    run.add_argument("--allow-hold", action="store_true")
    run.set_defaults(func=executar)
    ver = sub.add_parser("verify-artifacts"); ver.add_argument("--manifest", required=True); ver.add_argument("--output-dir", required=True)
    ver.set_defaults(func=lambda a: (verificar_manifesto(Path(a.manifest), Path(a.output_dir)) or 0))
    try:
        args = p.parse_args()
        return int(args.func(args))
    except (OSError, ValueError, RuntimeError, sqlite3.Error, json.JSONDecodeError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr); return 3


if __name__ == "__main__":
    raise SystemExit(principal())
