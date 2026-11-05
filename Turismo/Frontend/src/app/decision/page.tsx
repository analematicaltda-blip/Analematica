
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import Link from 'next/link';
import { FiCheckCircle } from 'react-icons/fi';
import AddToCartButton from './AddToCartButton'; // Componente cliente que crearemos

interface Plan {
    id: number;
    nombre: string;
    descripcion: string;
    precio: string;
    frecuencia: string;
    tipo_usuario_objetivo: string;
}

async function getPlans(): Promise<Plan[]> {
    try {
        const res = await fetch('http://localhost:8000/api/admin/plataforma/planes/', {
            cache: 'no-store',
        });
        if (!res.ok) return [];
        const data = await res.json();
        return data.results.filter((plan: any) => plan.is_active);
    } catch (error) {
        console.error('Failed to fetch plans:', error);
        return [];
    }
}

export default async function DecisionPage() {
    const plans = await getPlans();

    return (
        <div className="container mx-auto px-4 py-12">
            <div className="text-center mb-12">
                <h1 className="text-4xl font-bold">Elige el Plan Perfecto para Ti</h1>
                <p className="text-lg text-gray-600 mt-4">Soluciones diseñadas para potenciar tu negocio turístico.</p>
            </div>

            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
                {plans.length > 0 ? (
                    plans.map(plan => (
                        <Card key={plan.id} className="flex flex-col">
                            <CardHeader>
                                <CardTitle>{plan.nombre}</CardTitle>
                                <CardDescription>{plan.tipo_usuario_objetivo.replace('_', ' ')}</CardDescription>
                            </CardHeader>
                            <CardContent className="flex-grow">
                                <p className="text-4xl font-bold mb-4">${plan.precio} <span className="text-lg font-normal text-gray-500">/{plan.frecuencia.toLowerCase()}</span></p>
                                <p className="text-gray-600 mb-6">{plan.descripcion}</p>
                                <ul className="space-y-2 text-sm text-gray-600">
                                    <li className="flex items-center"><FiCheckCircle className="text-green-500 mr-2" /> Característica 1</li>
                                    <li className="flex items-center"><FiCheckCircle className="text-green-500 mr-2" /> Característica 2</li>
                                    <li className="flex items-center"><FiCheckCircle className="text-green-500 mr-2" /> Característica 3</li>
                                </ul>
                            </CardContent>
                            <CardFooter>
                                <AddToCartButton planId={plan.id} />
                            </CardFooter>
                        </Card>
                    ))
                ) : (
                    <p className="col-span-full text-center text-gray-500">No hay planes disponibles en este momento.</p>
                )}
            </div>
        </div>
    );
}
