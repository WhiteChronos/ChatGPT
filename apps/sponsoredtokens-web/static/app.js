'use strict';

const messages = [];
let submitting = false;
let failedTurn = false;

const statusNode = document.getElementById('status');
const providerNode = document.getElementById('provider');
const modelNode = document.getElementById('model');
const routerNode = document.getElementById('router');
const messagesNode = document.getElementById('messages');
const emptyNode = document.getElementById('empty-state');
const form = document.getElementById('composer');
const input = document.getElementById('message-input');
const send = document.getElementById('send');
const retry = document.getElementById('retry');
const clear = document.getElementById('clear');

function setStatus(text) { statusNode.textContent = text; }

function routerLabel(router) {
  return router === 'laya' ? 'Laya local' : 'Fallback determinístico';
}

function renderMessage(role, content) {
  const article = document.createElement('article');
  article.className = `message message-${role}`;
  const label = document.createElement('span');
  label.className = 'message-label';
  label.textContent = role === 'user' ? 'Voce' : 'Assistente';
  article.append(label, document.createTextNode(content));
  messagesNode.append(article);
  emptyNode.hidden = true;
  article.scrollIntoView({ block: 'nearest' });
}

function setBusy(value) {
  submitting = value;
  send.disabled = value;
  retry.disabled = value;
  clear.disabled = value;
  input.disabled = value;
}

async function submitHistory() {
  if (submitting || messages.length === 0) return;
  setBusy(true);
  retry.hidden = true;
  setStatus('Enviando...');
  try {
    const response = await fetch('/api/chat', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || 'request_failed');
    messages.push({ role: 'assistant', content: payload.text });
    renderMessage('assistant', payload.text);
    providerNode.textContent = payload.provider;
    modelNode.textContent = payload.model;
    routerNode.textContent = routerLabel(payload.router);
    failedTurn = false;
    setStatus('Pronto');
  } catch (error) {
    failedTurn = true;
    retry.hidden = false;
    setStatus('Falha no envio. Tente novamente.');
  } finally {
    setBusy(false);
    input.focus();
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (submitting || failedTurn) return;
  const content = input.value;
  if (!content.trim()) return;
  messages.push({ role: 'user', content });
  renderMessage('user', content);
  input.value = '';
  await submitHistory();
});

retry.addEventListener('click', submitHistory);
clear.addEventListener('click', () => {
  if (submitting) return;
  messages.splice(0);
  messagesNode.replaceChildren();
  emptyNode.hidden = false;
  retry.hidden = true;
  failedTurn = false;
  setStatus('Conversa limpa');
  input.focus();
});

input.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

async function loadHealth() {
  try {
    const response = await fetch('/api/health', { cache: 'no-store' });
    const health = await response.json();
    providerNode.textContent = health.provider;
    modelNode.textContent = health.model;
    routerNode.textContent = routerLabel(health.router);
    setStatus(health.ready ? 'Pronto' : 'Chave nao configurada');
    send.disabled = !health.ready;
  } catch (error) {
    setStatus('Servidor indisponivel');
    send.disabled = true;
  }
}

loadHealth();
input.focus();
