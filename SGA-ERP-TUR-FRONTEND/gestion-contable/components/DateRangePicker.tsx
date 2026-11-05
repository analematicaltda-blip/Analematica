// Placeholder for DateRangePicker component
import React from 'react';

interface DateRangePickerProps {
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  isLoading: boolean;
}

const DateRangePicker = ({ onSubmit, isLoading }: DateRangePickerProps) => {
  return (
    <form onSubmit={onSubmit} className="flex items-center gap-4 mb-4 p-4 bg-gray-50 rounded-lg">
      <div>
        <label htmlFor="start_date" className="block text-sm font-medium text-gray-700">Fecha de Inicio</label>
        <input type="date" name="start_date" id="start_date" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2" />
      </div>
      <div>
        <label htmlFor="end_date" className="block text-sm font-medium text-gray-700">Fecha de Fin</label>
        <input type="date" name="end_date" id="end_date" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2" />
      </div>
      <div className="self-end">
        <button type="submit" disabled={isLoading} className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50">
          {isLoading ? 'Generando...' : 'Generar Informe'}
        </button>
      </div>
    </form>
  );
};

export default DateRangePicker;
