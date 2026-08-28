async function initDeksMermaid() {
  const nodes = document.querySelectorAll('.mermaid');
  if (!nodes.length) return;

  try {
    const module = await import('https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs');
    const mermaid = module.default;
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: 'strict',
      theme: document.body.getAttribute('data-md-color-scheme') === 'slate' ? 'dark' : 'default'
    });
    await mermaid.run({ nodes: Array.from(nodes) });
  } catch (error) {
    console.warn('DEKS Mermaid indisponível:', error);
  }
}

if (typeof document$ !== 'undefined') {
  document$.subscribe(initDeksMermaid);
} else {
  document.addEventListener('DOMContentLoaded', initDeksMermaid);
}
