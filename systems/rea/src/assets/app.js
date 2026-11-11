'use strict';
(() => {
  let bearer = '';
  const el = (id) => document.getElementById(id);
  const status = el('status');
  const notice = el('notice');
  const output = el('output');
  async function connect() {
    const candidate = el('token').value.trim();
    if (candidate.length < 24) { notice.textContent = 'Token muito curto.'; return; }
    status.textContent = 'VERIFICANDO...';
    try {
      const r = await fetch('/api/tool/rea_bridge_status', {
        method: 'POST', headers: { Authorization: 'Bearer ' + candidate, 'Content-Type': 'application/json' },
        body: '{}', cache: 'no-store'
      });
      if (!r.ok) { bearer = ''; status.textContent = 'ACESSO BLOQUEADO';
        notice.textContent = 'Token recusado pelo servidor.'; return; }
      bearer = candidate;
      el('token').value = '';
      status.textContent = 'SESSAO VALIDADA';
      notice.textContent = 'Token validado e guardado apenas na memoria desta aba.';
    } catch (_) {
      status.textContent = 'SEM CONEXAO';
      notice.textContent = 'Servidor local indisponivel.';
    }
  }
  function disconnect() {
    bearer = ''; status.textContent = 'DESCONECTADO';
    output.textContent = 'Sessao encerrada. Nenhuma alteracao foi executada.';
    notice.textContent = 'Token descartado da memoria da pagina.';
  }
  async function invoke(name) {
    if (!bearer) { notice.textContent = 'Conecte com o token local antes de usar ferramentas.'; return; }
    const args = name === 'rea_internal_analyze' ? { directory: el('directory').value || '.', limit: 80 } :
                 name === 'rea_arena_compare' ? { objective: 'source_analysis', confidentiality: 'high' } :
                 name === 'rea_repositories_top10' ? { catalog: el('catalog').value } : {};
    output.textContent = 'Executando verificacao somente leitura...';
    try {
      const res = await fetch(`/api/tool/${encodeURIComponent(name)}`, {
        method: 'POST', headers: { Authorization: 'Bearer ' + bearer, 'Content-Type': 'application/json' },
        body: JSON.stringify(args), cache: 'no-store'
      });
      const data = await res.json();
      if (!res.ok) {
        output.textContent = `HTTP ${res.status}: ${data.error || 'Acesso bloqueado.'}`;
        if (res.status === 401) { disconnect(); }
        return;
      }
      output.textContent = JSON.stringify(data, null, 2);
      notice.textContent = 'Analise local concluida. Todos os resultados continuam sujeitos a revisao tecnica.';
    } catch (_) {
      output.textContent = 'O servidor local nao esta acessivel.';
    }
  }
  el('connect').addEventListener('click', connect);
  el('disconnect').addEventListener('click', disconnect);
  el('token').addEventListener('keydown', (ev) => { if (ev.key === 'Enter') connect(); });
  for (const b of document.querySelectorAll('[data-tool]')) {
    b.addEventListener('click', () => invoke(b.dataset.tool));
  }
})();
