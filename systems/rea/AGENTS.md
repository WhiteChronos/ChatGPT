# REA independente — contrato operacional

Sistema dedicado a engenharia reversa autorizada, com proteção de dados, inventário SHA-256, relatórios rastreáveis e análises estáticas. Não depende de outros produtos de engenharia.

- Usar upstream `morluto/rea` quando efetivamente instalado e descoberto; caso contrário, identificar a ferramenta local como independente e limitada.
- Escopo de caminhos sempre restrito ao root autorizado. Negar symlink de escape, credenciais, chaves e arquivos ocultos.
- Sem engenharia reversa em alvos não autorizados, bypass de licenças, captura indevida ou exfiltração.
- Evitar alegar execução de 100 agentes ou que o ranking automatizado é empírico.
- Não operar serviços em rede pública; exigir autenticação e revisão de segurança para qualquer implantação.
- Não modificar outros projetos nem arquivos analisados; análises são read-only.
