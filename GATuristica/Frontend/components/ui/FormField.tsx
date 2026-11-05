'use client';

import React from 'react';
import { UseFormRegister, FieldErrors, RegisterOptions, FieldValues, Path } from 'react-hook-form';

interface FormFieldProps<T extends FieldValues> {
  name: Path<T>;
  label: string;
  type?: string;
  register: UseFormRegister<T>;
  errors: FieldErrors<T>;
  required?: boolean;
  validation?: RegisterOptions;
  autoComplete?: string;
  disabled?: boolean;
}

const FormField = <T extends FieldValues>({
  name,
  label,
  type = 'text',
  register,
  errors,
  required = false,
  validation = {},
  autoComplete,
  disabled = false,
}: FormFieldProps<T>) => {
  const error = errors[name];

  return (
    <div>
      <label htmlFor={name} className="block text-sm font-medium text-gray-700">
        {label}
      </label>
      <div className="mt-1">
        {type === 'textarea' ? (
          <textarea
            id={name}
            // @ts-expect-error: Incompatibilidad de tipos complejos en `validation`
            {...register(name, { required: required && 'Este campo es obligatorio.', ...validation })}
            rows={4}
            className={`w-full px-3 py-2 border rounded-md shadow-sm ${
              error ? 'border-red-500' : 'border-gray-300'
            } focus:outline-none focus:ring-blue-500 focus:border-blue-500`}
            autoComplete={autoComplete}
            disabled={disabled}
          />
        ) : (
          <input
            id={name}
            type={type}
            // @ts-expect-error: Incompatibilidad de tipos complejos en `validation`
            {...register(name, { required: required && 'Este campo es obligatorio.', ...validation })}
            className={`w-full px-3 py-2 border rounded-md shadow-sm ${
              error ? 'border-red-500' : 'border-gray-300'
            } focus:outline-none focus:ring-blue-500 focus:border-blue-500`}
            autoComplete={autoComplete}
            disabled={disabled}
          />
        )}
      </div>
      {error && <p className="mt-1 text-xs text-red-600">{error.message?.toString()}</p>}
    </div>
  );
};

export default FormField;