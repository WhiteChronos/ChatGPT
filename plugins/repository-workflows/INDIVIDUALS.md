# Um plugin por repositório

Cada um dos 43 repositórios com SKILL.md confirmado tem uma entrada própria AVAILABLE no marketplace, uma pasta de plugin e um registro de integração próprios. O modo padrão é individual. REA, Superpowers, Arena, Replica e Vibe são camadas opcionais escolhidas pela tarefa e disponibilidade.

Os ZIPs individuais são gerados com `python plugins/repository-workflows/scripts/separate.py --output <nova-pasta> --packages <nova-pasta-zips> --receipt <recibo.json>`. O gerador preserva entradas existentes que diferem e não altera as skills de origem. Use o plugin individual ou o pacote conjunto para evitar duplicação de adaptadores. Eles referenciam as skills upstream; não instalam seus runtimes.

O upload da conta web é uma etapa separada; criação do ZIP e publicação GitHub não comprovam instalação ou execução no ChatGPT. O agente do host executa o workflow dentro do escopo autorizado; não há serviço permanente.

| Repositório | Plugin individual |
|---|---|
| 1337hero/faster-chat | [wf-1337hero-faster-chat-11cb6c69](individual/wf-1337hero-faster-chat-11cb6c69/README.md) |
| aeroxy/chrome-devtools-cli | [wf-aeroxy-chrome-devtools-cli-ec64bb78](individual/wf-aeroxy-chrome-devtools-cli-ec64bb78/README.md) |
| affaan-m/ECC | [wf-affaan-m-ecc-0658d7fa](individual/wf-affaan-m-ecc-0658d7fa/README.md) |
| Arize-ai/phoenix | [wf-arize-ai-phoenix-1ca6c04a](individual/wf-arize-ai-phoenix-1ca6c04a/README.md) |
| ChromeDevTools/chrome-devtools-mcp | [wf-chromedevtools-chrome-devtools-mcp-c68b4f26](individual/wf-chromedevtools-chrome-devtools-mcp-c68b4f26/README.md) |
| comet-ml/opik-mcp | [wf-comet-ml-opik-mcp-786fea2f](individual/wf-comet-ml-opik-mcp-786fea2f/README.md) |
| dataelement/bisheng | [wf-dataelement-bisheng-e21a4138](individual/wf-dataelement-bisheng-e21a4138/README.md) |
| future-agi/future-agi | [wf-future-agi-future-agi-dc3bdaee](individual/wf-future-agi-future-agi-dc3bdaee/README.md) |
| gbasin/dejank | [wf-gbasin-dejank-5a6ba81e](individual/wf-gbasin-dejank-5a6ba81e/README.md) |
| github/spec-kit | [wf-github-spec-kit-ea503c1a](individual/wf-github-spec-kit-ea503c1a/README.md) |
| google/perfetto | [wf-google-perfetto-72e3738b](individual/wf-google-perfetto-72e3738b/README.md) |
| GoogleChrome/lighthouse | [wf-googlechrome-lighthouse-d1708a87](individual/wf-googlechrome-lighthouse-d1708a87/README.md) |
| Jakeschincariol/arena-skill | [wf-jakeschincariol-arena-skill-c734ca29](individual/wf-jakeschincariol-arena-skill-c734ca29/README.md) |
| Jakeschincariol/replica-skill | [wf-jakeschincariol-replica-skill-a44b40b4](individual/wf-jakeschincariol-replica-skill-a44b40b4/README.md) |
| jamesmoore24/treegpt | [wf-jamesmoore24-treegpt-6a43b665](individual/wf-jamesmoore24-treegpt-6a43b665/README.md) |
| katanemo/plano | [wf-katanemo-plano-5d0e2850](individual/wf-katanemo-plano-5d0e2850/README.md) |
| kepano/obsidian-skills | [wf-kepano-obsidian-skills-bdf89258](individual/wf-kepano-obsidian-skills-bdf89258/README.md) |
| langfuse/langfuse | [wf-langfuse-langfuse-e85578e0](individual/wf-langfuse-langfuse-e85578e0/README.md) |
| latitude-dev/latitude-llm | [wf-latitude-dev-latitude-llm-02e58234](individual/wf-latitude-dev-latitude-llm-02e58234/README.md) |
| LibreChat-AI/LibreChat | [wf-librechat-ai-librechat-438ddea7](individual/wf-librechat-ai-librechat-438ddea7/README.md) |
| lobehub/lobehub | [wf-lobehub-lobehub-273e910e](individual/wf-lobehub-lobehub-273e910e/README.md) |
| LogneBudo/llmxray | [wf-lognebudo-llmxray-26c34ef4](individual/wf-lognebudo-llmxray-26c34ef4/README.md) |
| mastra-ai/mastra | [wf-mastra-ai-mastra-db814e7b](individual/wf-mastra-ai-mastra-db814e7b/README.md) |
| microsoft/playwright | [wf-microsoft-playwright-afbb5a8a](individual/wf-microsoft-playwright-afbb5a8a/README.md) |
| mlflow/mlflow | [wf-mlflow-mlflow-93fff73e](individual/wf-mlflow-mlflow-93fff73e/README.md) |
| monoscope-tech/monoscope | [wf-monoscope-tech-monoscope-66266baf](individual/wf-monoscope-tech-monoscope-66266baf/README.md) |
| obra/superpowers | [wf-obra-superpowers-4251a228](individual/wf-obra-superpowers-4251a228/README.md) |
| openai/skills | [wf-openai-skills-f46db908](individual/wf-openai-skills-f46db908/README.md) |
| openobserve/openobserve | [wf-openobserve-openobserve-edacb9cb](individual/wf-openobserve-openobserve-edacb9cb/README.md) |
| puppeteer/puppeteer | [wf-puppeteer-puppeteer-7201fb0e](individual/wf-puppeteer-puppeteer-7201fb0e/README.md) |
| pydantic/logfire | [wf-pydantic-logfire-0b169f2d](individual/wf-pydantic-logfire-0b169f2d/README.md) |
| shimo4228/jev-skill-router | [wf-shimo4228-jev-skill-router-d055091d](individual/wf-shimo4228-jev-skill-router-d055091d/README.md) |
| theopenco/llmgateway | [wf-theopenco-llmgateway-74060a45](individual/wf-theopenco-llmgateway-74060a45/README.md) |
| tma1-ai/tma1 | [wf-tma1-ai-tma1-0b591684](individual/wf-tma1-ai-tma1-0b591684/README.md) |
| vectorize-io/hindsight | [wf-vectorize-io-hindsight-57687486](individual/wf-vectorize-io-hindsight-57687486/README.md) |
| vercel-labs/agent-skills | [wf-vercel-labs-agent-skills-7327b382](individual/wf-vercel-labs-agent-skills-7327b382/README.md) |
| vercel-labs/skills | [wf-vercel-labs-skills-ac98481e](individual/wf-vercel-labs-skills-ac98481e/README.md) |
| vercel/next.js | [wf-vercel-next-js-079c0319](individual/wf-vercel-next-js-079c0319/README.md) |
| vllm-project/semantic-router | [wf-vllm-project-semantic-router-5b33926f](individual/wf-vllm-project-semantic-router-5b33926f/README.md) |
| vllm-project/speculators | [wf-vllm-project-speculators-14d6fbcd](individual/wf-vllm-project-speculators-14d6fbcd/README.md) |
| WhiteChronos/ChatGPT | [wf-whitechronos-chatgpt-e5a7df31](individual/wf-whitechronos-chatgpt-e5a7df31/README.md) |
| WhiteChronos/whitechronos-rea-lab | [wf-whitechronos-whitechronos-rea-lab-13b1eca9](individual/wf-whitechronos-whitechronos-rea-lab-13b1eca9/README.md) |
| WXK-AI/jev-opus | [wf-wxk-ai-jev-opus-3395fe54](individual/wf-wxk-ai-jev-opus-3395fe54/README.md) |
