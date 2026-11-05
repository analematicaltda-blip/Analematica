'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { toast } from 'react-toastify';
import { FiEdit, FiTrash2, FiPlus, FiMonitor, FiGlobe, FiEye } from 'react-icons/fi';
import api from '@/services/api';
import { Badge } from '@/components/ui/Badge';

interface WebPage {
    id: number;
    title: string;
    slug: string;
    is_published: boolean;
}

export default function WebContentPage() {
    const [pages, setPages] = useState<WebPage[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    const fetchPages = useCallback(async () => {
        try {
            setIsLoading(true);
            const response = await api.get('/web/admin/pages/');
            setPages(response.data.results || []);
        } catch (err) {
            // toast.error('No se pudieron cargar las páginas.');
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchPages();
    }, [fetchPages]);

    return (
        <div className="space-y-10 animate-in fade-in duration-700">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div>
                    <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight uppercase italic leading-none mb-2">Gobernanza del Contenido Digital</h1>
                    <p className="text-slate-500 dark:text-slate-400 text-lg">Control maestro de la presencia web y el funnel de ventas conversacional.</p>
                </div>
                <Button className="bg-brand text-white font-black px-8 py-6 rounded-2xl shadow-xl shadow-brand/20">
                    <FiPlus className="mr-2" /> Nueva Página Maestro
                </Button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
               <Card className="lg:col-span-2 border-none shadow-sm bg-white dark:bg-brand-deep/10 overflow-hidden">
                  <CardHeader className="p-8 border-b border-slate-50 dark:border-white/5 flex flex-row items-center justify-between">
                     <CardTitle className="text-xl font-bold flex items-center gap-3 text-brand italic">
                        <FiMonitor /> Catálogo de Páginas
                     </CardTitle>
                  </CardHeader>
                  <CardContent className="p-0">
                     <Table>
                        <TableHeader className="bg-slate-50 dark:bg-black/40">
                           <TableRow>
                              <TableHead className="font-bold text-[10px] uppercase tracking-widest px-8">Título de Página</TableHead>
                              <TableHead className="font-bold text-[10px] uppercase tracking-widest">Identificador (Slug)</TableHead>
                              <TableHead className="font-bold text-[10px] uppercase tracking-widest">Estatus</TableHead>
                              <TableHead className="font-bold text-[10px] uppercase tracking-widest text-right px-8">Acciones</TableHead>
                           </TableRow>
                        </TableHeader>
                        <TableBody>
                           {pages.map((page) => (
                             <TableRow key={page.id} className="hover:bg-slate-50 dark:hover:bg-white/5 transition-colors border-slate-50 dark:border-white/5">
                                <TableCell className="font-black text-slate-900 dark:text-white px-8 uppercase tracking-tighter italic">{page.title}</TableCell>
                                <TableCell className="font-mono text-xs text-slate-400">/{page.slug}</TableCell>
                                <TableCell>
                                   <Badge className={page.is_published ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}>
                                      {page.is_published ? 'PUBLICADA' : 'BORRADOR'}
                                   </Badge>
                                </TableCell>
                                <TableCell className="text-right px-8">
                                   <div className="flex justify-end gap-1">
                                      <Button variant="ghost" size="sm" className="h-10 w-10 p-0 hover:text-brand"><FiEye size={16} /></Button>
                                      <Button variant="ghost" size="sm" className="h-10 w-10 p-0 hover:text-brand"><FiEdit size={16} /></Button>
                                      <Button variant="ghost" size="sm" className="h-10 w-10 p-0 hover:text-red-500"><FiTrash2 size={16} /></Button>
                                   </div>
                                </TableCell>
                             </TableRow>
                           ))}
                           {pages.length === 0 && !isLoading && (
                             <TableRow>
                                <TableCell colSpan={4} className="text-center py-24 text-slate-400 font-bold italic">
                                   No se han detectado páginas maestras.
                                </TableCell>
                             </TableRow>
                           )}
                        </TableBody>
                     </Table>
                  </CardContent>
               </Card>

               <div className="space-y-6">
                  <Card className="border-none shadow-xl bg-slate-900 text-white p-10 rounded-3xl relative overflow-hidden group cursor-pointer">
                     <div className="absolute -right-6 -bottom-6 opacity-20 group-hover:scale-110 transition-transform duration-700">
                        <FiGlobe size={180} />
                     </div>
                     <p className="text-[10px] font-black uppercase tracking-widest text-brand-light mb-4 italic">Nodo Web Central</p>
                     <h3 className="text-3xl font-black leading-tight">Optimización SEO Sistémica Activa</h3>
                     <p className="mt-6 text-sm text-slate-400 font-medium leading-relaxed">SADI está ajustando los meta-tags de las rutas de atractivos para maximizar el tráfico orgánico.</p>
                  </Card>

                  <Card className="border-none shadow-sm bg-white dark:bg-brand-deep/20 p-8 rounded-3xl">
                     <h4 className="font-black text-slate-900 dark:text-white uppercase tracking-widest text-xs mb-6 italic">Assets Multimedia</h4>
                     <div className="grid grid-cols-2 gap-4">
                        <div className="aspect-square rounded-2xl bg-slate-100 dark:bg-black/20 flex flex-col items-center justify-center border-2 border-dashed border-slate-200 dark:border-white/5 text-slate-400 hover:text-brand hover:border-brand/40 transition-all cursor-pointer">
                           <FiPlus size={24} />
                           <span className="text-[10px] font-black uppercase mt-2">Subir</span>
                        </div>
                        <div className="aspect-square rounded-2xl bg-slate-100 dark:bg-black/20 animate-pulse" />
                     </div>
                  </Card>
               </div>
            </div>
        </div>
    );
}
