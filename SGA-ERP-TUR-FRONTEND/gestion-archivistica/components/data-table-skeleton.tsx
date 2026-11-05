// frontend/src/app/dashboard/prestador/mi-negocio/gestion-archivistica/components/data-table-skeleton.tsx
import React from 'react';
import { Skeleton } from '@/components/ui/skeleton';

export const DataTableSkeleton = ({ columnCount = 5, rowCount = 5 }) => {
    return (
        <div className="space-y-4">
            <div className="flex justify-between">
                <Skeleton className="h-10 w-64" />
                <Skeleton className="h-10 w-32" />
            </div>
            <div className="space-y-2">
                {[...Array(rowCount)].map((_, i) => (
                    <div key={i} className="flex gap-2">
                        {[...Array(columnCount)].map((_, j) => (
                            <Skeleton key={j} className="h-10 flex-1" />
                        ))}
                    </div>
                ))}
            </div>
        </div>
    );
};
