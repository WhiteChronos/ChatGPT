---
name: rea-engenharia-reversa-evolutiva
description: "Investigar engenharia reversa autorizada com evidencias, rastreabilidade e comparacao de implementacoes, sem dependencias de MCE."
---

# REA — Engenharia Reversa Evolutiva

## Missão
Investigar sistemas autorizados e transformar comportamento observado em conhecimento verificável e especificações úteis. Tratar REA como ferramenta de **investigação**, independente de qualquer serviço de compactação Jev.

## Fluxo obrigatório
1. Delimitar alvo, versão/commit, finalidade e autorização. Preferir interfaces públicas e código-fonte a métodos invasivos. Não burlar autenticação, licença ou proteções de segurança.
2. Verificar disponibilidade do REA no ambiente corrente. Projeto de referência: `https://github.com/morluto/rea`, pacote `rea-agents`. Consultar versão e instruções atuais antes de executar. Não inventar execução MCP, logs ou evidências.
3. Selecionar investigação proporcional: documentação/código, análise estática JavaScript, dependências, estruturas de dados, contratos, testes, ou inspeção dinâmica expressamente autorizada. Usar somente ferramentas efetivamente disponíveis; sem REA, realizar análise manual **identificada como manual**.
4. Registrar cada achado com `alvo`, `versão/sha`, `artefato`, `linha/símbolo`, `ferramenta`, `observação`, `inferência`, `incerteza`, `risco` e `passo de reprodução`. Preservar evidências originais e mascarar segredos.
5. Elaborar um mapa de módulos, entradas, saídas, dependências, fluxos e pontos de falha; separar fatos de hipóteses.
6. Validar com testes comportamentais e casos adversariais proporcionais. Quando criar implementação inspirada no alvo, utilizar interfaces suportadas, licenças pertinentes e testes independentes.
7. Detectar deficiência recorrente: reproduzir, classificar causa, verificar skills existentes e **propor** correção ou skill candidata se houver responsabilidade realmente nova. Nunca auto-instalar, publicar ou alterar outras skills sem autorização e recursos de escrita.
8. Em tarefas subsequentes, comparar nova evidência com o registro anterior e atualizar recomendações; não alegar execução contínua entre conversas sem agendamento real.

## Entregável padrão
Produzir resultado, evidências concretas, pontos ainda não verificáveis, risco, roteiro de reprodução e eventual proposta de evolução. Para trabalho em GitHub, respeitar PR, CI, SHA exato e gates de segurança; não fazer merge/deploy por implicação.

## Compatibilidade ChatGPT Web
A skill organiza investigações e ferramentas autorizadas acessíveis à conversa. Ela **não instala automaticamente** o servidor REA no ChatGPT Web e não cria acesso ao computador local. Se não houver ferramenta REA conectada, reportar `REA_RUNTIME=UNAVAILABLE` e preservar a distinção entre inspeção manual e análise instrumental.
