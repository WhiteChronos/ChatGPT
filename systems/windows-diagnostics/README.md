# Windows Diagnostics Hub

Controlador local de referências para diagnosticar Windows com dez forks públicos e uma skill própria de roteamento. Mantém origem, commit revisado, licença, HEAD observado do fork, riscos, critérios de comparação e rollback. Não é um otimizador ou antivírus e não altera Windows.

## Usar

Requer Node.js 20 ou superior já disponível, sem npm install. Na raiz do checkout:

```powershell
node systems/windows-diagnostics/scripts/hub.mjs catalog
node systems/windows-diagnostics/scripts/hub.mjs validate
node systems/windows-diagnostics/scripts/hub.mjs plan perfview
node --test systems/windows-diagnostics/tests/hub.test.mjs
```

Os três comandos do controlador são offline e somente leem `registry.json`. Argumentos de instalação ou execução são rejeitados. `plan` apresenta referência e proposta de avaliação; não concede autorização. A skill está em [.agents/skills/windows-diagnostics-hub](../../.agents/skills/windows-diagnostics-hub/SKILL.md).

## Repositórios ligados

| Função | Upstream | Fork |
|---|---|---|
| CPU/ETW | [microsoft/perfview](https://github.com/microsoft/perfview) | [WhiteChronos/perfview](https://github.com/WhiteChronos/perfview) |
| CPU/ETL alternativo | [microsoft/profile-explorer](https://github.com/microsoft/profile-explorer) | [WhiteChronos/profile-explorer](https://github.com/WhiteChronos/profile-explorer) |
| Processos | [winsiderss/systeminformer](https://github.com/winsiderss/systeminformer) | [WhiteChronos/systeminformer](https://github.com/WhiteChronos/systeminformer) |
| PowerShell, beta | [0x0bug/windows-diagnostics-toolkit](https://github.com/0x0bug/windows-diagnostics-toolkit) | [WhiteChronos/windows-diagnostics-toolkit](https://github.com/WhiteChronos/windows-diagnostics-toolkit) |
| Sensores | [LibreHardwareMonitor/LibreHardwareMonitor](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor) | [WhiteChronos/LibreHardwareMonitor](https://github.com/WhiteChronos/LibreHardwareMonitor) |
| Biblioteca de processos | [giampaolo/psutil](https://github.com/giampaolo/psutil) | [WhiteChronos/psutil](https://github.com/WhiteChronos/psutil) |
| Inventário | [osquery/osquery](https://github.com/osquery/osquery) | [WhiteChronos/osquery](https://github.com/WhiteChronos/osquery) |
| Skill de desempenho | [wieslawsoltes/Performance-Skill](https://github.com/wieslawsoltes/Performance-Skill) | [WhiteChronos/Performance-Skill](https://github.com/WhiteChronos/Performance-Skill) |
| Skill PowerShell | [LukeTsengTW/windows-powershell-agent-skill](https://github.com/LukeTsengTW/windows-powershell-agent-skill) | [WhiteChronos/windows-powershell-agent-skill](https://github.com/WhiteChronos/windows-powershell-agent-skill) |
| Método de investigação | [obra/superpowers](https://github.com/obra/superpowers) | [WhiteChronos/superpowers](https://github.com/WhiteChronos/superpowers) |

Nove forks foram criados para esta integração; o fork Superpowers existente foi reutilizado. Não há sincronização automática, submódulos ou código upstream vendorizado. Os estados são observações datadas, não garantias atuais de disponibilidade, segurança ou funcionamento. O fork Superpowers pode estar em commit diferente da revisão documental: `plan superpowers` expõe a diferença sem atualizar o fork ou substituir o plugin oficial.

## Fluxo de adoção

1. Identificar a pergunta e as ferramentas já disponíveis; selecionar uma ficha, sem carregar todo o catálogo.
2. Conferir o upstream e commit pretendido, README, licença do código e do binário, assinaturas e dependências. O metadado NOASSERTION do osquery foi esclarecido pelos arquivos de licença: Apache-2.0 OR GPL-2.0-only.
3. Propor coleta ou mudança com escopo, custo, critérios de comparação e rollback; reutilizar autorização já aplicável.
4. Executar somente a etapa autorizada e registrar resultados privados fora deste checkout público.
5. Comparar situações equivalentes; manter `NOT_RUN` para tudo que não foi executado. Catálogo/fork não comprova causa térmica nem mineração.

Para calor e CPU: registrar temperatura com fonte/horário e carga simultânea; comparar janelas passivas equivalentes, sem stress. Não somar tempo em kernel ao consumo dos processos como se fossem causas independentes. Capturas antigas, pilhas inclusivas e símbolos ausentes exigem interpretação explícita.

## Licenças e dados

O registro inclui URLs fixadas por commit e SHA-256 das fontes documentais observadas. Esses hashes identificam textos de referência; o CLI não baixa arquivos para revalidá-los. Licenças específicas e de componentes/binários devem ser conferidas antes de copiar código ou executar ferramentas. Apenas referências e código próprio do controlador são distribuídos aqui.

Não incluir dumps, traces, inventário da máquina, caminhos pessoais, credenciais ou conversas. Não instalar agentes, drivers, ferramentas, skills externas, hooks ou serviços como efeito de usar o catálogo. Esta integração não prova ativação no ChatGPT web, em outras conversas ou computadores.

## Atualizar ou reverter

Atualizações são manuais por branch/PR: reler fontes, conferir parent/HEAD dos forks, atualizar somente fatos revistos, executar testes e revisar o diff. Nunca marcar instalação/execução por inferência. Para desfazer a integração, reverter seu commit no repositório; os forks são independentes e não são apagados automaticamente. Instalações futuras precisam de rollback próprio registrado na ficha.
