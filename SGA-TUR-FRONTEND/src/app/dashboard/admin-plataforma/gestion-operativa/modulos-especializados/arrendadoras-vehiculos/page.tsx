// @/app/dashboard/prestador/mi-negocio/gestion-operativa/modulos-especializados/arrendadoras-vehiculos/page.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { useMiNegocioApi } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { useToast } from "@/components/ui/use-toast";
import { PlusCircle, Edit, Trash2 } from "lucide-react";

// Types
interface Vehiculo {
  id?: number;
  nombre: string;
  placa: string;
  categoria: string;
  transmision: string;
  numero_pasajeros: number;
  precio_por_dia: number;
  disponible?: boolean;
}

interface Alquiler {
    id: number;
    vehiculo_nombre: string;
    vehiculo_placa: string;
    nombre_cliente_temporal: string;
    fecha_recogida: string;
    fecha_devolucion: string;
    costo_total_calculado: number;
    estado: string;
}


const initialVehiculoState: Vehiculo = {
  nombre: '',
  placa: '',
  categoria: 'compacto',
  transmision: 'automatica',
  numero_pasajeros: 4,
  precio_por_dia: 150000,
};

export default function ArrendadoraVehiculosPage() {
  const { fetchData, postData, putData, deleteData } = useMiNegocioApi();
  const { toast } = useToast();

  const [flota, setFlota] = useState<Vehiculo[]>([]);
  const [alquileres, setAlquileres] = useState<Alquiler[]>([]);
  const [currentVehiculo, setCurrentVehiculo] = useState<Vehiculo>(initialVehiculoState);
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [view, setView] = useState<'flota' | 'alquileres'>('flota');

  const flotaEndpoint = 'operativa/arrendadora-vehiculos/flota/';
  const alquileresEndpoint = 'operativa/arrendadora-vehiculos/alquileres/';

  useEffect(() => {
    if (view === 'flota') {
      loadFlota();
    } else {
      loadAlquileres();
    }
  }, [view]);

  const loadFlota = async () => {
    setIsLoading(true);
    try {
      const data = await fetchData(flotaEndpoint);
      setFlota(data.results || data);
    } catch (error) {
      toast({ title: "Error", description: "No se pudo cargar la flota de vehículos.", variant: "destructive" });
    } finally {
      setIsLoading(false);
    }
  };

  const loadAlquileres = async () => {
      setIsLoading(true);
      try {
        const data = await fetchData(alquileresEndpoint);
        setAlquileres(data.results || data);
      } catch (error) {
         toast({ title: "Error", description: "No se pudieron cargar los alquileres.", variant: "destructive" });
      } finally {
          setIsLoading(false);
      }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;
    const val = type === 'number' ? parseFloat(value) : value;
    setCurrentVehiculo({ ...currentVehiculo, [name]: val });
  };

  const handleSelectChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const { name, value } = e.target;
    setCurrentVehiculo({ ...currentVehiculo, [name]: value });
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      if (isEditing) {
        await putData(`${flotaEndpoint}${currentVehiculo.id}/`, currentVehiculo);
        toast({ title: "Vehículo Actualizado", description: "El vehículo se ha actualizado." });
      } else {
        await postData(flotaEndpoint, currentVehiculo);
        toast({ title: "Vehículo Añadido", description: "El nuevo vehículo se ha añadido a la flota." });
      }
      resetForm();
      loadFlota();
    } catch (error) {
      toast({ title: "Error", description: "No se pudo guardar el vehículo.", variant: "destructive" });
    }
  };

  const resetForm = () => {
    setCurrentVehiculo(initialVehiculoState);
    setIsEditing(false);
    setShowForm(false);
  };

  const handleEdit = (vehiculo: Vehiculo) => {
    setCurrentVehiculo(vehiculo);
    setIsEditing(true);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('¿Seguro que quieres eliminar este vehículo de la flota?')) {
      try {
        await deleteData(`${flotaEndpoint}${id}/`);
        toast({ title: "Vehículo Eliminado" });
        loadFlota();
      } catch (error) {
        toast({ title: "Error", description: "No se pudo eliminar el vehículo. Puede tener alquileres asociados.", variant: "destructive" });
      }
    }
  };

  const renderVehiculoForm = () => (
    <Card className="mb-8">
      <CardHeader><CardTitle>{isEditing ? 'Editar Vehículo' : 'Añadir Vehículo a la Flota'}</CardTitle></CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="nombre">Nombre / Modelo</Label>
            <Input id="nombre" name="nombre" value={currentVehiculo.nombre} onChange={handleInputChange} required placeholder="Ej: Renault Duster"/>
          </div>
          <div>
            <Label htmlFor="placa">Placa</Label>
            <Input id="placa" name="placa" value={currentVehiculo.placa} onChange={handleInputChange} required />
          </div>
          <div>
            <Label htmlFor="categoria">Categoría</Label>
             <select name="categoria" id="categoria" value={currentVehiculo.categoria} onChange={handleSelectChange} className="w-full p-2 border rounded">
                <option value="economico">Económico</option>
                <option value="compacto">Compacto</option>
                <option value="intermedio">Intermedio</option>
                <option value="suv">SUV</option>
                <option value="lujo">Lujo</option>
                <option value="van">Van/Minivan</option>
                <option value="moto">Motocicleta</option>
            </select>
          </div>
           <div>
            <Label htmlFor="transmision">Transmisión</Label>
            <select name="transmision" id="transmision" value={currentVehiculo.transmision} onChange={handleSelectChange} className="w-full p-2 border rounded">
                <option value="automatica">Automática</option>
                <option value="manual">Manual</option>
            </select>
          </div>
           <div>
            <Label htmlFor="numero_pasajeros">Nº de Pasajeros</Label>
            <Input id="numero_pasajeros" name="numero_pasajeros" type="number" value={currentVehiculo.numero_pasajeros} onChange={handleInputChange} required />
          </div>
           <div>
            <Label htmlFor="precio_por_dia">Precio por Día (COP)</Label>
            <Input id="precio_por_dia" name="precio_por_dia" type="number" value={currentVehiculo.precio_por_dia} onChange={handleInputChange} required />
          </div>
          <div className="col-span-2 flex justify-end gap-2 mt-4">
            <Button type="button" variant="outline" onClick={resetForm}>Cancelar</Button>
            <Button type="submit">{isEditing ? 'Actualizar Vehículo' : 'Guardar Vehículo'}</Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );

  const renderFlotaView = () => (
    <>
     <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Mi Flota de Vehículos</h2>
          {!showForm && (
            <Button onClick={() => { setShowForm(true); setIsEditing(false); setCurrentVehiculo(initialVehiculoState); }}>
              <PlusCircle className="mr-2 h-4 w-4" /> Añadir Vehículo
            </Button>
          )}
      </div>
      {showForm && renderVehiculoForm()}
       <Card>
        <CardHeader><CardTitle>Listado de Vehículos</CardTitle></CardHeader>
        <CardContent>
             {isLoading ? <p>Cargando flota...</p> : (
                 <div className="space-y-4">
                     {flota.map(v => (
                         <Card key={v.id} className={`${!v.disponible ? 'bg-gray-100' : ''}`}>
                             <CardContent className="p-4 flex justify-between items-center">
                                 <div>
                                     <h3 className="font-bold">{v.nombre} ({v.placa})</h3>
                                     <p className="text-sm text-muted-foreground">
                                         {v.categoria} - {v.transmision} - {v.numero_pasajeros} pasajeros
                                     </p>
                                     <p className="text-sm font-semibold">
                                         ${v.precio_por_dia.toLocaleString()} COP/día -
                                         <span className={v.disponible ? 'text-green-600' : 'text-red-600'}>
                                             {v.disponible ? ' Disponible' : ' No Disponible'}
                                         </span>
                                     </p>
                                 </div>
                                 <div className="flex gap-2">
                                     <Button variant="outline" size="icon" onClick={() => handleEdit(v)}><Edit className="h-4 w-4" /></Button>
                                     <Button variant="destructive" size="icon" onClick={() => handleDelete(v.id!)}><Trash2 className="h-4 w-4" /></Button>
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

  const renderAlquileresView = () => (
       <Card>
        <CardHeader><CardTitle>Historial de Alquileres</CardTitle></CardHeader>
        <CardContent>
             {isLoading ? <p>Cargando alquileres...</p> : (
                 <div className="space-y-4">
                     {alquileres.map(a => (
                         <Card key={a.id}>
                             <CardContent className="p-4">
                                  <h3 className="font-bold">{a.vehiculo_nombre} ({a.vehiculo_placa}) - {a.nombre_cliente_temporal}</h3>
                                  <p className="text-sm text-muted-foreground">
                                      Desde: {new Date(a.fecha_recogida).toLocaleString()} | Hasta: {new Date(a.fecha_devolucion).toLocaleString()}
                                  </p>
                                  <p className="text-sm font-semibold">
                                      Costo Total: ${a.costo_total_calculado.toLocaleString()} COP | Estado: {a.estado}
                                  </p>
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
      <h1 className="text-3xl font-bold mb-4">Gestión de Arrendadora de Vehículos</h1>
      <div className="flex gap-2 mb-6 border-b">
        <Button variant={view === 'flota' ? 'default' : 'ghost'} onClick={() => setView('flota')}>
          Mi Flota
        </Button>
        <Button variant={view === 'alquileres' ? 'default' : 'ghost'} onClick={() => setView('alquileres')}>
          Alquileres
        </Button>
      </div>

      {view === 'flota' ? renderFlotaView() : renderAlquileresView()}

    </div>
  );
}
