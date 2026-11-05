
import { Funnel, Block, LandingPageBlockType, CadenaTurismo, Categoria, Subcategoria, BlockStyles, FunnelPage, FunnelPageType, Asset } from '../../types';
import * as Icons from '../icons';

export const cadenas: CadenaTurismo[] = [
    { id: 'cad-restaurantes', nombre: 'Restaurantes', color_primario: '#d97706', color_secundario: '#fef3c7' },
    { id: 'cad-hoteles', nombre: 'Hoteles', color_primario: '#0e7490', color_secundario: '#ecfeff' },
    { id: 'cad-bares', nombre: 'Bares y Discotecas', color_primario: '#a21caf', color_secundario: '#fdf2f8' },
    { id: 'cad-agencias', nombre: 'Agencias de Viajes', color_primario: '#1d4ed8', color_secundario: '#eef2ff' },
    { id: 'cad-guias', nombre: 'Guías de Turismo', color_primario: '#15803d', color_secundario: '#f0fdf4' },
    { id: 'cad-artesanias', nombre: 'Artesanías', color_primario: '#b45309', color_secundario: '#fff7ed' },
    { id: 'cad-transporte', nombre: 'Transporte Turístico', color_primario: '#475569', color_secundario: '#f1f5f9' },
];

export const categorias: Categoria[] = [
    // Restaurantes
    { id: 'cat-r-tradicional', cadenaId: 'cad-restaurantes', nombre: 'Comida Tradicional / Típica', icon: '🍛' },
    { id: 'cat-r-parrilla', cadenaId: 'cad-restaurantes', nombre: 'Parrilladas y Asaderos', icon: '🥩' },
    { id: 'cat-r-rapida', cadenaId: 'cad-restaurantes', nombre: 'Comida Rápida', icon: '🍔' },
    { id: 'cat-r-internacional', cadenaId: 'cad-restaurantes', nombre: 'Cocina Internacional', icon: '🍣' },
    { id: 'cat-r-saludable', cadenaId: 'cad-restaurantes', nombre: 'Restaurantes Saludables y Alternativos', icon: '🥗' },
    { id: 'cat-r-gourmet', cadenaId: 'cad-restaurantes', nombre: 'Restaurantes Gourmet', icon: '🧑‍🍳' },
    { id: 'cat-r-popular', cadenaId: 'cad-restaurantes', nombre: 'Restaurantes Populares o Corrientazos', icon: '🥘' },
    { id: 'cat-r-cafeteria', cadenaId: 'cad-restaurantes', nombre: 'Cafeterías y Panaderías', icon: '☕' },
    { id: 'cat-r-reposteria', cadenaId: 'cad-restaurantes', nombre: 'Reposterías y Pastelerías', icon: '🍰' },
    { id: 'cat-r-domicilio', cadenaId: 'cad-restaurantes', nombre: 'Restaurantes con Servicio a Domicilio', icon: '🛵' },
    // Hoteles
    { id: 'cat-h-clasificacion', cadenaId: 'cad-hoteles', nombre: 'Hoteles por Clasificación Tradicional', icon: '🛎️' },
    { id: 'cat-h-enfoque', cadenaId: 'cad-hoteles', nombre: 'Alojamientos por Tipo o Enfoque', icon: '🏕️' },
    { id: 'cat-h-especializados', cadenaId: 'cad-hoteles', nombre: 'Otros Tipos Especializados', icon: '🎯' },
    // Bares
    { id: 'cat-b-estilo', cadenaId: 'cad-bares', nombre: 'Bares por Estilo o Ambiente', icon: '🍻' },
    { id: 'cat-b-genero', cadenaId: 'cad-bares', nombre: 'Discotecas por Género Musical', icon: '💃' },
    { id: 'cat-b-otros', cadenaId: 'cad-bares', nombre: 'Otros tipos de establecimientos nocturnos', icon: '🕺' },
    // Agencias
    { id: 'cat-a-operacion', cadenaId: 'cad-agencias', nombre: 'Por tipo de operación', icon: '🧭' },
    { id: 'cat-a-especializacion', cadenaId: 'cad-agencias', nombre: 'Por especialización en el tipo de turismo', icon: '🧳' },
    // Guías
    { id: 'cat-g-servicio', cadenaId: 'cad-guias', nombre: 'Según el tipo de servicio', icon: '🗺️' },
    { id: 'cat-g-turismo', cadenaId: 'cad-guias', nombre: 'Según el tipo de turismo que realiza', icon: '🏞️' },
    { id: 'cat-g-formacion', cadenaId: 'cad-guias', nombre: 'Según nivel de formación y acreditación (Colombia)', icon: '📚' },
    // Artesanías
    { id: 'cat-art-material', cadenaId: 'cad-artesanias', nombre: 'Según el tipo de material utilizado', icon: '🎨' },
    { id: 'cat-art-producto', cadenaId: 'cad-artesanias', nombre: 'Según el tipo de producto o arte', icon: '🧑‍🎨' },
    { id: 'cat-art-uso', cadenaId: 'cad-artesanias', nombre: 'Según el uso o la función del producto', icon: '🏺' },
    { id: 'cat-art-region', cadenaId: 'cad-artesanias', nombre: 'Según la región o cultura', icon: '🖼️' },
    // Transporte
    { id: 'cat-t-terrestre', cadenaId: 'cad-transporte', nombre: 'Transportes terrestres', icon: '🚍' },
    { id: 'cat-t-acuatico', cadenaId: 'cad-transporte', nombre: 'Transportes acuáticos', icon: '🚢' },
    { id: 'cat-t-aereo', cadenaId: 'cad-transporte', nombre: 'Transportes aéreos', icon: '🛩️' },
    { id: 'cat-t-servicio', cadenaId: 'cad-transporte', nombre: 'Según el tipo de servicio', icon: '🤵' },
];

export const subcategorias: Subcategoria[] = [
    // Restaurantes > Comida Tradicional
    { id: 'sub-r-trad-regional', categoriaId: 'cat-r-tradicional', nombre: 'Cocina regional (ej. llanera, paisa, costeña)' },
    { id: 'sub-r-trad-colombiana', categoriaId: 'cat-r-tradicional', nombre: 'Comida colombiana tradicional' },
    { id: 'sub-r-trad-criolla', categoriaId: 'cat-r-tradicional', nombre: 'Comida criolla o casera' },
    { id: 'sub-r-trad-variada', categoriaId: 'cat-r-tradicional', nombre: 'Sancochos, asados, tamales, etc.' },
    // Hoteles > Enfoque
    { id: 'sub-h-enfoque-urbano', categoriaId: 'cat-h-enfoque', nombre: 'Hoteles Urbanos o Empresariales' },
    { id: 'sub-h-enfoque-turistico', categoriaId: 'cat-h-enfoque', nombre: 'Hoteles Turísticos o Vacacionales' },
    { id: 'sub-h-enfoque-hostales', categoriaId: 'cat-h-enfoque', nombre: 'Hostales' },
    { id: 'sub-h-enfoque-residencias', categoriaId: 'cat-h-enfoque', nombre: 'Residencias o Hospedajes Familiares' },
    { id: 'sub-h-enfoque-glamping', categoriaId: 'cat-h-enfoque', nombre: 'Glamping' },
    { id: 'sub-h-enfoque-cabanas', categoriaId: 'cat-h-enfoque', nombre: 'Cabañas y Fincas Turísticas' },
    { id: 'sub-h-enfoque-apartahoteles', categoriaId: 'cat-h-enfoque', nombre: 'Apartahoteles / Alojamiento tipo Airbnb' },
    { id: 'sub-h-enfoque-ecohoteles', categoriaId: 'cat-h-enfoque', nombre: 'Ecohoteles y Alojamiento Sostenible' },
];

export const createDefaultBlock = (type: LandingPageBlockType, order: number): Block => {
    const id = `blk-${Date.now()}-${Math.random()}`;
    const defaultStyles: BlockStyles = {
        padding: { top: 80, right: 16, bottom: 80, left: 16 },
        backgroundColor: '#ffffff',
        textColor: '#0f172a',
        textAlign: 'left'
    };
    // FIX: Added 'props: {}' to initialize the props property on baseBlock.
    // This resolves the TypeScript error where the 'props' property was missing on the object literal
    // but required by its type definition.
    const baseBlock: Omit<Block, 'props'> & { props: any } = {
        id, type, name: `${type.charAt(0).toUpperCase() + type.slice(1)} Block`, order, locked: false, version: 1,
        template_id: null, created_at: new Date().toISOString(), updated_at: new Date().toISOString(),
        responsive: { desktop: { overrides: {} }, tablet: { overrides: {} }, mobile: { overrides: { stack: true } } },
        styles: defaultStyles,
        props: {},
    };
    switch (type) {
        case 'hero':
            baseBlock.props = {
                title: { value: 'Comunica tu Beneficio Principal', type: 'string', label: 'Título', category: 'content' },
                subtitle: { value: 'Captura la atención con una frase impactante.', type: 'longtext', label: 'Subtítulo', category: 'content' },
                backgroundImage: { value: 'https://images.unsplash.com/photo-1507525428034-b723a9ce6890?q=80&w=2070&auto=format&fit=crop', type: 'image', label: 'Imagen de Fondo', category: 'style' },
                ctaText: { value: 'Llamada a la Acción', type: 'string', label: 'Texto del Botón', category: 'content' },
                ctaUrl: { value: '#', type: 'url', label: 'URL del Botón', category: 'setting' },
            }; 
            baseBlock.styles.textAlign = 'center';
            baseBlock.styles.textColor = '#ffffff';
            baseBlock.styles.padding = { top: 240, right: 16, bottom: 240, left: 16 };
            break;
        case 'services':
             baseBlock.props = {
                title: { value: 'Nuestros Servicios', type: 'string', label: 'Título Principal', category: 'content' },
                items: { value: [
                    { id: 'serv-1', icon: 'SparklesIcon', title: 'Servicio Innovador', description: 'Solucionamos un problema real.'},
                    { id: 'serv-2', icon: 'RocketLaunchIcon', title: 'Servicio Rápido', description: 'Enfocado en la velocidad y eficiencia.'},
                    { id: 'serv-3', icon: 'CheckCircleIcon', title: 'Servicio Confiable', description: 'Garantía de calidad y soporte.'}
                ], type: 'array:object', label: 'Servicios', options: {
                     itemSchema: {
                        icon: { type: 'icon', label: 'Icono', category: 'content' },
                        title: { type: 'string', label: 'Título', category: 'content' },
                        description: { type: 'longtext', label: 'Descripción', category: 'content' }
                    }
                }, category: 'content'},
            }; 
            baseBlock.styles.textAlign = 'center';
            break;
        case 'gallery':
            baseBlock.props = {
                title: { value: 'Nuestra Galería', type: 'string', label: 'Título', category: 'content' },
                images: { value: Array.from({length: 6}, (_, i) => `https://picsum.photos/seed/${i+10}/600/400`), type: 'array:image', label: 'Imágenes', category: 'content' },
            }; 
            baseBlock.styles.textAlign = 'center';
            break;
        case 'testimonials':
            baseBlock.props = {
                title: { value: 'Lo que dicen nuestros clientes', type: 'string', label: 'Título', category: 'content' },
                testimonials: {
                    value: [
                        { id: 'test-1', avatarUrl: 'https://randomuser.me/api/portraits/women/68.jpg', name: 'Ana Gómez', role: 'CEO, Innovatech', quote: 'Esta plataforma ha transformado nuestro flujo de trabajo.' },
                        { id: 'test-2', avatarUrl: 'https://randomuser.me/api/portraits/men/75.jpg', name: 'Marco Vega', role: 'CTO, Quantum Dynamics', quote: 'La mejor inversión que hemos hecho este año. El soporte es increíble.' },
                        { id: 'test-3', avatarUrl: 'https://randomuser.me/api/portraits/women/71.jpg', name: 'Elena Rodriguez', role: 'Marketing Manager', quote: 'Una herramienta indispensable para cualquier equipo.' },
                    ], type: 'array:object', label: 'Testimonios', options: {
                        itemSchema: {
                            avatarUrl: { type: 'image', label: 'URL del Avatar', category: 'content' },
                            name: { type: 'string', label: 'Nombre', category: 'content' },
                            role: { type: 'string', label: 'Cargo/Empresa', category: 'content' },
                            quote: { type: 'longtext', label: 'Cita', category: 'content' },
                        }
                    }, category: 'content'
                }
            };
            baseBlock.styles.textAlign = 'center';
            break;
        default:
            baseBlock.props = { placeholder: { value: `Contenido para el bloque '${type}'`, type: 'string', label: 'Contenido', category: 'content' } };
    }
    return baseBlock as Block;
};

export const createDefaultFunnelPage = (type: FunnelPageType, name: string): FunnelPage => {
    const blocks: Block[] = type === 'offer' 
        ? [createDefaultBlock('hero', 1), createDefaultBlock('services', 2), createDefaultBlock('testimonials', 3), createDefaultBlock('gallery', 4)]
        : [createDefaultBlock('hero', 1)];
    return { id: `fp-${Date.now()}-${Math.random()}`, name, path: `/${name.toLowerCase().replace(/\s+/g, '-')}`, type, blocks, metaTitle: `Página de ${name}`, metaDescription: `Descripción para la página de ${name}` };
};

export const createDefaultFunnel = (landingPageId: string, name: string): Funnel => {
    return {
        id: `funnel-${Date.now()}-${Math.random()}`,
        landingPageId,
        name,
        pages: [
            createDefaultFunnelPage('offer', 'Página de Oferta'),
            createDefaultFunnelPage('thankyou', 'Página de Gracias')
        ],
        theme: {
            font: { headings: 'Inter', body: 'Inter' },
            colors: { primary: '#0e7490', secondary: '#ecfeff', accent: '#f59e0b', text: '#082f49' }
        }
    };
};

export const initialAllData = {
    cadenas,
    categorias,
    subcategorias,
    mediaLibrary: [
        { id: 'img-1', url: 'https://images.unsplash.com/photo-1507525428034-b723a9ce6890?q=80&w=2070&auto=format&fit=crop', name: 'Playa Amanecer', type: 'image' },
        { id: 'img-2', url: 'https://images.unsplash.com/photo-1471922694854-ff1b63b20054?q=80&w=2072&auto=format&fit=crop', name: 'Costa Rocosa', type: 'image' },
        { id: 'img-3', url: 'https://images.unsplash.com/photo-1532926381893-7542298edf1d?q=80&w=2070&auto=format&fit=crop', name: 'Piscina Hotel', type: 'image' },
        { id: 'img-4', url: 'https://picsum.photos/seed/10/600/400', name: 'Abstract 1', type: 'image'},
        { id: 'img-5', url: 'https://picsum.photos/seed/11/600/400', name: 'Abstract 2', type: 'image'},
        { id: 'img-6', url: 'https://picsum.photos/seed/12/600/400', name: 'Abstract 3', type: 'image'},
    ] as Asset[],
    landingPages: [
        { id: 'lp-h1', subcategoriaId: 'sub-h-enfoque-ecohoteles', nombre: 'Landing Principal Ecohotel', publicada: true, funnels: [
            { id: 'funnel-h1', landingPageId: 'lp-h1', name: 'Reservas Ecohotel', pages: [ createDefaultFunnelPage('offer', 'Oferta Eco'), createDefaultFunnelPage('thankyou', 'Gracias Eco') ], theme: { font: { headings: 'Inter', body: 'Inter' }, colors: { primary: '#0e7490', secondary: '#ecfeff', accent: '#f59e0b', text: '#082f49' }} },
            createDefaultFunnel('lp-h1', 'Embudo de Prueba')
        ]},
        { id: 'lp-r1', subcategoriaId: 'sub-r-trad-regional', nombre: 'Landing Asados Llaneros', publicada: true, funnels: [
            { id: 'funnel-r1', landingPageId: 'lp-r1', name: 'Reservas Parrillada', pages: [ createDefaultFunnelPage('offer', 'Menú Parrilla'), createDefaultFunnelPage('thankyou', 'Gracias Parrilla') ], theme: { font: { headings: 'Inter', body: 'Inter' }, colors: { primary: '#d97706', secondary: '#fef3c7', accent: '#16a34a', text: '#451a03' }}}
        ]},
    ]
};

export const availableBlocks: { type: LandingPageBlockType; icon: React.FC<{className?: string}>; name: string }[] = [
    { type: 'hero', icon: Icons.SparklesIcon, name: 'Hero' }, { type: 'services', icon: Icons.Cog6ToothIcon, name: 'Servicios' },
    { type: 'gallery', icon: Icons.PhotoIcon, name: 'Galería' }, { type: 'testimonials', icon: Icons.ChatBubbleBottomCenterTextIcon, name: 'Testimonios' },
    { type: 'pricing', icon: Icons.CreditCardIcon, name: 'Precios' }, { type: 'faq', icon: Icons.QuestionMarkCircleIcon, name: 'FAQ' },
    { type: 'cta', icon: Icons.CursorArrowRaysIcon, name: 'CTA' }, { type: 'form', icon: Icons.FormIcon, name: 'Formulario' },
    { type: 'video', icon: Icons.VideoCameraIcon, name: 'Video' }, { type: 'countdown', icon: Icons.ClockIcon, name: 'Cuenta Regresiva' },
    { type: 'footer', icon: Icons.CodeBracketIcon, name: 'Pie de Página' },
];

export const ItemTypes = { BLOCK: 'block', LIBRARY_BLOCK: 'library_block', PROP_ITEM: 'prop_item' };
