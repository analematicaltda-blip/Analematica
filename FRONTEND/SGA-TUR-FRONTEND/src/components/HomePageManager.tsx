"use client";

import { useState, useEffect, useCallback, FormEvent } from 'react';
import Image from 'next/image';
import { FiPlus, FiEdit, FiTrash2, FiImage, FiMove } from 'react-icons/fi';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  rectSortingStrategy,
  useSortable,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import {
  getHomePageComponents,
  createHomePageComponent,
  updateHomePageComponent,
  deleteHomePageComponent,
  reorderHomePageComponents,
  HomePageComponent,
} from '@/services/api';

const COMPONENT_TYPES: HomePageComponent['component_type'][] = ['BANNER', 'SLIDER', 'VIDEO'];

const parseApiError = (error: unknown): string => {
    if (error && typeof error === 'object' && 'response' in error) {
        const response = (error as { response: { data: unknown } }).response;
        if (response && typeof response === 'object' && 'data' in response) {
            const data = response.data;
            if (typeof data === 'object' && data !== null && !Array.isArray(data)) {
                return Object.entries(data)
                    .map(([key, value]) => {
                        const message = Array.isArray(value) ? value.join(', ') : String(value);
                        return `${key}: ${message}`;
                    })
                    .join('; ');
            }
            if (data && typeof data === 'object' && 'detail' in data) {
                return String((data as { detail: unknown }).detail);
            }
            return JSON.stringify(data);
        }
    }
    if (error && typeof error === 'object' && 'message' in error) {
        return String((error as { message: string }).message);
    }
    return "Ocurrió un error inesperado.";
};

const ComponentForm = ({ onSubmit, onCancel, initialData }: { onSubmit: (data: FormData) => void; onCancel: () => void; initialData?: HomePageComponent | null; }) => {
  const [title, setTitle] = useState(initialData?.title || '');
  const [subtitle, setSubtitle] = useState(initialData?.subtitle || '');
  const [linkUrl, setLinkUrl] = useState(initialData?.link_url || '');
  const [videoUrl, setVideoUrl] = useState(initialData?.video_url || '');
  const [componentType, setComponentType] = useState<HomePageComponent['component_type']>(initialData?.component_type || 'BANNER');
  const [isActive, setIsActive] = useState(initialData?.is_active !== false);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(initialData?.image || null);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      const file = e.target.files[0];
      setImageFile(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('title', title);
    formData.append('subtitle', subtitle);
    formData.append('link_url', linkUrl);
    formData.append('video_url', videoUrl);
    formData.append('component_type', componentType);
    formData.append('is_active', String(isActive));
    if (imageFile) formData.append('image', imageFile);
    onSubmit(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-xl w-full max-w-2xl">
        <h2 className="text-xl font-bold mb-6">{initialData ? 'Editar' : 'Crear'} Componente</h2>
        <form onSubmit={handleSubmit} className="space-y-4 max-h-[80vh] overflow-y-auto pr-2">
          <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Título Principal" className="w-full px-3 py-2 border rounded-md" required />
          <textarea value={subtitle} onChange={(e) => setSubtitle(e.target.value)} placeholder="Subtítulo (opcional)" className="w-full px-3 py-2 border rounded-md" />
          <input type="text" value={linkUrl} onChange={(e) => setLinkUrl(e.target.value)} placeholder="URL de Destino (ej: /noticias/slug)" className="w-full px-3 py-2 border rounded-md" />
          <select value={componentType} onChange={(e) => setComponentType(e.target.value as HomePageComponent['component_type'])} className="w-full px-3 py-2 border rounded-md">
            {COMPONENT_TYPES.map(type => <option key={type} value={type}>{type}</option>)}
          </select>
          {componentType === 'VIDEO' && <input type="text" value={videoUrl} onChange={(e) => setVideoUrl(e.target.value)} placeholder="URL del Video (YouTube, etc.)" className="w-full px-3 py-2 border rounded-md" />}
          <div className="flex items-center">
            <input type="checkbox" id="is_active_component" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} className="h-4 w-4 text-blue-600 border-gray-300 rounded" />
            <label htmlFor="is_active_component" className="ml-2 block text-sm text-gray-900">Activo y visible</label>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Imagen</label>
            <div className="mt-1 flex items-center space-x-4">
              {imagePreview ? <Image src={imagePreview} alt="Vista previa" width={128} height={80} className="h-20 w-auto rounded-md object-cover" /> : <div className="h-20 w-32 bg-gray-100 rounded-md flex items-center justify-center text-gray-400"><FiImage size={32}/></div>}
              <input type="file" onChange={handleImageChange} className="block text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"/>
            </div>
            {!initialData && <p className="text-xs text-gray-500 mt-1">La imagen es requerida para crear un nuevo componente.</p>}
          </div>
          <div className="flex justify-end space-x-3 pt-4">
            <button type="button" onClick={onCancel} className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300">Cancelar</button>
            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">Guardar</button>
          </div>
        </form>
      </div>
    </div>
  );
};

function SortableComponentItem({ component, onEdit, onDelete }: { component: HomePageComponent; onEdit: (c: HomePageComponent) => void; onDelete: (id: number) => void; }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: component.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    zIndex: isDragging ? 10 : 'auto',
    opacity: isDragging ? 0.7 : 1,
  };

  return (
    <div ref={setNodeRef} style={style} className="bg-white rounded-lg shadow-md overflow-hidden touch-none">
      <div className="relative">
        <Image src={component.image} alt={component.title} width={400} height={160} className="w-full h-40 object-cover" />
        <div {...attributes} {...listeners} className="absolute top-2 right-2 p-2 bg-white bg-opacity-70 rounded-full cursor-grab active:cursor-grabbing" title="Arrastrar para reordenar">
          <FiMove className="text-gray-600" />
        </div>
      </div>
      <div className="p-4">
        <h3 className="font-bold text-lg">{component.title}</h3>
        <p className="text-sm text-gray-600 h-10 overflow-hidden">{component.subtitle}</p>
        <div className="mt-2 flex justify-between items-center text-xs text-gray-500">
          <span>{component.component_type}</span>
          <span className={`px-2 py-1 rounded-full ${component.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            {component.is_active ? 'Activo' : 'Inactivo'}
          </span>
        </div>
      </div>
      <div className="bg-gray-50 px-4 py-2 flex justify-end space-x-2">
        <button onClick={() => onEdit(component)} className="p-2 text-gray-500 hover:text-blue-600"><FiEdit /></button>
        <button onClick={() => onDelete(component.id)} className="p-2 text-gray-500 hover:text-red-600"><FiTrash2 /></button>
      </div>
    </div>
  );
}

export default function HomePageManager() {
  const [components, setComponents] = useState<HomePageComponent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingComponent, setEditingComponent] = useState<HomePageComponent | null>(null);

  const fetchComponents = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await getHomePageComponents();
      setComponents(response.results || []);
    } catch {
      setError("No se pudieron cargar los componentes.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { fetchComponents(); }, [fetchComponents]);

  const handleOpenModal = (component?: HomePageComponent) => {
    setEditingComponent(component || null);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingComponent(null);
  };

  const handleSaveComponent = async (data: FormData) => {
    setError(null);
    try {
      if (editingComponent?.id) {
        await updateHomePageComponent(editingComponent.id, data);
      } else {
        await createHomePageComponent(data);
      }
      fetchComponents();
      handleCloseModal();
    } catch (err) {
      setError(`Error al guardar el componente: ${parseApiError(err)}`);
    }
  };

  const handleDeleteComponent = async (id: number) => {
    if (!window.confirm("¿Está seguro?")) return;
    try {
      await deleteHomePageComponent(id);
      fetchComponents();
    } catch (err) {
      setError(`Error al eliminar: ${parseApiError(err)}`);
    }
  };

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    if (over && active.id !== over.id) {
      const oldIndex = components.findIndex((c) => c.id === active.id);
      const newIndex = components.findIndex((c) => c.id === over.id);

      const reorderedComponents = arrayMove(components, oldIndex, newIndex);
      setComponents(reorderedComponents);

      const orderedIds = reorderedComponents.map((c) => c.id);
      try {
        await reorderHomePageComponents(orderedIds);
      } catch {
        setError("Error al guardar el nuevo orden. Por favor, recargue la página.");
        setComponents(components);
      }
    }
  };

  if (isLoading) return <p className="text-center py-8">Cargando...</p>;
  if (error) return <p className="text-center py-8 text-red-500">{error}</p>;

  return (
    <div className="bg-gray-50 p-4 sm:p-6 rounded-xl">
      {isModalOpen && <ComponentForm onSubmit={handleSaveComponent} onCancel={handleCloseModal} initialData={editingComponent} />}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Gestión de Contenido de Inicio</h2>
        <button onClick={() => handleOpenModal()} className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 shadow-sm">
          <FiPlus className="mr-2" />Crear Componente
        </button>
      </div>
      <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        <SortableContext items={components.map(c => c.id)} strategy={rectSortingStrategy}>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {components.length > 0 ? components.map(component => (
              <SortableComponentItem key={component.id} component={component} onEdit={handleOpenModal} onDelete={handleDeleteComponent} />
            )) : (
              <p className="col-span-full text-center text-gray-500 py-12">No hay componentes creados.</p>
            )}
          </div>
        </SortableContext>
      </DndContext>
    </div>
  );
}