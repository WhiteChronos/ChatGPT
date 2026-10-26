# Metodologia de Elaboração de Blocos Técnicos

## 1. Princípio
A geometria do bloco deve ser consequência de evidência técnica. A semelhança visual nunca substitui o desenho dimensional.

## 2. Método de identificação
Criar um registro técnico do objeto contendo:
- TAG;
- disciplina;
- função;
- família;
- fabricante;
- série;
- modelo exato;
- part number;
- revisão/variante;
- parâmetros discriminadores.

Confirmar a identidade com pelo menos dois parâmetros além do nome do modelo.

## 3. Método de pesquisa
Pesquisar nesta ordem:
1. fabricante;
2. página oficial;
3. catálogo oficial;
4. ficha técnica PDF;
5. manual de instalação/serviço;
6. desenho dimensional;
7. CAD/BIM oficial;
8. distribuidor autorizado;
9. base técnica secundária apenas para localização.

Registrar URL, desenho, revisão e data da consulta.

## 4. Método de elaboração

### 4.1 CAD nativo disponível
- preservar a geometria original;
- não simplificar componentes relevantes;
- manter vistas ortográficas;
- converter numericamente a unidade quando necessário;
- não alterar posição relativa das entidades;
- normalizar estilo de texto/layers somente sem perda geométrica.

### 4.2 CAD nativo indisponível
Reconstruir apenas a partir de fonte dimensional oficial:
- começar pelo envelope;
- adicionar base/fixação;
- adicionar conexões;
- adicionar aberturas/grelhas/painéis;
- adicionar interfaces;
- adicionar detalhes de manutenção;
- adicionar vistas;
- manter cada detalhe associado à sua evidência.

Qualquer elemento não cotado deve ser:
- omitido; ou
- marcado como não dimensional/cosmético.

## 5. Sistema de layers sugerido
- `TB-OUTLINE`
- `TB-DETAIL`
- `TB-MOUNTING`
- `TB-CONNECTION`
- `TB-CLEARANCE`
- `TB-ANNOTATION`
- `TB-SOURCE`

## 6. Convenções geométricas
- unidade final: metro;
- escala: 1:1;
- ponto de inserção: definido de forma estável e documentada;
- textos: estilo `ARIAL`;
- nomes de bloco: `FABRICANTE_MODELO_VISTA`;
- vistas: `FRONT`, `LEFT`, `RIGHT`, `TOP`, `BOTTOM`, `SECTION`, conforme disponibilidade.

## 7. Rastreabilidade
Todo bloco deve possuir manifesto com:
- identidade;
- fontes;
- dimensões oficiais;
- desenho/revisão;
- classe da fonte;
- conflitos;
- QA;
- responsável lógico pela validação;
- histórico de mudança.

## 8. Tratamento de conflito
Quando projeto e fabricante divergirem:
1. não corrigir silenciosamente;
2. registrar valor do projeto;
3. registrar valor do fabricante;
4. identificar versão/variante;
5. bloquear aprovação se o conflito afetar instalação, interferência ou montagem;
6. liberar somente após decisão técnica documentada.

## 9. Critério de finalização
Um bloco é considerado final somente quando:
- identidade está fechada;
- fonte é rastreável;
- geometria está compatível;
- QA não possui falha crítica;
- manifesto está completo;
- classe de confiança está definida.
