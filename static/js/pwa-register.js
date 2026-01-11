if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js')
      .then(reg => {
        console.log('ServiceWorker registrado:', reg.scope);
        if (reg.waiting) {
          // caso já exista SW esperando, solicitar skip waiting
          reg.waiting.postMessage({ type: 'SKIP_WAITING' });
        }
        reg.addEventListener('updatefound', () => {
          const newSW = reg.installing;
          newSW && newSW.addEventListener('statechange', () => {
            if (newSW.state === 'installed' && navigator.serviceWorker.controller) {
              // nova versão disponível
              console.log('Nova versão disponível. Atualize para ver mudanças.');
            }
          });
        });
      })
      .catch(err => console.warn('Falha ao registrar ServiceWorker:', err));
  });
}

// utilitário simples para solicitar skipWaiting via UI (ex: botão atualizar)
function pwaSkipWaiting() {
  if (!navigator.serviceWorker) return;
  navigator.serviceWorker.getRegistration().then(reg => {
    if (reg && reg.waiting) reg.waiting.postMessage({ type: 'SKIP_WAITING' });
  });
}

export { pwaSkipWaiting };
