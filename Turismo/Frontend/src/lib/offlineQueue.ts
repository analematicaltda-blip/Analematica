/**
 * Cola de Operaciones Offline - SARITA Web
 * Utiliza persistencia local para asegurar que ninguna acción del usuario se pierda.
 */

export interface OfflineAction {
  id: string;
  type: string;
  payload: any;
  timestamp: number;
}

export const offlineQueue = {
  // Simulación de persistencia local (en producción usaría IndexedDB / Dexie)
  getQueue: (): OfflineAction[] => {
    if (typeof window === 'undefined') return [];
    const queue = localStorage.getItem('sarita_offline_queue');
    return queue ? JSON.parse(queue) : [];
  },

  enqueue: (type: string, payload: any) => {
    const action: OfflineAction = {
      id: crypto.randomUUID(),
      type,
      payload,
      timestamp: Date.now(),
    };
    const queue = offlineQueue.getQueue();
    queue.push(action);
    localStorage.setItem('sarita_offline_queue', JSON.stringify(queue));
    console.log(`Acción encolada offline: ${type}`);
  },

  sync: async (processAction: (action: OfflineAction) => Promise<void>) => {
    const queue = offlineQueue.getQueue();
    if (queue.length === 0) return;

    console.log(`Sincronizando ${queue.length} acciones pendientes...`);
    for (const action of queue) {
      try {
        await processAction(action);
        // Remover de la cola si es exitoso
        const currentQueue = offlineQueue.getQueue().filter(a => a.id !== action.id);
        localStorage.setItem('sarita_offline_queue', JSON.stringify(currentQueue));
      } catch (error) {
        console.error(`Fallo al sincronizar acción ${action.id}:`, error);
        // Se mantiene en cola para el siguiente intento
      }
    }
  }
};
