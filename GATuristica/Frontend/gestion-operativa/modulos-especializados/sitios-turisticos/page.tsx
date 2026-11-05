// @/app/dashboard/prestador/mi-negocio/gestion-operativa/modulos-especializados/sitios-turisticos/page.tsx
'use client';
import React, { useState, useEffect } from 'react';
import { useMiNegocioApi } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Textarea } from "@/components/ui/Textarea";
import { useToast } from "@/components/ui/use-toast";
import { PlusCircle, Edit, Trash2, ArrowLeft, Building, Plus, X } from "lucide-react";

// Types
interface Actividad {
    id?: number;
    nombre: string;
    descripcion: string;
    precio_adicional: number;
}
interface Sitio {
    id?: number;
    nombre: string;
    descripcion_corta: string;
    descripcion_larga: string;
    tipo_sitio: string;
    activo: boolean;
    actividades: Actividad[];
}

const initialSitioState: Sitio = {
    nombre: '',
    descripcion_corta: '',
    descripcion_larga: '',
    tipo_sitio: 'otro',
    activo: true,
    actividades: [],
};

const initialActividadState: Actividad = {
    nombre: '',
    descripcion: '',
    precio_adicional: 0,
};

export default function SitiosTuristicosPage() {
    const { fetchData, postData, putData, deleteData } = useMiNegocioApi();
    const { toast } = useToast();

    const [sitios, setSitios] = useState<Sitio[]>([]);
    const [selectedSitio, setSelectedSitio] = useState<Sitio | null>(null);
    const [currentSitio, setCurrentSitio] = useState<Sitio>(initialSitioState);
    const [currentActividad, setCurrentActividad] = useState<Actividad>(initialActividadState);

    const [isEditingSitio, setIsEditingSitio] = useState(false);
    const [showSitioForm, setShowSitioForm] = useState(false);
    const [showActividadForm, setShowActividadForm] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    const sitiosEndpoint = 'operativa/sitios-turisticos/sitios/';

    useEffect(() => {
        loadSitios();
    }, []);

    // --- Data Fetching ---
    const loadSitios = async () => {
        setIsLoading(true);
        try {
            const data = await fetchData(sitiosEndpoint);
            setSitios(data.results || data);
        } catch (error) {
            toast({ title: "Error", description: "No se pudieron cargar los sitios turísticos.", variant: "destructive" });
        } finally {
            setIsLoading(false);
        }
    };

    const loadSingleSitio = async (id: number) => {
        try {
            const data = await fetchData(`${sitiosEndpoint}${id}/`);
            setSelectedSitio(data);
        } catch (error) {
            toast({ title: "Error", description: "No se pudo cargar el detalle del sitio.", variant: "destructive" });
        }
    }

    // --- State Management & Forms ---
    const handleSelectSitio = (sitio: Sitio) => {
        loadSingleSitio(sitio.id!);
    };

    const resetToListView = () => {
        setSelectedSitio(null);
        setShowSitioForm(false);
        setIsEditingSitio(false);
        setCurrentSitio(initialSitioState);
        loadSitios();
    };

    const handleEditSitio = (sitio: Sitio) => {
        setCurrentSitio(sitio);
        setIsEditingSitio(true);
        setShowSitioForm(true);
    };

    // --- API Calls ---
    const handleSitioSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            if (isEditingSitio) {
                await putData(`${sitiosEndpoint}${currentSitio.id!}/`, currentSitio);
                toast({ title: "Sitio Actualizado" });
            } else {
                await postData(sitiosEndpoint, currentSitio);
                toast({ title: "Sitio Creado" });
            }
            resetToListView();
        } catch (error) {
            toast({ title: "Error", description: "No se pudo guardar el sitio.", variant: "destructive" });
        }
    };

    const handleDeleteSitio = async (id: number) => {
        if(window.confirm("¿Seguro que quieres eliminar este sitio y todas sus actividades?")) {
            try {
                await deleteData(`${sitiosEndpoint}${id}/`);
                toast({ title: "Sitio Eliminado" });
                resetToListView();
            } catch (error) {
                toast({ title: "Error al eliminar" });
            }
        }
    };

    const handleActividadSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const actividadEndpoint = `${sitiosEndpoint}${selectedSitio!.id}/actividades/`;
        try {
            await postData(actividadEndpoint, currentActividad);
            toast({title: "Actividad Añadida"});
            setShowActividadForm(false);
            setCurrentActividad(initialActividadState);
            loadSingleSitio(selectedSitio!.id!); // Recargar datos
        } catch (error) {
            toast({ title: "Error", description: "No se pudo guardar la actividad.", variant: "destructive" });
        }
    };

     const handleDeleteActividad = async (actividadId: number) => {
        if(window.confirm("¿Seguro que quieres eliminar esta actividad?")) {
            const actividadEndpoint = `${sitiosEndpoint}${selectedSitio!.id}/actividades/${actividadId}/`;
            try {
                await deleteData(actividadEndpoint);
                toast({ title: "Actividad Eliminada" });
                loadSingleSitio(selectedSitio!.id!); // Recargar datos
            } catch (error) {
                toast({ title: "Error al eliminar actividad" });
            }
        }
    };


    // --- Render Functions ---
    const renderSitioList = () => (
      <div>
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Mis Sitios Turísticos</h1>
          <Button onClick={() => { setShowSitioForm(true); setIsEditingSitio(false); setCurrentSitio(initialSitioState)}}>
            <PlusCircle className="mr-2 h-4 w-4" /> Registrar Nuevo Sitio
          </Button>
        </div>
        {isLoading ? <p>Cargando...</p> : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {sitios.map(s => (
                    <Card key={s.id} className="cursor-pointer hover:shadow-lg" onClick={() => handleSelectSitio(s)}>
                        <CardHeader>
                            <CardTitle><Building className="inline-block mr-2"/>{s.nombre}</CardTitle>
                            <CardDescription>{s.descripcion_corta}</CardDescription>
                        </CardHeader>
                        <CardContent><p className={`font-bold ${s.activo ? 'text-green-600' : 'text-gray-500'}`}>{s.activo ? 'Abierto al público' : 'Cerrado'}</p></CardContent>
                    </Card>
                ))}
            </div>
        )}
      </div>
    );

    const renderSitioForm = () => (
        <Card>
            <CardHeader>
                <div className="flex justify-between items-center">
                    <CardTitle>{isEditingSitio ? 'Editando Sitio' : 'Nuevo Sitio Turístico'}</CardTitle>
                    <Button variant="ghost" size="icon" onClick={resetToListView}><X/></Button>
                </div>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSitioSubmit} className="space-y-4">
                    <Input name="nombre" placeholder="Nombre del sitio" value={currentSitio.nombre} onChange={(e) => setCurrentSitio({...currentSitio, nombre: e.target.value})} required/>
                    <Input name="descripcion_corta" placeholder="Descripción corta" value={currentSitio.descripcion_corta} onChange={(e) => setCurrentSitio({...currentSitio, descripcion_corta: e.target.value})} required/>
                    <Textarea name="descripcion_larga" placeholder="Descripción detallada" value={currentSitio.descripcion_larga} onChange={(e) => setCurrentSitio({...currentSitio, descripcion_larga: e.target.value})}/>
                    <div className="flex justify-end gap-2"><Button type="button" variant="outline" onClick={resetToListView}>Cancelar</Button><Button type="submit">Guardar Sitio</Button></div>
                </form>
            </CardContent>
        </Card>
    );

    const renderSitioDetail = () => (
      <div>
        <Button variant="outline" onClick={resetToListView} className="mb-4"><ArrowLeft className="mr-2 h-4 w-4" /> Volver al listado</Button>
        <Card className="mb-6">
            <CardHeader>
                <div className="flex justify-between items-center">
                    <div>
                        <CardTitle>{selectedSitio?.nombre}</CardTitle>
                        <CardDescription>{selectedSitio?.descripcion_corta}</CardDescription>
                    </div>
                    <div className="flex gap-2">
                        <Button variant="outline" onClick={() => handleEditSitio(selectedSitio!)}>Editar</Button>
                        <Button variant="destructive" onClick={() => handleDeleteSitio(selectedSitio!.id!)}>Eliminar</Button>
                    </div>
                </div>
            </CardHeader>
            <CardContent><p>{selectedSitio?.descripcion_larga}</p></CardContent>
        </Card>

        {/* Actividades */}
        <Card>
            <CardHeader>
                <div className="flex justify-between items-center">
                    <CardTitle>Actividades en el Sitio</CardTitle>
                    <Button size="sm" onClick={() => setShowActividadForm(!showActividadForm)}><Plus className="mr-2 h-4 w-4"/>Añadir Actividad</Button>
                </div>
            </CardHeader>
            <CardContent>
                {showActividadForm && (
                     <form onSubmit={handleActividadSubmit} className="space-y-2 p-4 mb-4 border rounded">
                        <Input placeholder="Nombre actividad" value={currentActividad.nombre} onChange={(e) => setCurrentActividad({...currentActividad, nombre: e.target.value})} required/>
                        <Textarea placeholder="Descripción" value={currentActividad.descripcion} onChange={(e) => setCurrentActividad({...currentActividad, descripcion: e.target.value})} required/>
                        <Input type="number" placeholder="Precio adicional" value={currentActividad.precio_adicional} onChange={(e) => setCurrentActividad({...currentActividad, precio_adicional: Number(e.target.value)})} required/>
                        <div className="flex justify-end gap-2"><Button type="button" size="sm" variant="ghost" onClick={() => setShowActividadForm(false)}>Cancelar</Button><Button size="sm" type="submit">Guardar</Button></div>
                     </form>
                )}
                <div className="space-y-2">
                    {selectedSitio?.actividades.map(act => (
                        <div key={act.id} className="flex justify-between items-center p-2 border rounded">
                           <div><p className="font-bold">{act.nombre}</p><p className="text-sm">{act.descripcion}</p></div>
                           <div className="flex items-center gap-4">
                                <span className="font-semibold">${act.precio_adicional.toLocaleString()}</span>
                                <Button variant="destructive" size="icon" onClick={() => handleDeleteActividad(act.id!)}><Trash2 className="h-4 w-4"/></Button>
                           </div>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
      </div>
    );

    return (
        <div className="container mx-auto p-4">
            {showSitioForm ? renderSitioForm() : (selectedSitio ? renderSitioDetail() : renderSitioList())}
        </div>
    );
}
