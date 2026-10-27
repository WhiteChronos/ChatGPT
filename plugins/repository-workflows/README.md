# Workflows dos Repositórios + REA

43 repositórios com presença confirmada de SKILL.md, um adaptador individual para cada um e um coordenador conjunto. Conteúdo próprio: não redistribui skills upstream nem substitui plugins oficiais.

Use a skill pelo identificador em registry.json. O comando `python scripts/workflows.py plan --repository owner/repo --intent bugfix --mode individual` seleciona o modo isolado; `--mode combined` combina apenas etapas pertinentes. `--intent static-analysis` inclui REA e `reconstruct` inclui Replica. O helper é PLAN_ONLY; o agente executa a tarefa autorizada.

Na web, importe o ZIP individual desejado ou o pacote conjunto. Eles contêm os mesmos adaptadores: evite instalar ambos para o mesmo sistema. Não sobrescreva plugins oficiais. Fontes upstream requerem conector/arquivo acessível; não há execução remota Windows.

Cobertura é presença, não inventário exaustivo: buscas indexadas podem omitir arquivos. Sem resultado não significa ausência comprovada. Veja registry.json e evidências da execução. Fontes originais permanecem separadas. Licença MIT somente para estes adaptadores; conteúdo upstream mantém sua licença.

Sem agendamento semanal. Revalidação após atualização relevante. Conta web, descoberta em novas conversas e execução real de cada upstream permanecem NOT_VERIFIED até prova específica.

Versão de empacotamento 1.0.3: veja [compatibilidade ChatGPT web/Codex/GitHub](COMPATIBILITY.md).
