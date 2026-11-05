'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { toast } from 'react-toastify';
import api from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import { FiTrash2 } from 'react-icons/fi';

interface Plan {
    id: number;
    nombre: string;
    precio: string;
}

interface CartItem {
    id: number;
    plan: Plan;
    quantity: number;
    total_price: number;
}

interface Cart {
    items: CartItem[];
    total_cart_price: number;
}

export default function CheckoutPage() {
    const { user, isLoading: isAuthLoading } = useAuth();
    const [cart, setCart] = useState<Cart | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isProcessingPayment, setIsProcessingPayment] = useState(false);

    const handleInitiatePayment = async () => {
        setIsProcessingPayment(true);
        try {
            const response = await api.post('/payments/init/', { provider: 'wompi' }); // Usamos 'wompi' como ejemplo
            toast.success(`Iniciando proceso de pago ID: ${response.data.id}`);
            // En una implementación real, aquí se redirigiría a la pasarela de pago.
            // Por ahora, solo mostramos una notificación.
        } catch (error) {
            toast.error('No se pudo iniciar el proceso de pago.');
        } finally {
            setIsProcessingPayment(false);
        }
    };

    const fetchCart = useCallback(async () => {
        if (!user) return;
        try {
            setIsLoading(true);
            const response = await api.get('/cart/view/');
            setCart(response.data);
        } catch (error) {
            toast.error('No se pudo cargar el carro de compras.');
        } finally {
            setIsLoading(false);
        }
    }, [user]);

    useEffect(() => {
        if (!isAuthLoading) {
            fetchCart();
        }
    }, [isAuthLoading, fetchCart]);

    // Aquí iría la lógica para eliminar ítems

    if (isLoading || isAuthLoading) {
        return <p>Cargando carro de compras...</p>;
    }

    if (!user) {
        return <p>Por favor, inicia sesión para ver tu carro.</p>;
    }

    if (!cart || cart.items.length === 0) {
        return (
            <div className="container mx-auto px-4 py-8 text-center">
                 <h1 className="text-3xl font-bold mb-4">Carro de Compras</h1>
                 <p>Tu carro está vacío.</p>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold mb-8">Carro de Compras</h1>
            <div className="grid md:grid-cols-3 gap-8">
                <div className="md:col-span-2 space-y-4">
                    {cart.items.map(item => (
                        <Card key={item.id}>
                            <CardContent className="flex items-center justify-between p-4">
                                <div>
                                    <h3 className="font-semibold">{item.plan.nombre}</h3>
                                    <p className="text-sm text-gray-500">Cantidad: {item.quantity}</p>
                                </div>
                                <div className="flex items-center gap-4">
                                    <p className="font-semibold">${item.total_price}</p>
                                    <Button variant="ghost" size="sm">
                                        <FiTrash2 className="h-4 w-4" />
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
                <div>
                    <Card>
                        <CardHeader>
                            <CardTitle>Resumen del Pedido</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex justify-between">
                                <span>Subtotal</span>
                                <span>${cart.total_cart_price}</span>
                            </div>
                            <div className="flex justify-between font-bold text-lg">
                                <span>Total</span>
                                <span>${cart.total_cart_price}</span>
                            </div>
                            <Button className="w-full" onClick={handleInitiatePayment} disabled={isProcessingPayment}>
                                {isProcessingPayment ? 'Procesando...' : 'Proceder al Pago'}
                            </Button>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
