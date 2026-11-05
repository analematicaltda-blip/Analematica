// @/app/dashboard/prestador/mi-negocio/gestion-operativa/modulos-especializados/transporte/page.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { useMiNegocioApi } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Label } from '@/components/ui/Label';
import { useToast } from '@/components/ui/use-toast';
import { PlusCircle, Edit, Trash2 } from 'lucide-react';

// Define the type for a single vehicle for type safety
interface Vehicle {
  id?: number;
  nombre: string;
  placa: string;
  modelo_ano: string;
  tipo_vehiculo: string;
  capacidad: number;
  status: string;
  insurance_expiry_date: string;
  tech_inspection_expiry_date: string;
}

const initialVehicleState: Vehicle = {
  nombre: '',
  placa: '',
  modelo_ano: '',
  tipo_vehiculo: 'Terrestre',
  capacidad: 4,
  status: 'Disponible',
  insurance_expiry_date: '',
  tech_inspection_expiry_date: '',
};

export default function TransportePage() {
  const { fetchData, postData, putData, deleteData } = useMiNegocioApi();
  const { toast } = useToast();

  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [currentVehicle, setCurrentVehicle] = useState<Vehicle>(initialVehicleState);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [showForm, setShowForm] = useState<boolean>(false);

  const apiEndpoint = 'operativa/transporte/vehicles/';

  useEffect(() => {
    loadVehicles();
  }, []);

  const loadVehicles = async () => {
    setIsLoading(true);
    try {
      const response = await fetchData(apiEndpoint);
      setVehicles(response.results || response);
    } catch (error) {
      console.error("Error loading vehicles:", error);
      toast({
        title: "Error",
        description: "No se pudieron cargar los vehículos.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;
    setCurrentVehicle({
      ...currentVehicle,
      [name]: type === 'number' ? parseInt(value, 10) : value,
    });
  };

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setCurrentVehicle({ ...currentVehicle, [name]: value });
  };


  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      if (isEditing) {
        await putData(`${apiEndpoint}${currentVehicle.id}/`, currentVehicle);
        toast({ title: "Vehículo Actualizado", description: "El vehículo se ha actualizado correctamente." });
      } else {
        await postData(apiEndpoint, currentVehicle);
        toast({ title: "Vehículo Creado", description: "El nuevo vehículo se ha añadido correctamente." });
      }
      resetForm();
      loadVehicles();
    } catch (error: any) {
        const errorMsg = error.response?.data ? JSON.stringify(error.response.data) : "Error desconocido";
        toast({
            title: "Error al guardar",
            description: `No se pudo guardar el vehículo. Detalles: ${errorMsg}`,
            variant: "destructive",
        });
        console.error("Failed to save vehicle:", error);
    }
  };

  const resetForm = () => {
    setCurrentVehicle(initialVehicleState);
    setIsEditing(false);
    setShowForm(false);
  };

  const handleEdit = (vehicle: Vehicle) => {
    setCurrentVehicle(vehicle);
    setIsEditing(true);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este vehículo?')) {
      try {
        await deleteData(`${apiEndpoint}${id}/`);
        toast({ title: "Vehículo Eliminado", description: "El vehículo ha sido eliminado." });
        loadVehicles();
      } catch (error) {
        toast({
          title: "Error al eliminar",
          description: "No se pudo eliminar el vehículo.",
          variant: "destructive",
        });
        console.error("Failed to delete vehicle:", error);
      }
    }
  };

  const renderVehicleForm = () => (
    <Card className="mb-8">
      <CardHeader>
        <CardTitle>{isEditing ? 'Editar Vehículo' : 'Añadir Nuevo Vehículo'}</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <Label htmlFor="nombre">Nombre o Identificador</Label>
            <Input id="nombre" name="nombre" value={currentVehicle.nombre} onChange={handleInputChange} placeholder="Ej: Buseta 01" required />
          </div>
          <div>
            <Label htmlFor="placa">Placa</Label>
            <Input id="placa" name="placa" value={currentVehicle.placa} onChange={handleInputChange} placeholder="XYZ-123" required />
          </div>
          <div>
            <Label htmlFor="modelo_ano">Modelo (Año)</Label>
            <Input id="modelo_ano" name="modelo_ano" value={currentVehicle.modelo_ano} onChange={handleInputChange} placeholder="2023" required />
          </div>
          <div>
            <Label htmlFor="tipo_vehiculo">Tipo de Vehículo</Label>
            <Input id="tipo_vehiculo" name="tipo_vehiculo" value={currentVehicle.tipo_vehiculo} onChange={handleInputChange} placeholder="Terrestre, Acuático" required />
          </div>
          <div>
            <Label htmlFor="capacidad">Capacidad (Pasajeros)</Label>
            <Input id="capacidad" name="capacidad" type="number" value={currentVehicle.capacidad} onChange={handleInputChange} required />
          </div>
          <div>
            <Label htmlFor="status">Estado</Label>
            <Input id="status" name="status" value={currentVehicle.status} onChange={handleInputChange} placeholder="Disponible, En Mantenimiento" required />
          </div>
           <div>
            <Label htmlFor="insurance_expiry_date">Vencimiento del Seguro</Label>
            <Input id="insurance_expiry_date" name="insurance_expiry_date" type="date" value={currentVehicle.insurance_expiry_date} onChange={handleDateChange} required />
          </div>
          <div>
            <Label htmlFor="tech_inspection_expiry_date">Vencimiento Tecnomecánica</Label>
            <Input id="tech_inspection_expiry_date" name="tech_inspection_expiry_date" type="date" value={currentVehicle.tech_inspection_expiry_date} onChange={handleDateChange} required />
          </div>

          <div className="col-span-full flex justify-end gap-2 mt-4">
            <Button type="button" variant="outline" onClick={resetForm}>Cancelar</Button>
            <Button type="submit">{isEditing ? 'Actualizar' : 'Guardar'}</Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );

  const renderVehicleList = () => (
    <div className="space-y-4">
        {vehicles.map(vehicle => (
            <Card key={vehicle.id}>
                <CardContent className="p-4 flex justify-between items-center">
                    <div>
                        <h3 className="font-bold text-lg">{vehicle.nombre} ({vehicle.placa})</h3>
                        <p className="text-sm text-muted-foreground">
                            {vehicle.tipo_vehiculo} - Capacidad: {vehicle.capacidad} - Estado: <span className={vehicle.status === 'Disponible' ? 'text-green-600' : 'text-orange-600'}>{vehicle.status}</span>
                        </p>
                         <p className="text-xs text-gray-500">
                            Vence Seguro: {vehicle.insurance_expiry_date} | Vence Tecnomecánica: {vehicle.tech_inspection_expiry_date}
                        </p>
                    </div>
                    <div className="flex gap-2">
                        <Button variant="outline" size="icon" onClick={() => handleEdit(vehicle)}><Edit className="h-4 w-4" /></Button>
                        <Button variant="destructive" size="icon" onClick={() => handleDelete(vehicle.id!)}><Trash2 className="h-4 w-4" /></Button>
                    </div>
                </CardContent>
            </Card>
        ))}
    </div>
  );

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Gestión de Flota de Transporte</h1>
        {!showForm && (
          <Button onClick={() => { setShowForm(true); setIsEditing(false); setCurrentVehicle(initialVehicleState); }}>
            <PlusCircle className="mr-2 h-4 w-4" /> Añadir Vehículo
          </Button>
        )}
      </div>

      {showForm && renderVehicleForm()}

      <Card>
        <CardHeader>
          <CardTitle>Listado de Vehículos</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? <p>Cargando vehículos...</p> : vehicles.length > 0 ? renderVehicleList() : <p>No hay vehículos registrados.</p>}
        </CardContent>
      </Card>
    </div>
  );
}
