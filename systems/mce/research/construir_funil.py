#!/usr/bin/env python3
"""Reproduz a triagem 151->100->10 com evidencias observadas no GitHub.

Nao consulta a rede. A relacao de 105 nomes foi transcrita dos resultados
observados do conector GitHub em 2026-10-28; 151 repositorios distintos
foram encontrados nas seis buscas. Seleciona uma amostra auditavel de 100,
incluindo tres alvos obrigatorios, e 10 finalistas de revisao aprofundada.
NAO afirma que os 100 passaram por analise de codigo nem que o top10 e global.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parent
MANDATORY=[
    'Azure-Samples/digitization-of-piping-and-instrument-diagrams',
    'S-Houston/digitised-pid-mlops',
    'ZzzJjt/Industrial-Control',
]
# Os 10 finalistas tiveram branch HEAD, README e estrutura verificados via GitHub.
# Pontos editoriais: precisao de dominio/30; maturidade/20;
# interface/20; licenca e permissao de reutilizacao/15; privacidade/15.
FINALISTS=[
  dict(repo='Azure-Samples/digitization-of-piping-and-instrument-diagrams',head='c51302e3ec34147c676ef6eedbdd7551ea908b05',license='MIT',role='P&ID asset adjacency / graph',integration='ADAPTADOR_JSON_TESTADO',points=[29,17,16,15,11],notes='Graph-construction design: o grafo de conectividade nao comprova causa/efeito; direcao de fluxo nao garantida.'),
  dict(repo='S-Houston/digitised-pid-mlops',head='f0165e6477be7d891ee2d2403a65e474f484cb17',license='NAO_IDENTIFICADA',role='OCR CSV; detecao de simbolos',integration='ADAPTADOR_CSV_TESTADO_SEM_COPIAR_CODIGO',points=[25,9,13,0,9],notes='README prova YOLO/EAST/Tesseract; caminho Windows absoluto no Streamlit; dependencia de pesos de modelo. Sem licenca identificada.'),
  dict(repo='ZzzJjt/Industrial-Control',head='df9751647f92ea91ff8f51e985f8dbb6e663f380',license='NAO_IDENTIFICADA',role='exemplos didaticos de interlock',integration='VALIDADOR_REFERENCIA_NAO_NORMATIVA',points=[18,5,10,0,13],notes='Exemplo tem sombreamento da variavel effect_list em validate_coverage, invalidando a verificacao. Sem licença identificada.'),
  dict(repo='process-intelligence-research/pyDEXPI',head='83e5a11c4af3635ad12290a4dbe310480eb6d7a3',license='AGPL-3.0',role='DEXPI 1.3 / parser Proteus XML / grafo NetworkX',integration='CONTRATO_FUTURO_OPCIONAL',points=[30,18,15,3,14],notes='Dependencia AGPL-3.0: nao incorporar fonte ao sistema sem analise de compatibilidade legal; DEXPI 1.3 diverge de exemplos 2.0.'),
  dict(repo='aws-solutions-library-samples/guidance-for-piping-and-instrumentation-diagrams-digitization-on-aws',head='d53733862d8de16798113424b8a43b5cb1b507e3',license='MIT-0',role='extracao OCR/linhas/grafo cloud',integration='REFERENCIA_ARQUITETURAL',points=[29,17,13,15,5],notes='Custo, nuvem e encaminhamento de dados industrials exigem consentimento e politica de seguranca.'),
  dict(repo='hkoziolek/DiagEx-Repro',head='7d0a03855b8a397bf7503765eba57f24cb11ad6d',license='Apache-2.0',role='benchmark P&ID->DEXPI e reprodutibilidade',integration='BENCHMARK_OFFLINE_PLANEJADO',points=[29,18,17,15,13],notes='Dataset de referencia e cassettes offline; modo live depende de API externa. Compatibilidade DEXPI precisa de versionamento.'),
  dict(repo='mgupta70/PIDQA',head='570facf635653c2cf67b7dd80c10cd30bac94b65',license='CC0-1.0',role='avaliacao QA sobre P&ID e consultas em grafo',integration='BENCHMARK_PLANEJADO',points=[25,16,12,15,13],notes='64 mil pares QA declarados no README. Direitos das fontes externas do dataset devem ser validados separadamente.'),
  dict(repo='Maria-Antony/PID-Digitization-using-Neo4j',head='962866eccfb02b1f36c54aaab157c6694d751864',license='MIT',role='grafo Neo4j, CV, visualizacao',integration='REFERENCIA_ARQUITETURAL',points=[28,12,15,15,5],notes='Uso de APIs externas (OpenAI/Roboflow) e Neo4j Aura: nao transmitir dados sem permissao.'),
  dict(repo='javvi51/eDOCr',head='1786f898e0278fcc4574ce84a23ca6bad0c170e7',license='MIT',role='OCR em desenhos mecanicos',integration='REFERENCIA_OCR',points=[21,13,12,15,12],notes='Foco em desenho mecanico nao P&ID; README recomenda avaliar edocr2. Pilha TF antiga.'),
  dict(repo='sad123-yx/PIDCon',head='9f1669862771df37e507ccf08635e4bacaa43832',license='NAO_IDENTIFICADA',role='benchmark de conectividade P&ID/GNN',integration='REFERENCIA_METRICAS_NAO_EXECUTADA',points=[28,12,10,0,13],notes='README informa dataset GNN e medidas GED/NCA; dados externos e licença não verificados.'),
]


def run():
    observed=[r.strip() for r in (ROOT/'observados-github.txt').read_text(encoding='utf-8').splitlines() if r.strip()]
    if len(observed)!=105 or len(set(observed))!=len(observed):
        raise ValueError('Lista de 105 resultados alterada: revisar origem manualmente.')
    sample=observed[:97]+MANDATORY
    assert len(sample)==100 and len(set(sample))==100
    index={x['repo']:x for x in FINALISTS}
    assert len(index)==10 and all(n in sample for n in index)
    rows=[]
    for i,name in enumerate(sample,1):
        audited=index.get(name)
        low=name.lower()
        potential_family='SIM' if any(fragment in low for fragment in ('/diagex-repro','/pid_reader','/automated-pnid-symbol-detection-and-labelling','/pid-digitizer-app')) else 'NAO_IDENTIFICADA'
        rows.append({
            'id':f'C{i:03d}','repo':name,'url':'https://github.com/'+name,
            'nivel_evidencia':'README+ARVORE+HEAD+LICENCA_API' if audited else 'BUSCA_GITHUB_APENAS',
            'status':'FINALISTA' if audited else 'TRIAGEM_PENDENTE',
            'familia_semelhante_possivel':potential_family,
            'licenca':audited['license'] if audited else 'NAO_VERIFICADA',
            'score_tecnico':sum(audited['points']) if audited else '',
            'parecer':'CANDIDATO_OBRIGATORIO' if name in MANDATORY else ('CURADORIA_TECNICA' if audited else 'NAO_AVALIADO')
        })
    with (ROOT/'candidatos_100.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    top=[]
    for i,x in enumerate(sorted(FINALISTS,key=lambda x:-sum(x['points'])),1):
        y=dict(x);y['rank_entre_10_finalistas']=i;y['score_editorial']=sum(x['points']);y['url']='https://github.com/'+x['repo'];y['candidato_obrigatorio']=x['repo'] in MANDATORY
        top.append(y)
    (ROOT/'top10_verificados.json').write_text(json.dumps({'captured_at':'2026-10-28',
     'source':'GitHub connector: repository search + API metadata/branches/trees + README/source extracts',
     'method':'151 distintos observados; 100 em amostra auditavel incluindo 3 alvos obrigatorios; 10 revisados em detalhe. Pontuacao editorial sobre 10, NAO torneio independente ou auditoria de todos os 100.',
     'weights':{'dominio':30,'maturidade':20,'interface':20,'licenca':15,'privacidade':15},
     'reviewed':top},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with (ROOT/'top10_verificados.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['rank','repo','score_editorial','licenca','integracao','link'])
        w.writeheader()
        for x in top:w.writerow({'rank':x['rank_entre_10_finalistas'],'repo':x['repo'],'score_editorial':x['score_editorial'],'licenca':x['license'],'integracao':x['integration'],'link':x['url']})
    print(json.dumps({'distinct_discovered':151,'sampled':len(rows),'detailed_review':len(top),'mandatory_included':len(MANDATORY),'top10':[(x['repo'],x['score_editorial']) for x in top]},ensure_ascii=False))

if __name__=='__main__':run()
