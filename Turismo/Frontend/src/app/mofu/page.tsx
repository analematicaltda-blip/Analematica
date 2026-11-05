
import { notFound } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import Link from 'next/link';

// --- Tipos de datos (reutilizados de page.tsx) ---
interface ContentBlock {
    id: number;
    content_type: 'text' | 'image' | 'video' | 'button';
    content: string;
    link: string | null;
    order: number;
}

interface Section {
    id: number;
    title: string;
    order: number;
    content_blocks: ContentBlock[];
}

interface WebPage {
    id: number;
    title: string;
    slug: string;
    is_published: boolean;
    sections: Section[];
}

// --- Función de Fetch (reutilizada de page.tsx) ---
async function getPageData(slug: string): Promise<WebPage | null> {
    try {
        const res = await fetch(`http://localhost:8000/api/web/public/pages/${slug}/`, {
            cache: 'no-store',
        });
        if (!res.ok) return null;
        return res.json();
    } catch (error) {
        console.error(`Failed to fetch page data for slug ${slug}:`, error);
        return null;
    }
}

// --- Componente de Renderizado (reutilizado de page.tsx) ---
function RenderContentBlock({ block }: { block: ContentBlock }) {
     switch (block.content_type) {
        case 'text':
            return <p className="text-gray-600 mb-4 whitespace-pre-line">{block.content}</p>;
        case 'button':
            return (
                <div className="my-6">
                    <Button asChild>
                        <Link href={block.link || '#'}>{block.content}</Link>
                    </Button>
                </div>
            );
        case 'image':
            return <img src={block.content} alt={block.link || ''} className="my-4 rounded-lg shadow-md" />;
        default:
            return null;
    }
}


// --- Página MOFU ---
export default async function MofuPage() {
    const pageData = await getPageData('consideracion');

    if (!pageData) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen text-center">
                <h1 className="text-4xl font-bold">Página en Construcción</h1>
                 <p className="mt-2 text-sm text-gray-500">
                    (No se encontró una página con el slug "consideracion")
                </p>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-4xl font-bold text-center mb-12">{pageData.title}</h1>

            {pageData.sections.sort((a, b) => a.order - b.order).map(section => (
                <Card key={section.id} className="mb-8">
                    <CardHeader>
                        <CardTitle>{section.title}</CardTitle>
                    </CardHeader>
                    <CardContent>
                        {section.content_blocks.sort((a, b) => a.order - b.order).map(block => (
                            <RenderContentBlock key={block.id} block={block} />
                        ))}
                    </CardContent>
                </Card>
            ))}
        </div>
    );
}
