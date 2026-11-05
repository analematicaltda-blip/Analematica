"use client";

import { useForm, FormProvider } from "react-hook-form";
import { PageHeader } from '@/components/shared/page-header';
import { Button } from '@/components/ui/Button';

// --- Componentes Anidados (Placeholders) ---

const TourRequirementsEditor = () => (
    <div className="p-4 border rounded-md bg-gray-50">
        <h4 className="font-semibold">Requisitos del Guía (Próximamente)</h4>
    </div>
);

const ItineraryEditor = () => (
    <div className="p-4 border rounded-md bg-gray-50">
        <h4 className="font-semibold">Editor de Itinerario (Próximamente)</h4>
    </div>
);

// --- Formulario Principal ---

export default function GuideManagementPage() {
    const methods = useForm(); // Formulario principal

    const onSubmit = (data: any) => {
        console.log("Datos del Tour:", data);
        // Aquí iría la lógica de mutación para crear/actualizar el tour
    };

    return (
        <div className="flex flex-col gap-8">
            <PageHeader
                title="Gestión de Guías y Tours"
                description="Diseñe sus expediciones, defina itinerarios y asigne a los guías más calificados."
            />

            <FormProvider {...methods}>
                <form onSubmit={methods.handleSubmit(onSubmit)} className="space-y-6 p-4 border rounded-lg bg-white">
                    <h2 className="text-xl font-bold">Crear/Editar Tour</h2>

                    {/* Inputs básicos del producto */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <input {...methods.register("name", { required: true })} placeholder="Nombre del Tour" className="p-2 border rounded" />
                        <input type="number" {...methods.register("base_price", { required: true })} placeholder="Precio Base" className="p-2 border rounded" />
                    </div>

                    <textarea {...methods.register("description")} placeholder="Descripción del tour..." className="w-full p-2 border rounded" />

                    {/* Componentes anidados */}
                    <TourRequirementsEditor />
                    <ItineraryEditor />

                    <Button type="submit">Guardar Tour</Button>
                </form>
            </FormProvider>
        </div>
    );
}
