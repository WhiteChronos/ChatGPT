---
name: repository-systems-workflow
description: Selecionar um workflow de repositório confirmado e coordená-lo com REA, Replica, Superpowers, Arena e Vibe em trabalho conjunto solicitado.
---

# Coordenação seletiva por repositório

Busque o identificador exato em references/registry.json. Leia somente o adaptador e a skill upstream pertinentes. Modo individual permanece independente. Modo conjunto escolhe responsabilidades pela intenção; não carrega todo o catálogo.

- Desenvolvimento: Superpowers para plano, diagnóstico, implementação e testes; Vibe para padrões quando útil.
- Análise estática: whitechronos-lab encaminha fontes selecionadas ao REA real. Confira disponibilidade via doctor, preserve saída completa e hashes. Falha do motor é BLOCKED; inventário não substitui análise semântica. REA não prova comportamento.
- Reconstrução/paridade: replica-workflow somente quando houver referência e necessidade.
- Revisão: arena-workflow e ferramentas realmente disponíveis, perspectivas sequenciais; não inicia torneios automaticamente.
- GitHub: origin/HEAD/trabalho humano, mudança delimitada, testes e PR. Atualização de plugin exige envio e readback da versão na conta; ZIP não prova upload.

O helper scripts/workflows.py plan retorna PLAN_ONLY. A execução cabe ao agente atual com ferramentas disponíveis e escopo autorizado. Não muda modelo/conta, não inicia modelos pagos nem serviços, não exige Linux/WSL/Docker. Não amplia aprovações de ferramentas nem publica arquivos privados. Após atualização, registre evidência nova; sem monitoramento periódico. Instalação não comprova todas as conversas.
