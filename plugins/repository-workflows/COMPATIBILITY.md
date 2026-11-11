# ChatGPT web, Codex e GitHub — compatibilidade 1.0.3

A versão 1.0.3 limita `shortDescription` a 25 caracteres, abaixo do limite de 30 do Plugin Creator. Preserva nomes, prompts, fontes e repositórios. Salvar um pacote exige as ferramentas reais do Plugin Creator e readback; esta correção não comprova instalação na conta.

## Formato

O manifesto portátil é `plugin.json` na raiz, com `$schema`, identidade, versão e `extensions.com.openai.interface`. Skills são descobertas em `skills/`. O arquivo `.codex-plugin/plugin.json` é mantido como overlay de compatibilidade Codex com a mesma identidade, versão e apresentação. O esquema portátil não permite os campos legados `skills` e `interface` na raiz; a regressão reproduz essa falha antes da correção.

Os 43 plugins individuais mantêm seus nomes. Existe também um pacote conjunto opcional. Escolha individual ou conjunto para evitar duplicar as mesmas skills. Os adaptadores referenciam os upstreams e não instalam seus runtimes.

## GitHub e Codex

As pastas individuais estão em `plugins/repository-workflows/individual/<nome>`. O marketplace `.agents/plugins/marketplace.json` e os registros de integração continuam apontando para elas. A publicação conserva a política AVAILABLE e as escolhas existentes; não instala ou habilita plugins automaticamente.

Para adicionar a fonte GitHub em um Codex que ofereça o comando oficial, use `codex plugin marketplace add WhiteChronos/ChatGPT --ref main`. Para uma fonte já configurada, confira `codex plugin marketplace list` e atualize a fonte correta com `codex plugin marketplace upgrade <nome>`. Confirme o nome e a versão 1.0.3 no host. O arquivo no repositório e a atualização da conta ChatGPT web são estados diferentes.

## ChatGPT web

Use o ZIP 1.0.3 do plugin escolhido. Na página de plugins da conta, envie-o como atualização quando aquele plugin já existir; crie uma entrada somente quando ainda não houver a mesma identidade. Confira a versão e as skills após o processamento. A disponibilidade do formulário e da instalação depende da conta/workspace. Importação GitHub no desktop não prova importação no workspace web.

Em uma conversa nova, selecione o plugin e peça: “Identifique a skill deste plugin e o repositório correspondente. Leia a referência pertinente com as ferramentas disponíveis e informe qual operação foi realmente executada.” Registre resultado e limitações; o modelo repetir o nome do plugin não prova execução do upstream. REA local requer acesso real ao host; sem ele, registre BLOCKED.

## Validação

`jsonschema==4.25.1` valida os manifestos portáteis contra o esquema Agent Plugins 1.0.0. O snapshot de constraints em `schemas/agent-plugins-1.0.0.schema.json` mantém os tipos, campos obrigatórios, padrões e política de propriedades do original; descrições de campos foram omitidas. As regressões verificam manifesto/overlay, caminhos, identidades, isolamento e ZIPs. Isso comprova formato e empacotamento, não instalação em conta nem descoberta automática em todos os chats.

Fontes consultadas em 27/10/2026:
- https://developers.openai.com/plugins/build/plugins
- https://developers.openai.com/plugins/build/skills
- https://developers.openai.com/plugins/deploy/submission
- https://agent-plugins.org/schemas/1.0.0/plugin.schema.json

Nenhuma credencial, hook, serviço permanente, permissão ou alteração de modelo é necessária para esta correção de formato.
