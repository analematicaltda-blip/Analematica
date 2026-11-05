import React, { useState, useCallback, useEffect, useRef } from 'react';
import { generateImage, editImage, generateVideo, pollVideoOperation, generateText, generateTextFromBackend } from '../services/geminiService';
import { LoadingSpinner, MediaIcon, CalendarIcon, SparklesIcon, FacebookIcon, InstagramIcon, TikTokIcon, YouTubeIcon, XIcon } from './icons';
import { useSettings } from '../context/SettingsContext';
import PlatformFormatSelector from './PlatformFormatSelector';
import { ContentToSchedule, SelectedPlatforms, PlatformID } from '../types';

// Helper to convert file to base64
const fileToBase64 = (file: File): Promise<{base64: string, mimeType: string}> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
        const result = reader.result as string;
        const mimeType = result.split(',')[0].split(':')[1].split(';')[0];
        const base64 = result.split(',')[1];
        resolve({ base64, mimeType });
    };
    reader.onerror = error => reject(error);
  });
};

// --- CREATION COMPONENTS ---
const ImageGenerator: React.FC<{ onSchedule: (contentUrl: string, platforms: SelectedPlatforms) => void }> = ({ onSchedule }) => {
  const [prompt, setPrompt] = useState('');
  const [image, setImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedPlatforms, setSelectedPlatforms] = useState<SelectedPlatforms>({});

  const handleGenerate = async () => {
    if (!prompt) return;
    setIsLoading(true);
    setImage(null);
    const result = await generateImage(prompt);
    setImage(result);
    setIsLoading(false);
  };

  const handleSchedule = () => {
    if (!image || Object.keys(selectedPlatforms).length === 0) {
        alert("Por favor, genera una imagen y selecciona al menos una red social y formato.");
        return;
    }
    onSchedule(image, selectedPlatforms);
  }

  return (
    <div className="bg-card p-6 rounded-lg shadow-lg border">
      <h3 className="text-xl font-bold mb-4">Creación de Imágenes</h3>
      <div className="flex space-x-2">
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Ej: Un astronauta surfeando en un cometa"
          className="flex-grow bg-input border border-border rounded-md p-2 text-foreground placeholder-muted-foreground focus:ring-primary focus:border-primary"
        />
        <button onClick={handleGenerate} disabled={isLoading || !prompt} className="bg-primary px-4 py-2 rounded-md hover:bg-primary/90 disabled:opacity-50 text-primary-foreground font-semibold">
          {isLoading ? <LoadingSpinner /> : 'Generar'}
        </button>
      </div>
      <div className="mt-4 h-64 bg-input rounded-md flex items-center justify-center">
        {isLoading && <LoadingSpinner className="w-10 h-10"/>}
        {image && <img src={image} alt="Generated" className="object-contain h-full w-full rounded-md" />}
        {!isLoading && !image && <p className="text-muted-foreground">La imagen aparecerá aquí</p>}
      </div>
      {image && !isLoading && (
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
            <PlatformFormatSelector selected={selectedPlatforms} onSelectionChange={setSelectedPlatforms} />
            <div className="flex justify-end h-full items-end">
                <button onClick={handleSchedule} disabled={Object.keys(selectedPlatforms).length === 0} className="flex items-center space-x-2 bg-green-600 px-4 py-2 rounded-md hover:opacity-90 disabled:opacity-50 text-white font-semibold">
                    <CalendarIcon className="w-5 h-5" />
                    <span>Programar Contenido</span>
                </button>
            </div>
        </div>
      )}
    </div>
  );
};

const ImageEditor: React.FC<{ onSchedule: (contentUrl: string, platforms: SelectedPlatforms) => void }> = ({ onSchedule }) => {
    const [originalImage, setOriginalImage] = useState<{file: File, url: string} | null>(null);
    const [editedImage, setEditedImage] = useState<string | null>(null);
    const [prompt, setPrompt] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [selectedPlatforms, setSelectedPlatforms] = useState<SelectedPlatforms>({});

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if(file) {
            setOriginalImage({ file, url: URL.createObjectURL(file) });
            setEditedImage(null);
        }
    };

    const handleEdit = async () => {
        if (!originalImage || !prompt) return;
        setIsLoading(true);
        setEditedImage(null);
        const { base64, mimeType } = await fileToBase64(originalImage.file);
        const result = await editImage(base64, mimeType, prompt);
        setEditedImage(result);
        setIsLoading(false);
    };

    const handleSchedule = () => {
        if (!editedImage || Object.keys(selectedPlatforms).length === 0) {
            alert("Por favor, edita una imagen y selecciona al menos una red social y formato.");
            return;
        }
        onSchedule(editedImage, selectedPlatforms);
    }

    return (
        <div className="bg-card p-6 rounded-lg shadow-lg border">
            <h3 className="text-xl font-bold mb-4">Edición de Imágenes</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label htmlFor="image-upload" className="block text-sm font-medium text-muted-foreground mb-1">Subir Imagen Original</label>
                    <input id="image-upload" type="file" accept="image/*" onChange={handleFileChange} className="w-full text-sm text-muted-foreground file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary/10 file:text-primary hover:file:opacity-80 cursor-pointer"/>
                    <div className="mt-2 h-64 bg-input rounded-md flex items-center justify-center">
                        {originalImage ? <img src={originalImage.url} alt="Original" className="object-contain h-full w-full rounded-md"/> : <p className="text-muted-foreground">Vista previa</p>}
                    </div>
                </div>
                <div>
                    <label htmlFor="edit-prompt" className="block text-sm font-medium text-muted-foreground mb-1">Instrucción de Edición</label>
                     <input
                        id="edit-prompt"
                        type="text"
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        placeholder="Ej: Añade un filtro retro"
                        className="w-full bg-input border border-border rounded-md p-2 text-foreground placeholder-muted-foreground focus:ring-primary focus:border-primary mb-2"
                    />
                    <div className="mt-2 h-64 bg-input rounded-md flex items-center justify-center">
                         {isLoading && <LoadingSpinner className="w-10 h-10"/>}
                         {editedImage && <img src={editedImage} alt="Edited" className="object-contain h-full w-full rounded-md" />}
                        {!isLoading && !editedImage && <p className="text-muted-foreground">La imagen editada aparecerá aquí</p>}
                    </div>
                </div>
            </div>
             <div className="mt-4 flex justify-end">
                <button onClick={handleEdit} disabled={isLoading || !originalImage || !prompt} className="bg-primary px-4 py-2 rounded-md hover:bg-primary/90 disabled:opacity-50 text-primary-foreground font-semibold">
                    {isLoading ? <LoadingSpinner /> : 'Aplicar Edición'}
                </button>
            </div>
             {editedImage && !isLoading && (
                <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
                    <PlatformFormatSelector selected={selectedPlatforms} onSelectionChange={setSelectedPlatforms} />
                    <div className="flex justify-end h-full items-end">
                        <button onClick={handleSchedule} disabled={Object.keys(selectedPlatforms).length === 0} className="flex items-center space-x-2 bg-green-600 px-4 py-2 rounded-md hover:opacity-90 disabled:opacity-50 text-white font-semibold">
                            <CalendarIcon className="w-5 h-5" />
                            <span>Programar Contenido</span>
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

const VideoGenerator: React.FC<{ onSchedule: (contentUrl: string, platforms: SelectedPlatforms) => void }> = ({ onSchedule }) => {
    const [image, setImage] = useState<{file: File, url: string} | null>(null);
    const [prompt, setPrompt] = useState('');
    const [aspectRatio, setAspectRatio] = useState<'16:9' | '9:16'>('16:9');
    const [videoUrl, setVideoUrl] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [loadingMessage, setLoadingMessage] = useState('');
    const [apiKeySelected, setApiKeySelected] = useState(false);
    const [selectedPlatforms, setSelectedPlatforms] = useState<SelectedPlatforms>({});
    const pollInterval = useRef<number | null>(null);

    const checkApiKey = useCallback(async () => {
        if(window.aistudio?.hasSelectedApiKey) {
            const hasKey = await window.aistudio.hasSelectedApiKey();
            setApiKeySelected(hasKey);
        } else {
            setApiKeySelected(true);
        }
    }, []);

    useEffect(() => {
        checkApiKey();
        return () => {
            if(pollInterval.current) clearInterval(pollInterval.current);
        };
    }, [checkApiKey]);

    const handleSelectKey = async () => {
        if(window.aistudio?.openSelectKey) {
            await window.aistudio.openSelectKey();
            setApiKeySelected(true);
        }
    };
    
    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if(file) {
            setImage({ file, url: URL.createObjectURL(file) });
            setVideoUrl(null);
        }
    };

    const handleSchedule = () => {
        if (!videoUrl || Object.keys(selectedPlatforms).length === 0) {
            alert("Por favor, genera un video y selecciona al menos una red social y formato.");
            return;
        }
        onSchedule(videoUrl, selectedPlatforms);
    }

    const handleGenerate = async () => {
        if (!image || !prompt) return;

        setIsLoading(true);
        setVideoUrl(null);
        setLoadingMessage('Iniciando la generación del video...');
        
        try {
            const { base64, mimeType } = await fileToBase64(image.file);
            let operation = await generateVideo(base64, mimeType, prompt, aspectRatio);
            setLoadingMessage('Operación iniciada. El video puede tardar varios minutos en generarse. Comprobando estado...');

            pollInterval.current = window.setInterval(async () => {
                try {
                    operation = await pollVideoOperation(operation);
                    if (operation.done) {
                        if(pollInterval.current) clearInterval(pollInterval.current);
                        const downloadLink = operation.response?.generatedVideos?.[0]?.video?.uri;
                        if(downloadLink) {
                            const response = await fetch(`${downloadLink}&key=${process.env.API_KEY}`);
                            const blob = await response.blob();
                            setVideoUrl(URL.createObjectURL(blob));
                            setLoadingMessage('¡Video generado con éxito!');
                            setIsLoading(false);
                        } else {
                            setLoadingMessage('Error: No se encontró el video en la respuesta.');
                            setIsLoading(false);
                        }
                    } else {
                        setLoadingMessage('Generando video... por favor espere.');
                    }
                } catch(pollError: any) {
                    if (pollError.message?.includes("Requested entity was not found")) {
                        setLoadingMessage("Error de clave de API. Por favor, seleccione una clave válida.");
                        setApiKeySelected(false);
                    } else {
                        setLoadingMessage(`Error al comprobar el estado: ${pollError.message}`);
                    }
                    if(pollInterval.current) clearInterval(pollInterval.current);
                    setIsLoading(false);
                }
            }, 10000);

        } catch (error: any) {
            if (error.message?.includes("API key not valid")) {
                setLoadingMessage("Error de clave de API. Por favor, seleccione una clave válida.");
                setApiKeySelected(false);
            } else {
                setLoadingMessage(`Error al iniciar la generación: ${error.message}`);
            }
            setIsLoading(false);
        }
    };

    if(!apiKeySelected) {
        return (
            <div className="bg-card p-6 rounded-lg shadow-lg text-center border">
                 <h3 className="text-xl font-bold mb-4">Creación de Video (Veo)</h3>
                 <p className="mb-4 text-muted-foreground">Para usar la generación de video, debe seleccionar una clave de API. <a href="https://ai.google.dev/gemini-api/docs/billing" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">Información de facturación</a></p>
                 <button onClick={handleSelectKey} className="bg-primary px-4 py-2 rounded-md hover:bg-primary/90 text-primary-foreground font-semibold">
                    Seleccionar Clave de API
                 </button>
            </div>
        )
    }

    return (
        <div className="bg-card p-6 rounded-lg shadow-lg border">
            <h3 className="text-xl font-bold mb-4">Creación de Video (Veo)</h3>
            <div className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-muted-foreground mb-1">Subir Imagen Inicial</label>
                    <input type="file" accept="image/*" onChange={handleFileChange} className="w-full text-sm text-muted-foreground file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary/10 file:text-primary hover:file:opacity-80 cursor-pointer"/>
                </div>
                <div>
                    <label className="block text-sm font-medium text-muted-foreground mb-1">Prompt del Video</label>
                    <input type="text" value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder="Ej: La imagen cobra vida y la cámara se aleja lentamente" className="w-full bg-input border border-border rounded-md p-2" />
                </div>
                <div>
                    <label className="block text-sm font-medium text-muted-foreground mb-1">Relación de Aspecto</label>
                    <select value={aspectRatio} onChange={(e) => setAspectRatio(e.target.value as '16:9' | '9:16')} className="w-full bg-input border border-border rounded-md p-2">
                        <option value="16:9">16:9 (Horizontal)</option>
                        <option value="9:16">9:16 (Vertical)</option>
                    </select>
                </div>
                 <div className="flex justify-end">
                    <button onClick={handleGenerate} disabled={isLoading || !image || !prompt} className="bg-primary px-4 py-2 rounded-md hover:bg-primary/90 disabled:opacity-50 text-primary-foreground font-semibold">
                        {isLoading ? <LoadingSpinner /> : 'Generar Video'}
                    </button>
                </div>
            </div>
            <div className="mt-4 h-80 bg-input rounded-md flex flex-col items-center justify-center p-4">
                {isLoading && <><LoadingSpinner className="w-10 h-10 mb-4"/><p className="text-muted-foreground text-center">{loadingMessage}</p></>}
                {videoUrl && <video src={videoUrl} controls className="max-h-full max-w-full rounded-md" />}
                {!isLoading && !videoUrl && image && <img src={image.url} alt="Preview" className="object-contain h-full w-full rounded-md" />}
                {!isLoading && !videoUrl && !image && <p className="text-muted-foreground">El video aparecerá aquí</p>}
            </div>
            {videoUrl && !isLoading && (
                 <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
                    <PlatformFormatSelector selected={selectedPlatforms} onSelectionChange={setSelectedPlatforms} />
                     <div className="flex justify-end h-full items-end">
                        <button onClick={handleSchedule} disabled={Object.keys(selectedPlatforms).length === 0} className="flex items-center space-x-2 bg-green-600 px-4 py-2 rounded-md hover:opacity-90 disabled:opacity-50 text-white font-semibold">
                            <CalendarIcon className="w-5 h-5" />
                            <span>Programar Contenido</span>
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

const CreationView: React.FC<{ onSchedule: (contentUrl: string, platforms: SelectedPlatforms) => void }> = ({ onSchedule }) => {
    const { provider } = useSettings();

    if (provider === 'ollama') {
        return (
            <div className="h-full flex flex-col items-center justify-center text-center">
                <MediaIcon className="w-16 h-16 text-muted-foreground mb-4" />
                <h2 className="text-2xl font-bold text-foreground mb-2">Funcionalidad No Disponible</h2>
                <p className="text-muted-foreground max-w-md">
                    La creación y edición de contenido multimedia (imágenes y video) son funciones avanzadas que requieren el proveedor de IA de Google Gemini.
                </p>
                <p className="text-muted-foreground max-w-md mt-2">
                    Por favor, cambie al proveedor 'Gemini' en la pantalla de <span className="font-bold text-primary">Ajustes</span> para utilizar este estudio de contenido.
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            <ImageGenerator onSchedule={onSchedule} />
            <ImageEditor onSchedule={onSchedule} />
            <VideoGenerator onSchedule={onSchedule} />
        </div>
    );
};


// --- SCHEDULER COMPONENT ---
interface ScheduledPost {
    id: number;
    content: string;
    dateTime: Date;
    targets: { platform: PlatformID; format: string }[];
}

const socialPlatformMap: { [key in PlatformID]: { name: string, icon: React.FC<{className?: string}> } } = {
    facebook: { name: 'Facebook', icon: FacebookIcon },
    instagram: { name: 'Instagram', icon: InstagramIcon },
    tiktok: { name: 'TikTok', icon: TikTokIcon },
    youtube: { name: 'YouTube', icon: YouTubeIcon },
    x: { name: 'X', icon: XIcon },
};

const getPlatformInfo = (platformId: PlatformID) => {
    return socialPlatformMap[platformId] || { name: 'Unknown', icon: () => null };
};

const SchedulerView: React.FC<{ initialContent: ContentToSchedule | null, onClearInitialContent: () => void }> = ({ initialContent, onClearInitialContent }) => {
  const [posts, setPosts] = useState<ScheduledPost[]>([]);
  const [postContent, setPostContent] = useState('');
  const [postDate, setPostDate] = useState(new Date().toISOString().split('T')[0]);
  const [postTime, setPostTime] = useState('10:00');
  const [selectedPlatforms, setSelectedPlatforms] = useState<SelectedPlatforms>({});
  const [isGenerating, setIsGenerating] = useState(false);
  const [campaignGoal, setCampaignGoal] = useState('');
  const [isGeneratingCampaign, setIsGeneratingCampaign] = useState(false);
  const { provider, ollamaEndpoint } = useSettings();
  const formRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (initialContent) {
        setPostContent(`Contenido generado por IA. Puedes previsualizarlo aquí: ${initialContent.contentUrl}`);
        setSelectedPlatforms(initialContent.selectedPlatforms);
        formRef.current?.scrollIntoView({ behavior: 'smooth' });
        onClearInitialContent();
    }
  }, [initialContent, onClearInitialContent]);

  const handleGenerateContent = async () => {
    setIsGenerating(true);
    const prompt = "Genera una idea para una publicación en redes sociales para una empresa de tecnología. Incluye un texto atractivo y algunos hashtags relevantes.";

    // Simulación del Auth Token
    const authToken = "simulated-auth-token"; // En una app real, esto vendría del estado de autenticación.

    // Llamada a la nueva función del backend
    const content = await generateTextFromBackend(prompt, authToken);

    setPostContent(content);
    setIsGenerating(false);
  };

  const handleGenerateCampaign = async () => {
    if (!campaignGoal) return;
    setIsGeneratingCampaign(true);
    const campaignPrompt = `Actúa como un estratega de marketing digital. Crea un plan de contenido para una campaña de una semana sobre el siguiente objetivo: "${campaignGoal}". Devuelve un calendario de 7 publicaciones en formato JSON. Cada publicación debe tener 'day' (número del 1 al 7), 'platform' (sugiere una de estas opciones: 'Instagram', 'Facebook', 'TikTok', 'YouTube', 'X'), 'content' (el texto de la publicación con hashtags), y 'media_suggestion' (una breve descripción de la imagen o video a usar). No incluyas nada más que el array JSON en tu respuesta.`;
    
    try {
        const model = provider === 'gemini' ? 'gemini-2.5-pro' : 'llama3';
        const result = await generateText(provider, { ollamaEndpoint, model }, campaignPrompt);
        const jsonString = result.replace(/```json/g, '').replace(/```/g, '').trim();
        const campaignPosts = JSON.parse(jsonString);

        const today = new Date();
        const scheduledPosts: ScheduledPost[] = campaignPosts.map((post: any) => {
            const postDate = new Date(today);
            postDate.setDate(today.getDate() + (post.day - 1));
            const platformId = (post.platform?.toLowerCase() ?? 'x') as PlatformID;
            return {
                id: Date.now() + Math.random(),
                content: `${post.content}\n\n[Sugerencia de Media: ${post.media_suggestion}]`,
                dateTime: new Date(`${postDate.toISOString().split('T')[0]}T${postTime}`),
                targets: [{ platform: platformId, format: 'post' }], // Defaulting campaign posts to 'post' format
            }
        });

        setPosts(prev => [...prev, ...scheduledPosts].sort((a, b) => a.dateTime.getTime() - b.dateTime.getTime()));
        setCampaignGoal('');
    } catch (e) {
        console.error("Failed to parse campaign JSON", e);
        alert("Hubo un error al generar la campaña. El modelo puede haber devuelto un formato inválido. Por favor, inténtalo de nuevo.");
    }
    setIsGeneratingCampaign(false);
  };

  const handleSchedulePost = (e: React.FormEvent) => {
    e.preventDefault();
    if (!postContent || !postDate || !postTime || Object.keys(selectedPlatforms).length === 0) return;
    
    const targets: { platform: PlatformID; format: string }[] = [];
    for (const platformId in selectedPlatforms) {
        const formats = selectedPlatforms[platformId as PlatformID]!;
        for (const format of formats) {
            targets.push({ platform: platformId as PlatformID, format });
        }
    }

    const newPost: ScheduledPost = {
      id: Date.now(),
      content: postContent,
      dateTime: new Date(`${postDate}T${postTime}`),
      targets: targets,
    };
    setPosts(prev => [...prev, newPost].sort((a, b) => a.dateTime.getTime() - b.dateTime.getTime()));
    setPostContent('');
    setSelectedPlatforms({});
  };

  return (
    <div className="flex gap-8 h-[calc(100vh-200px)]">
      {/* Scheduler Form */}
      <div ref={formRef} className="w-1/3 flex-shrink-0">
        <div className="bg-card rounded-lg p-6 shadow-2xl flex flex-col gap-6 h-full overflow-y-auto border">
          <div>
            <h3 className="text-xl font-bold mb-4">Programar Publicación</h3>
            <form onSubmit={handleSchedulePost} className="space-y-4">
              <div>
                <label htmlFor="postContent" className="block text-sm font-medium text-muted-foreground mb-1">Contenido</label>
                <textarea
                  id="postContent"
                  rows={5}
                  value={postContent}
                  onChange={(e) => setPostContent(e.target.value)}
                  className="w-full bg-input border border-border rounded-md p-2"
                  placeholder="Escribe el contenido o genéralo con IA"
                />
              </div>
              <button
                type="button"
                onClick={handleGenerateContent}
                disabled={isGenerating}
                className="w-full flex justify-center items-center bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 disabled:opacity-50"
              >
                {isGenerating ? <LoadingSpinner className="w-5 h-5"/> : <SparklesIcon className="w-5 h-5"/>}
                <span className="ml-2">Generar Contenido</span>
              </button>
              
              <PlatformFormatSelector selected={selectedPlatforms} onSelectionChange={setSelectedPlatforms} />

              <div className="flex gap-4">
                <div>
                  <label htmlFor="postDate" className="block text-sm font-medium text-muted-foreground mb-1">Fecha</label>
                  <input type="date" id="postDate" value={postDate} onChange={(e) => setPostDate(e.target.value)} className="w-full bg-input border border-border rounded-md p-2" />
                </div>
                <div>
                  <label htmlFor="postTime" className="block text-sm font-medium text-muted-foreground mb-1">Hora</label>
                  <input type="time" id="postTime" value={postTime} onChange={(e) => setPostTime(e.target.value)} className="w-full bg-input border border-border rounded-md p-2" />
                </div>
              </div>
              <button type="submit" className="w-full bg-green-600 text-white px-6 py-2 rounded-md hover:opacity-90 disabled:opacity-50" disabled={Object.keys(selectedPlatforms).length === 0 || !postContent}>Programar</button>
            </form>
          </div>
          <div className="border-t border-border pt-6">
            <h3 className="text-xl font-bold mb-4">Generador de Campañas con IA</h3>
             <div className="space-y-4">
                <div>
                    <label htmlFor="campaignGoal" className="block text-sm font-medium text-muted-foreground mb-1">Objetivo de la Campaña</label>
                    <textarea id="campaignGoal" rows={3} value={campaignGoal} onChange={(e) => setCampaignGoal(e.target.value)} className="w-full bg-input border border-border rounded-md p-2" placeholder="Ej: Lanzamiento de nueva línea de zapatillas veganas durante una semana." />
                </div>
                <button onClick={handleGenerateCampaign} disabled={isGeneratingCampaign || !campaignGoal} className="w-full flex justify-center items-center bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50">
                    {isGeneratingCampaign ? <LoadingSpinner className="w-5 h-5"/> : <SparklesIcon className="w-5 h-5"/>}
                    <span className="ml-2">Generar Campaña Completa</span>
                </button>
             </div>
          </div>
        </div>
      </div>

      {/* Calendar/Timeline View */}
      <div className="w-2/3 bg-card rounded-lg p-6 shadow-2xl overflow-y-auto border">
        <h3 className="text-xl font-bold mb-4">Cronograma de Publicaciones</h3>
        <div className="space-y-4">
          {posts.length > 0 ? posts.map(post => (
            <div key={post.id} className="bg-muted p-4 rounded-lg">
              <p className="font-bold text-primary mb-2">{post.dateTime.toLocaleString('es-ES', { dateStyle: 'full', timeStyle: 'short' })}</p>
              <div className="flex flex-wrap gap-2 mb-3">
                  {post.targets.map((target, index) => {
                      const { icon: Icon, name } = getPlatformInfo(target.platform);
                      return (
                          <div key={index} className="flex items-center space-x-2 bg-secondary px-2 py-1 rounded-full text-sm">
                              <Icon className="w-4 h-4 text-secondary-foreground" />
                              <span className="text-secondary-foreground font-medium">{name} - <span className="capitalize font-light">{target.format}</span></span>
                          </div>
                      )
                  })}
              </div>
              <p className="text-muted-foreground mt-2 whitespace-pre-wrap">{post.content}</p>
            </div>
          )) : (
            <div className="text-center text-muted-foreground py-16">
              <p>No hay publicaciones programadas.</p>
              <p>Usa el formulario para añadir una o generar una campaña completa.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};


// --- MAIN COMPONENT ---
const LevelAIStudio: React.FC = () => {
    const [activeTab, setActiveTab] = useState<'creation' | 'scheduler'>('creation');
    const [contentToSchedule, setContentToSchedule] = useState<ContentToSchedule | null>(null);

    const handleScheduleRequest = (contentUrl: string, selectedPlatforms: SelectedPlatforms) => {
        setContentToSchedule({ contentUrl, selectedPlatforms });
        setActiveTab('scheduler');
    };

    return (
        <div className="p-8 h-full flex flex-col">
            <div className="flex space-x-2 border-b border-border mb-6 flex-shrink-0">
                <button 
                    onClick={() => setActiveTab('creation')} 
                    className={`flex items-center space-x-2 py-2 px-4 font-medium transition-colors ${activeTab === 'creation' ? 'border-b-2 border-primary text-foreground' : 'text-muted-foreground hover:text-foreground'}`}>
                    <SparklesIcon className="w-5 h-5" /><span>Creación de Contenido</span>
                </button>
                <button 
                    onClick={() => setActiveTab('scheduler')} 
                    className={`flex items-center space-x-2 py-2 px-4 font-medium transition-colors ${activeTab === 'scheduler' ? 'border-b-2 border-primary text-foreground' : 'text-muted-foreground hover:text-foreground'}`}>
                    <CalendarIcon className="w-5 h-5" /><span>Programador</span>
                </button>
            </div>
            
            <div className="flex-1 overflow-y-auto">
                {activeTab === 'creation' 
                    ? <CreationView onSchedule={handleScheduleRequest} /> 
                    : <SchedulerView initialContent={contentToSchedule} onClearInitialContent={() => setContentToSchedule(null)} />
                }
            </div>
        </div>
    );
};

export default LevelAIStudio;