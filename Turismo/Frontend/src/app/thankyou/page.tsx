
import { Button } from '@/components/ui/Button';
import Link from 'next/link';
import { FiCheckCircle } from 'react-icons/fi';

export default function ThankYouPage() {
    return (
        <div className="flex flex-col items-center justify-center min-h-screen text-center bg-gray-50">
            <FiCheckCircle className="w-24 h-24 text-green-500 mb-6" />
            <h1 className="text-4xl font-bold mb-4">¡Gracias por tu compra!</h1>
            <p className="text-lg text-gray-600 mb-8">
                Hemos iniciado el proceso para activar tu suscripción. Recibirás una confirmación por correo electrónico en breve.
            </p>
            <Button asChild>
                <Link href="/dashboard">Ir a mi Panel</Link>
            </Button>
        </div>
    );
}
