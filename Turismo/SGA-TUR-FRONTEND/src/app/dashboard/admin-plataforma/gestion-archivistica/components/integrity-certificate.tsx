"use client";

import React from 'react';

// --- Componentes de UI Reales ---
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/skeleton";
import { Copy, ExternalLink, CheckCircle2, AlertTriangle, Hourglass, ShieldCheck } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

const InfoRow = ({ label, value }) => {
    const { toast } = useToast();
    const onCopy = () => {
        navigator.clipboard.writeText(value);
        toast({ title: `${label} copiado` });
    };
    return (
        <div>
            <span className="text-sm font-medium text-muted-foreground">{label}</span>
            <div className="flex items-center gap-2">
                <p className="text-sm font-mono break-all w-48 truncate">{value}</p>
                <Button variant="ghost" size="icon" className="h-6 w-6" onClick={onCopy}><Copy className="h-3 w-3" /></Button>
            </div>
        </div>
    );
};

const StatusBadge = ({ status }) => {
    const statusConfig = {
        VERIFIED: { variant: "default", icon: <CheckCircle2 className="mr-2 h-4 w-4" />, label: "Verificado", className: "bg-green-600 text-white" },
        PENDING_CONFIRMATION: { variant: "secondary", icon: <Hourglass className="mr-2 h-4 w-4 animate-spin" />, label: "Pendiente Notarización" },
        COMPROMISED: { variant: "destructive", icon: <AlertTriangle className="mr-2 h-4 w-4" />, label: "Comprometido" },
        PENDING_UPLOAD: { variant: "outline", icon: <Hourglass className="mr-2 h-4 w-4" />, label: "Procesando" },
    };
    const config = statusConfig[status] || statusConfig.PENDING_UPLOAD;
    return <Badge variant={config.variant as any} className={config.className}>{config.icon}{config.label}</Badge>;
};

export function IntegrityCertificate({ version }) {
    if (!version) {
        return <Skeleton className="h-96 w-full" />;
    }

    const isVerified = version.status === 'VERIFIED';

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2"><ShieldCheck className="h-6 w-6 text-primary"/>Certificado de Integridad</CardTitle>
                <CardDescription>Prueba criptográfica de la existencia e integridad del documento.</CardDescription>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    <div>
                        <span className="text-sm font-medium text-muted-foreground">Estado</span>
                        <StatusBadge status={version.status} />
                    </div>
                    {version.file_hash_sha256 && <InfoRow label="Huella Digital (SHA-256)" value={version.file_hash_sha256} />}
                    {isVerified && version.blockchain_timestamp && <InfoRow label="Fecha de Verificación (UTC)" value={new Date(version.blockchain_timestamp).toLocaleString()} />}
                    {isVerified && version.blockchain_transaction && (
                        <div>
                            <span className="text-sm font-medium text-muted-foreground">Prueba en Blockchain</span>
                            <a href={`https://polygonscan.com/tx/${version.blockchain_transaction}`} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-sm text-primary hover:underline font-mono break-all">
                                <span className="truncate w-48">{version.blockchain_transaction}</span>
                                <ExternalLink className="h-4 w-4" />
                            </a>
                        </div>
                    )}
                    <div className="border-t pt-4">
                        <Button className="w-full" disabled={!isVerified}>
                            <ShieldCheck className="mr-2 h-4 w-4" />
                            Verificar Integridad Ahora
                        </Button>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
