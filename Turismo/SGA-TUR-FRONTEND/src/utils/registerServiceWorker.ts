/**
 * Utilitario para el registro y ciclo de vida del Service Worker en SARITA Web.
 */

export const registerServiceWorker = async () => {
  if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js');
      console.log('SARITA Service Worker registrado con éxito:', registration.scope);

      // Manejo de actualizaciones del SW
      registration.onupdatefound = () => {
        const installingWorker = registration.installing;
        if (installingWorker) {
          installingWorker.onstatechange = () => {
            if (installingWorker.state === 'installed') {
              if (navigator.serviceWorker.controller) {
                console.log('Nueva versión disponible. Recargue para actualizar.');
                // Aquí se podría disparar un toast de notificación
              } else {
                console.log('Contenido cacheado para uso offline.');
              }
            }
          };
        }
      };
    } catch (error) {
      console.error('Error al registrar el Service Worker:', error);
    }
  }
};
