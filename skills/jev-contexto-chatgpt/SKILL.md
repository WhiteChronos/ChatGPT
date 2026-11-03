---
name: jev-contexto-chatgpt
description: Orientar retencao, deduplicacao e verificacao de contexto de trabalho no ChatGPT Web com base no fast-jev-compaction; usar quando o usuario pedir Jev, reducao de redundancia, compactacao de evidencias, preservacao de decisoes ou avaliacao de eficiencia do contexto.
---

# Jev — contexto inteligente para ChatGPT

- Separe informacoes essenciais, restricoes, provas, resultados transitorios e material recuperavel. Nunca omita instrucao superior nem fatos criticos.
- Nao afirme acesso ao historico interno completo, a mecanismos de compactacao privativos ou a hooks do ChatGPT Web.
- Resuma somente evidencias sob controle da conversa; preserve links, versoes, hashes, decisoes, incertezas e orientacoes explicitas.
- Para historicos de ferramentas acessiveis, mantenha pares chamada/resultado consistentes e nunca substitua um comprovante por inferencia.
- Se uma compactacao perder contexto critico, retorne ao original e registre a falha para melhoria futura.
- Motor original: `tamaratran/fast-jev-compaction`, biblioteca npm e plugin Claude Code. Nao declarar sua execucao dentro do ChatGPT Web sem interface realmente suportada e teste real.
- Jev nao deve realizar engenharia reversa; a skill REA tem responsabilidade distinta. As duas podem compartilhar apenas protocolos de evidencia.
- Nao execute inferencias pagas, nao instale aplicativos ou plugins, nao publique nem altere repositorios automaticamente.
