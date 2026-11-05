"use client";

import React, { useState, useEffect } from 'react';
import { touristService } from '@/services/tripleViaService';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';

export default function TouristDashboard() {
  const [destinations, setDestinations] = useState([]);

  useEffect(() => {
    touristService.getDestinations().then(res => setDestinations(res.data.results || []));
  }, []);

  return (
    <div className="p-8 space-y-6">
      <h1 className="text-3xl font-black">Mi Viaje</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {destinations.map((dest: any) => (
          <Card key={dest.id}>
            <CardHeader><CardTitle>{dest.name}</CardTitle></CardHeader>
            <CardContent>
              <p className="text-sm">{dest.provider_type}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
