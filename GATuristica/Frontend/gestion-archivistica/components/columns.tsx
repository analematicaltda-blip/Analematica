// frontend/src/app/dashboard/prestador/mi-negocio/gestion-archivistica/components/columns.tsx
"use client"

import { ColumnDef } from "@tanstack/react-table"
import { MoreHorizontal, ArrowUpDown } from "lucide-react"
import Link from "next/link"

import { Button } from "@/components/ui/Button"
// Eliminado Dropdown
// Eliminado Badge

// --- Tipos de Datos ---
// Este tipo debe coincidir con lo que devuelve el DocumentListSerializer del backend
export type DocumentData = {
    id: string
    document_code: string
    title: string
    last_version_status: "PENDING_UPLOAD" | "PENDING_CONFIRMATION" | "VERIFIED" | "COMPROMISED" | null
    created_at: string
}

const statusVariant = {
    PENDING_UPLOAD: "secondary",
    PENDING_CONFIRMATION: "warning",
    VERIFIED: "success",
    COMPROMISED: "destructive",
}

export const columns: ColumnDef<DocumentData>[] = [
    {
        accessorKey: "document_code",
        header: ({ column }) => (
            <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
                Código
                <ArrowUpDown className="ml-2 h-4 w-4" />
            </Button>
        ),
    },
    {
        accessorKey: "title",
        header: "Título",
        // Hacemos que el título sea un enlace a la página de detalle
        cell: ({ row }) => (
            <Link href={`/dashboard/prestador/mi-negocio/gestion-archivistica/${row.original.id}`}>
                <span className="font-medium text-blue-600 hover:underline">{row.getValue("title")}</span>
            </Link>
        )
    },
    {
        accessorKey: "last_version_status",
        header: "Estado Última Versión",
        cell: ({ row }) => {
            const status = row.getValue("last_version_status") as DocumentData["last_version_status"];
            if (!status) return <span className="text-gray-500">N/A</span>

            return (
                <span className="p-2 bg-gray-200 rounded">
                    {status.replace(/_/g, ' ')}
                </span>
            )
        },
    },
    {
        accessorKey: "created_at",
        header: "Fecha de Creación",
        cell: ({ row }) => new Date(row.getValue("created_at")).toLocaleDateString(),
    },
    {
        id: "actions",
        cell: ({ row }) => {
            const document = row.original
            return (
                <Link href={`/dashboard/prestador/mi-negocio/gestion-archivistica/${document.id}`}>
                    <Button variant="outline" size="sm">Ver Detalles</Button>
                </Link>
            )
        },
    },
]
