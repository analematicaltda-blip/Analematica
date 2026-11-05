
'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { toast } from 'react-toastify';
import api from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { FiShoppingCart, FiLoader } from 'react-icons/fi';

interface AddToCartButtonProps {
    planId: number;
}

export default function AddToCartButton({ planId }: AddToCartButtonProps) {
    const { user, isLoading: isAuthLoading } = useAuth();
    const [isAdding, setIsAdding] = useState(false);
    const router = useRouter();

    const handleAddToCart = async () => {
        if (!user) {
            toast.info('Por favor, inicia sesión para añadir planes a tu carro.');
            router.push('/dashboard/login');
            return;
        }

        setIsAdding(true);
        try {
            await api.post('/cart/add-item/', {
                plan_id: planId,
                quantity: 1,
            });
            toast.success('¡Plan añadido al carro!');
            router.push('/checkout'); // Redirigir al checkout después de añadir
        } catch (error) {
            toast.error('Error al añadir el plan al carro.');
            console.error(error);
        } finally {
            setIsAdding(false);
        }
    };

    return (
        <Button onClick={handleAddToCart} disabled={isAdding || isAuthLoading} className="w-full">
            {isAdding ? (
                <FiLoader className="animate-spin mr-2" />
            ) : (
                <FiShoppingCart className="mr-2 h-4 w-4" />
            )}
            {isAdding ? 'Añadiendo...' : 'Añadir al Carro'}
        </Button>
    );
}
