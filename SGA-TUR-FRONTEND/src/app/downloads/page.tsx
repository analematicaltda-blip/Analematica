
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import Link from 'next/link';
import { FiDownload } from 'react-icons/fi';

interface DownloadLink {
    id: number;
    nombre: string;
    plataforma: string;
    url: string;
    version: string;
}

async function getDownloadLinks(): Promise<DownloadLink[]> {
    try {
        const res = await fetch('http://localhost:8000/api/downloads/public/links/', {
            cache: 'no-store',
        });
        if (!res.ok) {
            return [];
        }
        const data = await res.json();
        return data.results || [];
    } catch (error) {
        console.error('Failed to fetch download links:', error);
        return [];
    }
}

export default async function DownloadsPage() {
    const links = await getDownloadLinks();

    const groupedLinks = links.reduce((acc, link) => {
        const platform = link.plataforma;
        if (!acc[platform]) {
            acc[platform] = [];
        }
        acc[platform].push(link);
        return acc;
    }, {} as Record<string, DownloadLink[]>);

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-4xl font-bold text-center mb-12">Centro de Descargas</h1>

            {Object.keys(groupedLinks).length > 0 ? (
                <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
                    {Object.entries(groupedLinks).map(([platform, platformLinks]) => (
                        <Card key={platform}>
                            <CardHeader>
                                <CardTitle className="capitalize">{platform.toLowerCase().replace('_', ' ')}</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                {platformLinks.map(link => (
                                    <div key={link.id} className="flex items-center justify-between p-2 border rounded-lg">
                                        <div>
                                            <p className="font-semibold">{link.nombre}</p>
                                            <p className="text-sm text-gray-500">Versión {link.version || 'N/A'}</p>
                                        </div>
                                        <Button asChild>
                                            <a href={link.url} target="_blank" rel="noopener noreferrer">
                                                <FiDownload className="mr-2 h-4 w-4" />
                                                Descargar
                                            </a>
                                        </Button>
                                    </div>
                                ))}
                            </CardContent>
                        </Card>
                    ))}
                </div>
            ) : (
                <div className="text-center text-gray-500">
                    <p>No hay enlaces de descarga disponibles en este momento.</p>
                </div>
            )}
        </div>
    );
}
