'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { toast } from 'react-toastify';
import { FiEdit, FiTrash2, FiPlusCircle } from 'react-icons/fi';
import api from '@/services/api';
// Asumiremos que crearemos un DownloadLinkFormModal similar a PlanFormModal
// import DownloadLinkFormModal from './DownloadLinkFormModal';

interface DownloadLink {
    id: number;
    nombre: string;
    plataforma: string;
    url: string;
    version: string;
    is_active: boolean;
}

export default function AdminDownloadsPage() {
    const [links, setLinks] = useState<DownloadLink[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchLinks = useCallback(async () => {
        try {
            setIsLoading(true);
            const response = await api.get('/downloads/admin/links/');
            setLinks(response.data.results || []);
        } catch (err) {
            setError('No se pudieron cargar los enlaces.');
            toast.error('No se pudieron cargar los enlaces.');
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchLinks();
    }, [fetchLinks]);

    // Aquí iría la lógica para handleDelete, handleOpenModal, etc.
    // Por simplicidad en este paso, solo se muestra la tabla.

    if (isLoading) {
        return <p>Cargando enlaces de descarga...</p>;
    }

    if (error) {
        return <p className="text-red-500">{error}</p>;
    }

    return (
        <Card>
            <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Gestión de Enlaces de Descarga</CardTitle>
                <Button>
                    <FiPlusCircle className="mr-2 h-4 w-4" />
                    Añadir Nuevo Enlace
                </Button>
            </CardHeader>
            <CardContent>
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Nombre</TableHead>
                            <TableHead>Plataforma</TableHead>
                            <TableHead>Versión</TableHead>
                            <TableHead>URL</TableHead>
                            <TableHead>Estado</TableHead>
                            <TableHead>Acciones</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {links.map((link) => (
                            <TableRow key={link.id}>
                                <TableCell className="font-medium">{link.nombre}</TableCell>
                                <TableCell>{link.plataforma}</TableCell>
                                <TableCell>{link.version}</TableCell>
                                <TableCell><a href={link.url} className="text-blue-600 hover:underline">{link.url}</a></TableCell>
                                <TableCell>
                                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${link.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                        {link.is_active ? 'Activo' : 'Inactivo'}
                                    </span>
                                </TableCell>
                                <TableCell className="flex gap-2">
                                    <Button variant="outline" size="sm">
                                        <FiEdit className="h-4 w-4" />
                                    </Button>
                                    <Button variant="destructive" size="sm">
                                        <FiTrash2 className="h-4 w-4" />
                                    </Button>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    );
}
