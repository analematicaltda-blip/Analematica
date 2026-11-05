import { useState, useEffect } from 'react';

// Custom hook para "rebotar" (debounce) un valor.
// Solo actualiza el valor devuelto después de que no ha habido cambios en un tiempo (delay).
export default function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    // Configura un temporizador para actualizar el valor debounced después del delay
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    // Limpia el temporizador si el valor cambia (o el componente se desmonta)
    // Esto es lo que evita que el valor se actualice con cada tecleo.
    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]); // Solo se vuelve a ejecutar si el valor o el delay cambian

  return debouncedValue;
}