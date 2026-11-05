// frontend/src/app/dashboard/prestador/mi-negocio/gestion-archivistica/[documentId]/page.tsx
"use client";

import React, { useState } from 'react';
import { useQuery, useMutation } from "@tanstack/react-query";
import { useParams } from 'next/navigation';
import apiClient from "@/services/api";
import { Button } from "@/components/ui/Button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertTriangle, Download, ChevronsRight, Hash, ShieldCheck, Upload } from 'lucide-react';
import Link from 'next/link';
import { PageHeader } from '@/components/shared/page-header';
import { UploadDialog } from '../components/upload-dialog';
import { toast } from 'react-hot-toast';

// --- Tipos de Datos ---
interface VersionData {
    id: number;
    version_number: number;
    title: string;
    status: "PENDING_UPLOAD" | "PENDING_CONFIRMATION" | "VERIFIED" | "COMPROMISED";
    uploaded_at: string;
    original_filename: string;
    file_hash_sha256: string | null;
    merkle_root: string | null;
    blockchain_transaction: string | null;
    blockchain_timestamp: string | null;
}

interface DocumentDetailData {
    id: string;
    document_code: string;
    title: string; // Título de la primera versión
    versions: VersionData[];
}

const fetchDocumentDetail = async (id: string): Promise<DocumentDetailData> => {
    const response = await apiClient.get(`/mi-negocio/archivistica/documents/${id}/`);
    return response.data;
};

const downloadVersion = async ({ docId, versionId, filename }: { docId: string; versionId: number; filename: string }) => {
    const response = await apiClient.get(`/mi-negocio/archivistica/documents/${docId}/versions/${versionId}/download/`, {
        responseType: 'blob',
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.parentNode?.removeChild(link);
};


// --- Componentes de UI ---
// ... CryptoProof y statusVariant se mantienen igual ...
const CryptoProof = ({ version }: { version: VersionData }) => {
    if (version.status !== 'VERIFIED') return null;
    return (
        <div className="bg-gray-50 p-4 rounded-lg mt-4 border">
            <h4 className="font-semibold text-md mb-2 flex items-center"><ShieldCheck className="mr-2 h-5 w-5 text-green-600"/> Prueba Criptográfica</h4>
            <div className="text-sm space-y-2">
                <div className="flex justify-between">
                    <span className="font-medium text-gray-600">Hash (SHA-256):</span>
                    <code className="text-xs truncate">{version.file_hash_sha256}</code>
                </div>
                <div className="flex justify-between">
                    <span className="font-medium text-gray-600">Raíz de Merkle:</span>
                    <code className="text-xs truncate">{version.merkle_root}</code>
                </div>
                <div className="flex justify-between items-center">
                    <span className="font-medium text-gray-600">Transacción Blockchain:</span>
                    <Link href={`https://polygonscan.com/tx/${version.blockchain_transaction}`} target="_blank" className="text-blue-600 hover:underline">
                        <code className="text-xs truncate">{version.blockchain_transaction}</code>
                    </Link>
                </div>
            </div>
        </div>
    );
};

// --- Componente Principal ---
export default function DocumentDetailPage() {
    const params = useParams();
    const documentId = params.documentId as string;
    const [downloadingId, setDownloadingId] = useState<number | null>(null);

    const { data: document, isLoading, isError, error } = useQuery<DocumentDetailData, Error>({
        queryKey: ['archivisticaDocumentDetail', documentId],
        queryFn: () => fetchDocumentDetail(documentId),
        enabled: !!documentId,
    });

    const downloadMutation = useMutation({
        mutationFn: downloadVersion,
        onSuccess: () => {
            toast.success("Descarga iniciada.");
            setDownloadingId(null);
        },
        onError: (error: any) => {
            toast.error("No se pudo descargar el archivo.");
            setDownloadingId(null);
        }
    });

    const handleDownload = (version: VersionData) => {
        setDownloadingId(version.id);
        downloadMutation.mutate({
            docId: documentId,
            versionId: version.id,
            filename: version.original_filename
        });
    };

    if (isLoading) return <div>Cargando detalle del documento...</div>;
    if (isError) return <Alert variant="destructive"><AlertTriangle className="h-4 w-4" /><AlertTitle>Error</AlertTitle><AlertDescription>{error.message}</AlertDescription></Alert>;

    return (
        <div className="flex flex-col gap-8">
            <PageHeader
                title={`Documento: ${document?.document_code}`}
                description={`Historial de versiones para "${document?.title}".`}
            >
                {/* Asumimos que UploadDialog puede manejar una prop para subir una nueva versión */}
                {/* <UploadDialog documentId={documentId}><Button><Upload className="mr-2 h-4 w-4"/>Subir Nueva Versión</Button></UploadDialog> */}
            </PageHeader>

            <div className="space-y-6">
                {document?.versions.map(version => (
                    <div key={version.id} className="border p-4 rounded-lg">
                        <div className="flex justify-between items-start">
                            <div>
                                <h3 className="font-bold text-lg">{version.title} (v{version.version_number})</h3>
                                <p className="text-sm text-gray-500">Subido el {new Date(version.uploaded_at).toLocaleString()}</p>
                            </div>
                            <div className="flex items-center gap-4">
                                <span className="p-2 bg-gray-200 rounded">{version.status.replace(/_/g, ' ')}</span>
                                <Button
                                    size="sm"
                                    variant="outline"
                                    disabled={version.status !== 'VERIFIED' || downloadingId === version.id}
                                    onClick={() => handleDownload(version)}
                                >
                                    {downloadingId === version.id ? 'Descargando...' : <><Download className="mr-2 h-4 w-4"/>Descargar</>}
                                </Button>
                            </div>
                        </div>
                        <CryptoProof version={version} />
                    </div>
                ))}
            </div>
        </div>
    );
}
