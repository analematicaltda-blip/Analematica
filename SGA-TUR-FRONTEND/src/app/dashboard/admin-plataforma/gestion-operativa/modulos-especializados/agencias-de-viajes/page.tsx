// @/app/dashboard/prestador/mi-negocio/gestion-operativa/modulos-especializados/agencias-de-viajes/page.tsx
'use client';
import React, { useState, useEffect } from 'react';
import { useMiNegocioApi } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Textarea } from "@/components/ui/Textarea";
import { useToast } from "@/components/ui/use-toast";
import { PlusCircle, Edit, Trash2, Eye } from "lucide-react";

// Types
interface Paquete {
  id?: number;
  nombre: string;
  descripcion: string;
  duracion_dias: number;
  precio_por_persona: number;
  estado: 'borrador' | 'publicado' | 'archivado';
}

interface Reserva {
  id: number;
  paquete_nombre: string;
  nombre_cliente_temporal: string;
  fecha_inicio: string;
  numero_de_personas: number;
  costo_total: number;
  estado: string;
}

const initialPaqueteState: Paquete = {
  nombre: '',
  descripcion: '',
  duracion_dias: 1,
  precio_por_persona: 100000,
  estado: 'borrador',
};

export default function AgenciasDeViajesPage() {
  const { fetchData, postData, putData, deleteData } = useMiNegocioApi();
  const { toast } = useToast();

  const [paquetes, setPaquetes] = useState<Paquete[]>([]);
  const [reservas, setReservas] = useState<Reserva[]>([]);
  const [currentPaquete, setCurrentPaquete] = useState<Paquete>(initialPaqueteState);
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [view, setView] = useState<'paquetes' | 'reservas'>('paquetes');

  const paquetesEndpoint = 'operativa/agencias-viajes/paquetes/';
  const reservasEndpoint = 'operativa/agencias-viajes/reservas/';

  useEffect(() => {
    if (view === 'paquetes') {
      loadPaquetes();
    } else {
      loadReservas();
    }
  }, [view]);

  const loadPaquetes = async () => {
    setIsLoading(true);
    try {
      const data = await fetchData(paquetesEndpoint);
      setPaquetes(data.results || data);
    } catch (error) {
      toast({ title: "Error", description: "No se pudieron cargar los paquetes.", variant: "destructive" });
    } finally {
      setIsLoading(false);
    }
  };

  const loadReservas = async () => {
    setIsLoading(true);
    try {
      const data = await fetchData(reservasEndpoint);
      setReservas(data.results || data);
    } catch (error) {
      toast({ title: "Error", description: "No se pudieron cargar las reservas.", variant: "destructive" });
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    // @ts-ignore
    const val = type === 'number' ? parseFloat(value) : value;
    setCurrentPaquete({ ...currentPaquete, [name]: val });
  };

  const handleSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const { name, value } = e.target;
    // @ts-ignore
    setCurrentPaquete({ ...currentPaquete, [name]: value });
  };


  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      if (isEditing) {
        await putData(`${paquetesEndpoint}${currentPaquete.id}/`, currentPaquete);
        toast({ title: "Paquete Actualizado", description: "El paquete se ha actualizado." });
      } else {
        await postData(paquetesEndpoint, currentPaquete);
        toast({ title: "Paquete Creado", description: "El nuevo paquete se ha guardado." });
      }
      resetForm();
      loadPaquetes();
    } catch (error) {
      toast({ title: "Error", description: "No se pudo guardar el paquete.", variant: "destructive" });
    }
  };

  const resetForm = () => {
    setCurrentPaquete(initialPaqueteState);
    setIsEditing(false);
    setShowForm(false);
  };

  const handleEdit = (paquete: Paquete) => {
    setCurrentPaquete(paquete);
    setIsEditing(true);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('¿Confirmas la eliminación de este paquete?')) {
      try {
        await deleteData(`${paquetesEndpoint}${id}/`);
        toast({ title: "Paquete Eliminado", description: "El paquete ha sido eliminado." });
        loadPaquetes();
      } catch (error) {
        toast({ title: "Error", description: "No se pudo eliminar el paquete.", variant: "destructive" });
      }
    }
  };

  const renderPaquetesView = () => (
    <>
      <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Mis Paquetes Turísticos</h2>
          {!showForm && (
            <Button onClick={() => { setShowForm(true); setIsEditing(false); setCurrentPaquete(initialPaqueteState); }}>
              <PlusCircle className="mr-2 h-4 w-4" /> Crear Paquete
            </Button>
          )}
      </div>
      {showForm && renderPaqueteForm()}
      <Card>
        <CardHeader><CardTitle>Listado de Paquetes</CardTitle></CardHeader>
        <CardContent>
          {isLoading ? <p>Cargando...</p> : (
            <div className="space-y-4">
              {paquetes.map(p => (
                <Card key={p.id}>
                  <CardContent className="p-4 flex justify-between items-center">
                    <div>
                      <h3 className="font-bold">{p.nombre}</h3>
                      <p className="text-sm text-muted-foreground">
                        {p.duracion_dias} días - ${p.precio_por_persona.toLocaleString()} COP/persona - Estado: {p.estado}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="icon" onClick={() => handleEdit(p)}><Edit className="h-4 w-4" /></Button>
                      <Button variant="destructive" size="icon" onClick={() => handleDelete(p.id!)}><Trash2 className="h-4 w-4" /></Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </>
  );

  const renderPaqueteForm = () => (
    <Card className="mb-8">
      <CardHeader><CardTitle>{isEditing ? 'Editar Paquete' : 'Nuevo Paquete'}</CardTitle></CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="col-span-2">
            <Label htmlFor="nombre">Nombre del Paquete</Label>
            <Input id="nombre" name="nombre" value={currentPaquete.nombre} onChange={handleInputChange} required />
          </div>
          <div className="col-span-2">
            <Label htmlFor="descripcion">Descripción</Label>
            <Textarea id="descripcion" name="descripcion" value={currentPaquete.descripcion} onChange={handleInputChange} required />
          </div>
          <div>
            <Label htmlFor="duracion_dias">Duración (días)</Label>
            <Input id="duracion_dias" name="duracion_dias" type="number" value={currentPaquete.duracion_dias} onChange={handleInputChange} required />
          </div>
          <div>
            <Label htmlFor="precio_por_persona">Precio por Persona (COP)</Label>
            <Input id="precio_por_persona" name="precio_por_persona" type="number" value={currentPaquete.precio_por_persona} onChange={handleInputChange} required />
          </div>
           <div>
            <Label htmlFor="estado">Estado</Label>
            <select name="estado" id="estado" value={currentPaquete.estado} onChange={handleSelectChange} className="w-full p-2 border rounded">
                <option value="borrador">Borrador</option>
                <option value="publicado">Publicado</option>
                <option value="archivado">Archivado</option>
            </select>
           </div>
          <div className="col-span-2 flex justify-end gap-2 mt-4">
            <Button type="button" variant="outline" onClick={resetForm}>Cancelar</Button>
            <Button type="submit">{isEditing ? 'Actualizar' : 'Guardar'}</Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );

  const renderReservasView = () => (
     <Card>
        <CardHeader><CardTitle>Reservas de Paquetes</CardTitle></CardHeader>
        <CardContent>
          {isLoading ? <p>Cargando...</p> : (
            <div className="space-y-4">
              {reservas.map(r => (
                <Card key={r.id}>
                  <CardContent className="p-4">
                    <h3 className="font-bold">{r.paquete_nombre} - {r.nombre_cliente_temporal}</h3>
                    <p className="text-sm text-muted-foreground">
                      Fecha: {r.fecha_inicio} | {r.numero_de_personas} personas | Total: ${r.costo_total.toLocaleString()} COP
                    </p>
                     <p className="text-sm font-semibold">Estado: {r.estado}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
  );

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Gestión de Agencia de Viajes</h1>
      <div className="flex gap-2 mb-6 border-b">
        <Button variant={view === 'paquetes' ? 'default' : 'ghost'} onClick={() => setView('paquetes')}>
          Paquetes
        </Button>
        <Button variant={view === 'reservas' ? 'default' : 'ghost'} onClick={() => setView('reservas')}>
          Reservas
        </Button>
      </div>

      {view === 'paquetes' ? renderPaquetesView() : renderReservasView()}
    </div>
  );
}
