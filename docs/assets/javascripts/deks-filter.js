function initDeksFilters() {
  const text = document.querySelector('#deks-text-filter');
  const discipline = document.querySelector('#deks-discipline-filter');
  const objectType = document.querySelector('#deks-object-filter');
  const status = document.querySelector('#deks-status-filter');
  const cards = Array.from(document.querySelectorAll('.deks-card'));
  const count = document.querySelector('#deks-result-count');

  if (!cards.length || !text || !discipline || !objectType || !status) return;

  const apply = () => {
    const query = text.value.trim().toLocaleLowerCase();
    const disciplineValue = discipline.value;
    const objectValue = objectType.value;
    const statusValue = status.value;
    let visible = 0;

    cards.forEach((card) => {
      const matchesText = !query || (card.dataset.search || '').includes(query);
      const matchesDiscipline = !disciplineValue || (card.dataset.discipline || '').split(' ').includes(disciplineValue);
      const matchesObject = !objectValue || card.dataset.object === objectValue;
      const matchesStatus = !statusValue || card.dataset.status === statusValue;
      const show = matchesText && matchesDiscipline && matchesObject && matchesStatus;
      card.hidden = !show;
      if (show) visible += 1;
    });

    if (count) count.textContent = `${visible} verbete(s) exibido(s)`;
  };

  [text, discipline, objectType, status].forEach((control) => {
    control.addEventListener('input', apply);
    control.addEventListener('change', apply);
  });

  apply();
}

if (typeof document$ !== 'undefined') {
  document$.subscribe(initDeksFilters);
} else {
  document.addEventListener('DOMContentLoaded', initDeksFilters);
}
