# Windows Diagnostics Skills Implementation Plan

> Execução sequencial neste chat, usando writing-plans, executing-plans e verificação proporcional. Nenhum subagente foi iniciado.

**Goal:** Integrar dez forks públicos a um controlador de skills Windows sem executar ferramentas de terceiros ou publicar dados do computador.

**Architecture:** Catálogo JSON com upstream e commit revisado, fork e HEAD observado, licença e estado de adoção. Uma skill própria roteia para referências oficiais; CLI Node offline valida o catálogo e apresenta plano por ferramenta. Os forks permanecem separados do main.

**Tech Stack:** Node.js nativo, node:test, JSON e Markdown. Sem dependências npm, serviços, credenciais ou instalador.

## Decisão de desenho

Escolhida a integração por referências versionadas. Copiar dez árvores de código ou adicionar submódulos ampliaria o checkout e duplicaria ferramentas existentes. Não há atualização automática dos forks nem execução de código externo. A contribuição vai para branch e PR; merge exige aprovação do SHA concreto.

## Restrições e revisão

- Não incluir capturas, dumps, caminhos pessoais, processos, temperaturas ou transcrições.
- Não modificar plugins oficiais, espelhos vendor ou governança de engenharia.
- Fork não significa instalação, segurança ou execução; estados separados e verificáveis.
- Não aceitar licenças binárias, instalar drivers, elevar, coletar ou interromper processos pelo CLI.
- Validar entradas desconhecidas, duplicações, drift e licenças sem afirmar CI remoto inexistente.

## Tarefas

- [x] Conferir conta, origin e main atual; criar worktree e branch isoladas.
- [x] Criar nove forks e reutilizar Superpowers, conferindo parent.
- [x] Registrar catálogo público sanitizado e evidências de commit/licença.
- [x] Escrever testes de validação e limites do CLI; observar falha antes da implementação.
- [x] Implementar CLI offline catalog/validate/plan e skill de roteamento.
- [ ] Rodar testes próprios e gates do repositório, revisar diff e publicar PR para main.

## Aceite

Dez identidades únicas com parent correto e SHAs observados; CLI executável sem rede; erros claros em argumentos ou catálogo inválidos. Skills externas somente referenciadas. PR com resultados reais e nenhuma alegação de correção do Windows.
