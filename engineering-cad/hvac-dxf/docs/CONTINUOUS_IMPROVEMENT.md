# Processo de Melhoria Contínua

## Objetivo
Melhorar precisão, velocidade, cobertura de fontes e confiabilidade sem permitir que regras ou geometria mudem silenciosamente.

## Ciclo

```text
DEFEITO / NOVA EVIDÊNCIA
        |
        v
[1] CAPTURAR
        |
        v
[2] CLASSIFICAR
        |
        v
[3] ANALISAR CAUSA RAIZ
        |
        v
[4] PROPOR MENOR MELHORIA REUTILIZÁVEL
        |
        v
[5] IMPLEMENTAR EM BRANCH
        |
        v
[6] TESTAR CASO FALHO + CASOS BONS
        |
        v
[7] REVISAR GATE HUMANO
        |
        v
[8] APROVAR / REJEITAR
        |
        v
[9] VERSIONAR E REGISTRAR
```

## Eventos que disparam melhoria
- erro dimensional;
- modelo identificado incorretamente;
- CAD simplificado quando existia fonte melhor;
- fonte superior encontrada;
- conversão destruiu geometria;
- unidade errada;
- layer/texto fora do padrão;
- fornecedor classificado incorretamente;
- usuário reportou defeito verificável;
- repetição de pesquisa improdutiva;
- nova revisão de fabricante.

## Classificação do defeito
- `IDENTITY`
- `SOURCE`
- `DIMENSION`
- `GEOMETRY`
- `CONVERSION`
- `DXF_STRUCTURE`
- `TEXT_STYLE`
- `LAYERING`
- `SUPPLIER`
- `QA`
- `WORKFLOW`

## Análise de causa raiz
Perguntar:
1. Qual evidência estava ausente?
2. Qual regra permitiu o erro?
3. O problema é específico do modelo ou generalizável?
4. Existe fonte de maior autoridade?
5. Um script pode detectar isso automaticamente?
6. Qual o menor ajuste que evita repetição sem criar falsos positivos?

## Tipos de melhoria
- nova regra de pesquisa;
- nova heurística de identificação;
- novo validador;
- novo teste;
- nova fonte confiável;
- novo parser/conversor;
- ajuste de manifesto;
- ajuste de layer/padrão;
- atualização de skill.

## Regressão obrigatória
Toda melhoria deve testar:
- o caso que falhou;
- pelo menos um caso anteriormente correto;
- um caso limítrofe quando aplicável.

## Gate humano obrigatório
Exigir revisão humana antes de alterar:
- hierarquia de fontes;
- critério de `CAD_FABRICANTE`;
- tolerância dimensional;
- regra de conversão de unidade;
- lógica de matching automático;
- política de aceitação geométrica;
- classificação de confiança.

## Registro
Usar `evolution_record.yaml`.

Nunca apagar o histórico. Marcar regras antigas como `superseded`.

## Métricas
Acompanhar:
- % de blocos CAD_FABRICANTE;
- % RECONSTRUCAO_FICHA;
- % BLOQUEADO;
- taxa de retrabalho;
- taxa de falha de QA;
- tempo até fechar identidade;
- fontes oficiais por objeto;
- conflitos projeto x fabricante;
- regressões detectadas;
- melhorias aprovadas/rejeitadas.

## Meta
A evolução deve aumentar evidência, reduzir ambiguidade e reduzir retrabalho — nunca apenas aumentar automação.
