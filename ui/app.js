async function updateStatus() {
  const r = await fetch('/api/status');
  const s = await r.json();
  document.getElementById('state').textContent = `Estado: ${s.state}`;
  document.getElementById('credit').textContent = `Crédito: $${s.credit}`;
  document.getElementById('size').textContent = `Selección: ${s.selected_size ?? 'ninguna'}`;
}

setInterval(updateStatus, 1000);
updateStatus();
