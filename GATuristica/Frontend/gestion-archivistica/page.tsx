'use client';

import React, { useEffect, useState } from 'react';
import { useMiNegocioApi } from '../hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import {
  FiArchive,
  FiUpload,
  FiSearch,
  FiShield,
  FiFileText,
  FiClock,
  FiExternalLink
} from 'react-icons/fi';
import { Badge } from '@/components/ui/Badge';

interface Documento {
    id: string;
    document_code: string;
    process_name: string;
    document_type_name: string;
    current_version: number;
    status: string;
    created_at: string;
    blockchain_tx?: string;
}

export default function GestionArchivisticaPage() {
  const { getArchivisticaDocumentos, isLoading } = useMiNegocioApi();
  const [documents, setDocuments] = useState<Documento[]>([]);

  useEffect(() => {
    const loadData = async () => {
      const data = await getArchivisticaDocumentos();
      if (data) setDocuments(data as any);
    };
    loadData();
  }, [getArchivisticaDocumentos]);

  return (
    <div className="space-y-8 animate-in zoom-in-95 duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Gestión Archivística Digital</h1>
          <p className="text-gray-500 mt-1">Custodia documental, trazabilidad y notarización con Blockchain.</p>
        </div>
        <div className="flex gap-3">
          <Button className="bg-indigo-600 hover:bg-indigo-700 shadow-md">
            <FiUpload className="mr-2" /> Subir Documento
          </Button>
          <div className="relative group">
            <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por código o nombre..."
              className="pl-10 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none w-64 transition-all"
            />
          </div>
        </div>
      </div>

      {/* Trust Banner */}
      <div className="bg-gradient-to-r from-slate-900 to-indigo-900 rounded-2xl p-6 text-white flex items-center justify-between shadow-xl">
         <div className="flex items-center gap-6">
            <div className="w-16 h-16 bg-white/10 rounded-2xl flex items-center justify-center backdrop-blur-md">
               <FiShield size={32} className="text-indigo-300" />
            </div>
            <div>
               <h2 className="text-xl font-bold">Invariabilidad Garantizada</h2>
               <p className="text-indigo-200 text-sm max-w-md">Todos los documentos cargados en este módulo son hasheados y preparados para su registro en la red Polygon.</p>
            </div>
         </div>
         <div className="hidden lg:block text-right">
            <p className="text-xs text-indigo-300 uppercase font-black tracking-widest">Estado del Nodo</p>
            <p className="text-lg font-mono text-green-400">SYNCED ●</p>
         </div>
      </div>

      {/* Main Table */}
      <Card className="border-none shadow-sm overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between border-b border-gray-50">
           <CardTitle className="text-lg font-bold">Expediente Digital</CardTitle>
           <Badge variant="outline" className="font-mono">{documents.length} Documentos</Badge>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader className="bg-gray-50/50">
              <TableRow>
                <TableHead className="w-[150px]">Código</TableHead>
                <TableHead>Título / Proceso</TableHead>
                <TableHead>Versión</TableHead>
                <TableHead>Fecha</TableHead>
                <TableHead>Seguridad</TableHead>
                <TableHead className="text-right">Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {documents.map((doc) => (
                <TableRow key={doc.id} className="hover:bg-gray-50/50 transition-colors">
                  <TableCell className="font-mono text-xs font-bold text-indigo-600">{doc.document_code}</TableCell>
                  <TableCell>
                    <div className="flex flex-col">
                       <span className="font-medium text-gray-900 text-sm">Documento de Prueba</span>
                       <span className="text-[10px] text-gray-500 uppercase tracking-tighter">{doc.process_name}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                     <div className="flex items-center gap-1.5">
                        <FiClock size={12} className="text-gray-400" />
                        <span className="text-xs font-bold">v{doc.current_version}</span>
                     </div>
                  </TableCell>
                  <TableCell className="text-xs text-gray-600">
                    {new Date(doc.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <Badge className={doc.blockchain_tx ? "bg-green-100 text-green-700" : "bg-blue-100 text-blue-700"}>
                       {doc.blockchain_tx ? 'NOTARIZADO' : 'PROTEGIDO'}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                      <FiExternalLink size={16} />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {documents.length === 0 && !isLoading && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-20">
                     <div className="flex flex-col items-center opacity-20">
                        <FiArchive size={64} />
                        <p className="mt-4 font-bold">No hay documentos en el archivo digital.</p>
                     </div>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
