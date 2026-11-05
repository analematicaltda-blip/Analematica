'use client';
import { useEffect, useState } from 'react';
import { useMiNegocioApi } from '@/app/dashboard/prestador/mi-negocio/hooks/useMiNegocioApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/Table';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Skeleton } from '@/components/ui/skeleton';
import { toast } from 'react-toastify';
import { UploadCloud } from 'lucide-react';

// Asumiendo una interfaz simple para el documento
interface ArchivoDocumento {
  id: string;
  name: string;
  size: number;
  upload_date: string;
  version: number;
  status: string;
}

const GestionArchivisticaPage = () => {
  const { getArchivisticaDocumentos, uploadArchivisticaDocumento, isLoading } = useMiNegocioApi();
  const [documentos, setDocumentos] = useState<ArchivoDocumento[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  useEffect(() => {
    const fetchDocumentos = async () => {
      const data = await getArchivisticaDocumentos();
      if (data) setDocumentos(data);
      else toast.error('No se pudieron cargar los documentos.');
    };
    fetchDocumentos();
  }, [getArchivisticaDocumentos]);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setSelectedFile(event.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.warn('Por favor, seleccione un archivo primero.');
      return;
    }
    // Metadata de ejemplo
    const metadata = { description: 'Documento subido desde el frontend' };
    const result = await uploadArchivisticaDocumento(selectedFile, metadata);
    if (result) {
      // Recargar la lista de documentos
      const data = await getArchivisticaDocumentos();
      if (data) setDocumentos(data);
      setSelectedFile(null);
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Gestión Archivística</h1>
        <div className="flex items-center gap-2">
          <Input type="file" onChange={handleFileChange} />
          <Button onClick={handleUpload} disabled={isLoading || !selectedFile}>
            <UploadCloud className="h-4 w-4 mr-2" /> Subir Documento
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader><CardTitle>Repositorio de Documentos</CardTitle></CardHeader>
        <CardContent>
          {isLoading && documentos.length === 0 ? (
            <div className="space-y-2"><Skeleton className="h-10 w-full" /><Skeleton className="h-10 w-full" /></div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nombre</TableHead><TableHead>Versión</TableHead><TableHead>Fecha de Subida</TableHead>
                  <TableHead>Estado</TableHead><TableHead className="text-right">Tamaño (KB)</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {documentos.length > 0 ? documentos.map((doc) => (
                    <TableRow key={doc.id}>
                      <TableCell>{doc.name}</TableCell>
                      <TableCell>v{doc.version}</TableCell>
                      <TableCell>{new Date(doc.upload_date).toLocaleDateString()}</TableCell>
                      <TableCell>{doc.status}</TableCell>
                      <TableCell className="text-right">{(doc.size / 1024).toFixed(2)}</TableCell>
                    </TableRow>
                  )) : (
                  <TableRow><TableCell colSpan={5} className="text-center">No hay documentos en el archivo.</TableCell></TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default GestionArchivisticaPage;
