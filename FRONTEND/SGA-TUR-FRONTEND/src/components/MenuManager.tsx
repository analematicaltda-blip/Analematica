"use client";

import { useState, useEffect, useCallback, FormEvent, useMemo } from 'react';
import { FiPlus, FiEdit, FiTrash2, FiChevronDown, FiChevronRight, FiMove, FiLoader } from 'react-icons/fi';
import {
  DndContext,
  closestCenter,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
  DragStartEvent,
  DragOverlay,
} from '@dnd-kit/core';
import {
  SortableContext,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import {
  getMenuItems,
  createMenuItem,
  updateMenuItem,
  deleteMenuItem,
  reorderMenuItems,
  MenuItem as MenuItemType,
  CreateMenuItemPayload,
  ReorderMenuItem,
} from '@/services/api';

// --- Tipos y Interfaces ---

interface MenuItemFormData {
  id?: number | null;
  nombre: string;
  url: string;
  parent: number | null;
}

// --- Componente del Formulario (Modal) ---

const MenuItemForm = ({
  onSubmit,
  onCancel,
  initialData,
  menuItems,
}: {
  onSubmit: (data: Partial<MenuItemFormData>) => void;
  onCancel: () => void;
  initialData?: Partial<MenuItemFormData> | null;
  menuItems: MenuItemType[];
}) => {
  const [formData, setFormData] = useState({
    nombre: initialData?.nombre || '',
    url: initialData?.url || '#',
    parent: initialData?.parent || null,
  });

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    onSubmit({ id: initialData?.id, ...formData });
  };

  const findItemWithDescendants = (items: MenuItemType[], id: number): number[] => {
    const item = findItem(items, id);
    if (!item) return [];
    let ids: number[] = [item.id];
    if (item.children) {
      item.children.forEach(child => {
        ids = [...ids, ...findItemWithDescendants(items, child.id)];
      });
    }
    return ids;
  };

  const renderOptions = (items: MenuItemType[], level = 0, disabledIds: number[] = []) => {
    let options: JSX.Element[] = [];
    if (initialData?.id) {
        disabledIds = findItemWithDescendants(menuItems, initialData.id);
    }

    items.forEach(item => {
      const isDisabled = disabledIds.includes(item.id);
      if (level < 2) {
          options.push(
            <option key={item.id} value={item.id} disabled={isDisabled}>
              {'--'.repeat(level)} {item.nombre}
            </option>
          );
          if (item.children && item.children.length > 0) {
            options = options.concat(renderOptions(item.children, level + 1, disabledIds));
          }
      }
    });
    return options;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-xl w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">{initialData?.id ? 'Editar' : 'Añadir'} Elemento</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input type="text" value={formData.nombre} onChange={(e) => setFormData({ ...formData, nombre: e.target.value })} placeholder="Nombre" className="w-full px-3 py-2 border rounded-md" required/>
          <input type="text" value={formData.url} onChange={(e) => setFormData({ ...formData, url: e.target.value })} placeholder="URL (ej: /noticias, o # si es un padre)" className="w-full px-3 py-2 border rounded-md" required/>
          <select value={formData.parent || ''} onChange={(e) => setFormData({ ...formData, parent: e.target.value ? parseInt(e.target.value) : null })} className="w-full px-3 py-2 border rounded-md">
            <option value="">-- Ninguno (Elemento Principal) --</option>
            {renderOptions(menuItems)}
          </select>
          <div className="flex justify-end space-x-3 pt-4">
            <button type="button" onClick={onCancel} className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300">Cancelar</button>
            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">Guardar</button>
          </div>
        </form>
      </div>
    </div>
  );
};

// --- Componente para una Fila de Menú (Arrastrable) ---

const SortableMenuItem = ({
  item,
  onEdit,
  onDelete,
  level = 0,
}: {
  item: MenuItemType;
  onEdit: (item: MenuItemType) => void;
  onDelete: (id: number) => void;
  level?: number;
}) => {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: item.id });
  const [isExpanded, setIsExpanded] = useState(true);

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div ref={setNodeRef} style={style} className="my-1 touch-none">
      <div className="flex items-center justify-between p-3 bg-white rounded-lg shadow-sm border border-gray-200 hover:bg-gray-50" style={{ marginLeft: `${level * 24}px` }}>
        <div className="flex items-center flex-grow min-w-0">
          {item.children && item.children.length > 0 ? (
            <button onClick={() => setIsExpanded(!isExpanded)} className="mr-2 p-1 hover:bg-gray-200 rounded-full flex-shrink-0">
              {isExpanded ? <FiChevronDown size={16} /> : <FiChevronRight size={16} />}
            </button>
          ) : ( <div className="w-6 mr-2 flex-shrink-0"></div> )}

          <div {...listeners} {...attributes} className="mr-3 text-gray-400 cursor-grab active:cursor-grabbing flex-shrink-0">
            <FiMove />
          </div>

          <span className="font-medium text-gray-800 truncate">{item.nombre}</span>
          <span className="ml-4 text-sm text-gray-500 truncate hidden sm:inline">{item.url}</span>
        </div>
        <div className="flex items-center space-x-2 flex-shrink-0">
          <button onClick={() => onEdit(item)} className="p-2 text-gray-500 hover:text-blue-600 rounded-full hover:bg-blue-100 transition-colors"><FiEdit size={16} /></button>
          <button onClick={() => onDelete(item.id)} className="p-2 text-gray-500 hover:text-red-600 rounded-full hover:bg-red-100 transition-colors"><FiTrash2 size={16} /></button>
        </div>
      </div>
      {isExpanded && item.children && item.children.length > 0 && (
        <div className="mt-1">
          <SortableContext items={item.children.map(child => child.id)} strategy={verticalListSortingStrategy}>
            {item.children.map(child => (
              <SortableMenuItem key={child.id} item={child} onEdit={onEdit} onDelete={onDelete} level={level + 1} />
            ))}
          </SortableContext>
        </div>
      )}
    </div>
  );
};

// --- Funciones de Ayuda para el Árbol ---

const findItem = (items: MenuItemType[], id: number): MenuItemType | undefined => {
  for (const item of items) {
    if (item.id === id) return item;
    if (item.children) {
      const found = findItem(item.children, id);
      if (found) return found;
    }
  }
  return undefined;
};

const findParentAndChildren = (items: MenuItemType[], id: number): { container: MenuItemType[], parent: MenuItemType | null } | null => {
    for (const item of items) {
        if (item.children?.some(child => child.id === id)) {
            return { container: item.children, parent: item };
        }
        if (item.children) {
            const result = findParentAndChildren(item.children, id);
            if (result) return result;
        }
    }
    if (items.some(item => item.id === id)) {
        return { container: items, parent: null };
    }
    return null;
}

// --- Componente Principal ---

export default function MenuManager() {
  const [menuItems, setMenuItems] = useState<MenuItemType[]>([]);
  const [activeItem, setActiveItem] = useState<MenuItemType | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<Partial<MenuItemFormData> | null>(null);

  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } }));

  const flattenedItemIds = useMemo(() => {
    const ids: number[] = [];
    const recurse = (items: MenuItemType[]) => {
        items.forEach(item => {
            ids.push(item.id);
            if (item.children) recurse(item.children);
        });
    }
    recurse(menuItems);
    return ids;
  }, [menuItems]);

  const fetchMenuItems = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await getMenuItems();
      setMenuItems(response.results || []);
    } catch (err) {
      setError("No se pudo cargar los elementos del menú.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { fetchMenuItems(); }, [fetchMenuItems]);

  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event;
    setActiveItem(findItem(menuItems, active.id as number) || null);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveItem(null);

    if (over && active.id !== over.id) {
        setMenuItems((items) => {
            const newItems = JSON.parse(JSON.stringify(items));

            const activeParentInfo = findParentAndChildren(newItems, active.id as number);
            const overParentInfo = findParentAndChildren(newItems, over.id as number);

            if (activeParentInfo && overParentInfo && activeParentInfo.parent?.id === overParentInfo.parent?.id) {
                const container = activeParentInfo.container;
                const oldIndex = container.findIndex(item => item.id === active.id);
                const newIndex = container.findIndex(item => item.id === over.id);

                if (oldIndex !== -1 && newIndex !== -1) {
                    const [movedItem] = container.splice(oldIndex, 1);
                    container.splice(newIndex, 0, movedItem);
                }
            } else {
                 // Drag-and-drop reparenting is disabled to maintain data integrity.
                 // Users are encouraged to use the "Edit" button to change parent-child relationships.
            }
            return newItems;
        });
    }
  };

  const handleOpenModal = (item?: MenuItemType) => {
    setEditingItem(item ? { id: item.id, nombre: item.nombre, url: item.url, parent: item.parent } : null);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingItem(null);
  };

  const handleSaveMenuItem = async (data: Partial<MenuItemFormData>) => {
    setError(null);
    const payload: CreateMenuItemPayload = {
      nombre: data.nombre!,
      url: data.url!,
      parent: data.parent === undefined ? null : data.parent,
    };

    try {
      if (data.id) {
        await updateMenuItem(data.id, payload);
      } else {
        await createMenuItem(payload);
      }
      fetchMenuItems();
      handleCloseModal();
    } catch (err) {
      const error = err as { response?: { data: unknown }; message: string };
      const errorMessage =
        typeof error.response?.data === 'string'
          ? error.response.data
          : JSON.stringify(error.response?.data);
      setError(`Error al guardar: ${errorMessage || error.message}`);
    }
  };

  const handleDeleteMenuItem = async (id: number) => {
    if (!window.confirm("¿Está seguro? Los elementos anidados también serán eliminados.")) return;
    setError(null);
    try {
        await deleteMenuItem(id);
        fetchMenuItems();
    } catch (err) {
      const error = err as { response?: { data?: { detail?: string } }; message: string };
      setError(`Error al eliminar: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleSaveChanges = async () => {
      setIsSaving(true);
      setError(null);
      try {
          const formatForApi = (items: MenuItemType[]): ReorderMenuItem[] => {
              return items.map(item => ({
                  id: item.id,
                  children: item.children ? formatForApi(item.children) : [],
              }));
          };
          await reorderMenuItems(formatForApi(menuItems));
          fetchMenuItems();
      } catch (err) {
          const error = err as { response?: { data?: { detail?: string } }; message: string };
          setError(`Error al guardar el orden: ${error.response?.data?.detail || error.message}`);
      } finally {
          setIsSaving(false);
      }
  };

  if (isLoading) return <div className="text-center py-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div><p className="mt-4 text-gray-500">Cargando gestor de menú...</p></div>;
  if (error) return <p className="text-center py-8 text-red-500 bg-red-50 p-4 rounded-lg">{error}</p>;

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
      <div className="bg-gray-50 p-4 sm:p-6 rounded-xl shadow-md">
        {isModalOpen && (
          <MenuItemForm
            onSubmit={handleSaveMenuItem}
            onCancel={handleCloseModal}
            initialData={editingItem}
            menuItems={menuItems}
          />
        )}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">Gestión del Menú Principal</h2>
            <p className="text-sm text-gray-500 mt-1">Arrastre para reordenar. Use &quot;Editar&quot; para anidar elementos.</p>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={() => handleOpenModal()} className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 shadow-sm transition-colors">
              <FiPlus className="mr-2" />
              Añadir Elemento
            </button>
            <button
              onClick={handleSaveChanges}
              disabled={isSaving}
              className="flex items-center justify-center px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 shadow-sm transition-colors disabled:bg-green-400 disabled:cursor-not-allowed"
            >
              {isSaving ? <FiLoader className="animate-spin mr-2" /> : null}
              {isSaving ? 'Guardando...' : 'Guardar Orden'}
            </button>
          </div>
        </div>
        <div className="p-4 bg-white rounded-lg shadow-inner min-h-[200px]">
          {menuItems.length > 0 ? (
            <SortableContext items={flattenedItemIds} strategy={verticalListSortingStrategy}>
              {menuItems.map(item => (
                <SortableMenuItem key={item.id} item={item} onEdit={handleOpenModal} onDelete={handleDeleteMenuItem} />
              ))}
            </SortableContext>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500">No hay elementos en el menú.</p>
              <p className="text-sm text-gray-400 mt-2">Haga clic en &quot;Añadir Elemento&quot; para empezar.</p>
            </div>
          )}
        </div>
        <DragOverlay>
            {activeItem ? <div className="p-3 bg-white rounded-lg shadow-xl border border-blue-500 font-medium flex items-center gap-2"><FiMove/>{activeItem.nombre}</div> : null}
        </DragOverlay>
      </div>
    </DndContext>
  );
}