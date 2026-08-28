function initInteractiveGlossary() {
  const grid = document.querySelector('#deks-glossary-grid');
  if (!grid) return;

  const cards = Array.from(grid.querySelectorAll('.deks-glossary-card'));
  const search = document.querySelector('#deks-glossary-search');
  const source = document.querySelector('#deks-glossary-source');
  const entity = document.querySelector('#deks-glossary-entity');
  const status = document.querySelector('#deks-glossary-status');
  const evidence = document.querySelector('#deks-glossary-evidence');
  const sort = document.querySelector('#deks-glossary-sort');
  const count = document.querySelector('#deks-glossary-result-count');
  const reset = document.querySelector('#deks-glossary-reset');
  const empty = document.querySelector('#deks-glossary-empty');
  const scopeButtons = Array.from(document.querySelectorAll('[data-glossary-scope]'));
  const detailPanel = document.querySelector('#deks-detail-panel');
  const detailContent = document.querySelector('#deks-detail-content');
  const detailClose = document.querySelector('#deks-detail-close');
  let activeScope = 'all';

  const normalize = (value) => (value || '').toLocaleLowerCase('pt-BR');

  const matchesScope = (card) => {
    if (activeScope === 'all') return true;
    if (activeScope === 'symbol') return card.dataset.scope === 'staging' && card.dataset.entity === 'symbol';
    return card.dataset.scope === activeScope;
  };

  const sortCards = () => {
    const key = sort?.value || 'title';
    const attribute = key === 'title' ? 'title' : key;
    const ordered = [...cards].sort((a, b) => {
      const left = normalize(a.dataset[attribute]);
      const right = normalize(b.dataset[attribute]);
      return left.localeCompare(right, 'pt-BR', { numeric: true, sensitivity: 'base' });
    });
    ordered.forEach((card) => grid.appendChild(card));
  };

  const apply = () => {
    const query = normalize(search?.value.trim());
    const sourceValue = source?.value || '';
    const entityValue = entity?.value || '';
    const statusValue = status?.value || '';
    const evidenceValue = evidence?.value || '';
    let visible = 0;

    cards.forEach((card) => {
      const show =
        matchesScope(card) &&
        (!query || normalize(card.dataset.search).includes(query)) &&
        (!sourceValue || card.dataset.source === sourceValue) &&
        (!entityValue || card.dataset.entity === entityValue) &&
        (!statusValue || card.dataset.status === statusValue) &&
        (!evidenceValue || card.dataset.evidence === evidenceValue);

      card.hidden = !show;
      if (show) visible += 1;
    });

    sortCards();
    if (count) count.textContent = `${visible} registro(s) exibido(s) de ${cards.length}`;
    if (empty) empty.hidden = visible !== 0;
  };

  scopeButtons.forEach((button) => {
    button.addEventListener('click', () => {
      activeScope = button.dataset.glossaryScope || 'all';
      scopeButtons.forEach((item) => item.classList.toggle('is-active', item === button));
      apply();
    });
  });

  [search, source, entity, status, evidence, sort].filter(Boolean).forEach((control) => {
    control.addEventListener('input', apply);
    control.addEventListener('change', apply);
  });

  if (reset) {
    reset.addEventListener('click', () => {
      [search, source, entity, status, evidence].filter(Boolean).forEach((control) => {
        control.value = '';
      });
      if (sort) sort.value = 'title';
      activeScope = 'all';
      scopeButtons.forEach((item) => item.classList.toggle('is-active', item.dataset.glossaryScope === 'all'));
      apply();
    });
  }

  const closeDetail = () => {
    if (!detailPanel) return;
    detailPanel.hidden = true;
    if (detailContent) detailContent.replaceChildren();
  };

  cards.forEach((card) => {
    const trigger = card.querySelector('.deks-open-entry');
    const template = card.querySelector('.deks-entry-detail');
    if (!trigger || !template || !detailPanel || !detailContent) return;

    trigger.addEventListener('click', () => {
      detailContent.replaceChildren(template.content.cloneNode(true));
      detailPanel.hidden = false;
      detailPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  if (detailClose) detailClose.addEventListener('click', closeDetail);
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && detailPanel && !detailPanel.hidden) closeDetail();
  });

  apply();
}

if (typeof document$ !== 'undefined') {
  document$.subscribe(initInteractiveGlossary);
} else {
  document.addEventListener('DOMContentLoaded', initInteractiveGlossary);
}
