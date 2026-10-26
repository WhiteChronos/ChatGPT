# Entradas automáticas individuais e conjuntas

Objetivo: três skills de entrada independentes e coordenação conjunta por tarefa.
Arquitetura: reutilizar skills oficiais; seletor determinístico por intenção
declarada e inventário local. Nenhum daemon, timer, modelo extra ou shell remoto.

- Criar testes de isolamento dos modos, rotas por intenção e limites.
- Implementar seletor e diagnóstico de dependências sem executar o plano.
- Criar replica-workflow, superpowers-workflow e arena-workflow.
- Atualizar a coordenação, instalador e pacote portátil para quinze skills.
- Rodar regressões, instalar com backup e validar readback.
- Publicar mudanças em branch e PR separado; gerar pacote web sem afirmar upload.

Aceite: modos individuais não ativam os outros; modo conjunto reutiliza somente
as etapas pertinentes; intenção inválida falha explicitamente; evidência de
seleção não é apresentada como execução do modelo ou do host web.
