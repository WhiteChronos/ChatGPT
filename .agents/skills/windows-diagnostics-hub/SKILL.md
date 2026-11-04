---
name: windows-diagnostics-hub
description: Selecionar ferramentas e skills para investigar CPU, temperatura, processos e persistência no Windows usando o catálogo de dez forks verificados; preparar adoção e comparação por evidências sem instalar ou alterar o host automaticamente.
---

# Windows Diagnostics Hub

Esta skill integra referências, não executa os dez projetos. Sua implementação fica em [systems/windows-diagnostics](../../../systems/windows-diagnostics/README.md), no mesmo checkout. Não instalar este arquivo isolado sem os recursos do sistema.

## Escolher a entrada

- Consumo de CPU/kernel e ETL: `perfview`; `profile-explorer` como alternativa, sem instalar para substituir automaticamente uma ferramenta já disponível.
- Processos, threads e serviços: `systeminformer`; priorizar primeiro as coletas nativas já autorizadas e preservar a escolha do usuário sobre encerrar processos.
- Inventário e triagem PowerShell: `windows-diagnostics-toolkit`, beta e com revisão adicional antes de execução.
- Sensores: fonte OEM já disponível primeiro; `librehardwaremonitor` somente se necessário e após avaliar driver, privilégios e compatibilidade.
- Desenvolvimento de coletor: `psutil`, sem duplicar o coletor existente e sem presumir sensores térmicos Windows.
- Inventário de persistência: `osquery`, com consultas limitadas, sem instalar daemon automaticamente.
- Metodologia: referências `performance-skill` e `windows-powershell-agent-skill`; reutilizar o plugin oficial Superpowers já disponível para investigação/verificação. Não copiar ou substituir suas skills.

## Operação do catálogo

Resolver a raiz deste checkout. Com Node já disponível:

```text
node systems/windows-diagnostics/scripts/hub.mjs catalog
node systems/windows-diagnostics/scripts/hub.mjs validate
node systems/windows-diagnostics/scripts/hub.mjs plan perfview
```

O CLI lê apenas o registro local; não faz rede, coleta, elevação, instalação ou execução upstream. `validate` verifica estrutura, não confirma o estado atual dos forks na web. Ler somente a ficha da ferramenta pertinente em `registry.json`; conferir upstream, commit, licença, fork e eventual divergência antes de adotar.

## Conduzir a investigação

Registrar sintoma, carga e temperatura com fonte e horário; distinguir leitura histórica de atual, CPU do processo de tempo em kernel e percentual amostrado de capacidade total. Identificar PID, início, caminho e processo pai antes de atribuir consumo. Nome desconhecido ou certificado não confiável não comprova malware.

Reutilizar as autorizações específicas do chat. Coletar e executar somente no alvo e escopo autorizados. Não transformar fork ou esta skill em aprovação de EULA, driver, serviço, remoção, mudanças de energia, BIOS ou segurança. Não iniciar stress enquanto houver suspeita térmica. Para mudanças: evidência, benefício, risco, comparação equivalente e rollback praticável.

Manter capturas, dumps, caminhos pessoais e relatos do computador fora deste repositório público. O sistema de caso existente, como avell-diagnostico-seguro quando disponível, continua dono das evidências locais. Não replicar dados privados no catálogo.

## Fechar o trabalho

Separar fork verificado na data, revisão documental, instalação e execução. Exigir resultados antes/depois para afirmar melhora. Reportar símbolos faltantes, eventos perdidos e sobrecarga. Disponibilidade no checkout não comprova carregamento em todos os hosts ou monitoramento permanente.
