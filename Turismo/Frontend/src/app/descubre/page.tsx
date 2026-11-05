'use client';

import React from 'react';
import { AttractionCard, EventCalendar, InteractiveRouteMap } from '@sarita/shared-ui';

const TOURIST_MOCK = {
  attractions: [
    { id: '1', name: 'Río Manacacías', category: 'Naturaleza', description: 'Avistamiento de delfines rosados y atardeceres únicos.', imageUrl: 'https://images.unsplash.com/photo-1501785888041-af3ef285b470' },
    { id: '2', name: 'Arco de la Maloca', category: 'Cultura', description: 'Monumento emblemático de la cultura llanera.', imageUrl: 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b' }
  ],
  events: [
    { id: '1', title: 'Festival del Retorno', date: 'Octubre 2026', location: 'Plaza Principal' },
    { id: '2', title: 'Muestra Gastronómica', date: 'Abril 12', location: 'Puerto Malecón' }
  ],
  route: {
    name: 'Ruta del Amanecer Llanero',
    points: [
      { label: 'Puerto Gaitán', type: 'Punto de Inicio' },
      { label: 'Mirador del Manacacías', type: 'Atractivo Natural' },
      { label: 'Finca La Esperanza', type: 'Agroturismo' }
    ]
  },
  marketplace: {
    trending: [
      { id: '1', name: 'Avistamiento de Toninas', price: 45000, rating: 4.9, reviews: 124 },
      { id: '2', name: 'Safari Fotográfico', price: 85000, rating: 4.8, reviews: 89 }
    ],
    recommended: [
      { id: '3', name: 'Cena Romántica en el Río', price: 120000, rating: 5.0, reviews: 45 },
      { id: '4', name: 'Tour de Pesca Deportiva', price: 200000, rating: 4.7, reviews: 67 }
    ]
  }
};

export default function DescubrePage() {
  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb', padding: '40px' }}>
      <h1 style={{ fontSize: '32px', fontWeight: 'bold', color: '#1e40af', marginBottom: '40px' }}>Descubre el Paraíso</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '32px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
          <section>
            <h2 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '16px' }}>Atractivos Destacados</h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
              {TOURIST_MOCK.attractions.map(attr => (
                <AttractionCard key={attr.id} attraction={attr} />
              ))}
            </div>
          </section>

          <section>
            <h2 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '16px' }}>Tendencias del Destino</h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
              {TOURIST_MOCK.marketplace.trending.map(item => (
                <div key={item.id} style={{ padding: '20px', backgroundColor: '#fff', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
                  <h3 style={{ fontWeight: 'bold' }}>{item.name}</h3>
                  <p style={{ fontSize: '14px', color: '#6b7280' }}>Desde ${item.price}</p>
                  <p style={{ fontSize: '12px', color: '#f59e0b' }}>★ {item.rating} ({item.reviews} reseñas)</p>
                </div>
              ))}
            </div>
          </section>

          <section>
            <h2 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '16px' }}>Experiencias Recomendadas</h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
              {TOURIST_MOCK.marketplace.recommended.map(item => (
                <div key={item.id} style={{ padding: '20px', backgroundColor: '#fff', borderRadius: '12px', border: '1px solid #6366f1', borderWidth: '2px' }}>
                  <h3 style={{ fontWeight: 'bold' }}>{item.name}</h3>
                  <p style={{ fontSize: '14px', color: '#6b7280' }}>Desde ${item.price}</p>
                  <p style={{ fontSize: '12px', color: '#f59e0b' }}>★ {item.rating} ({item.reviews} reseñas)</p>
                </div>
              ))}
            </div>
          </section>

          <InteractiveRouteMap routeName={TOURIST_MOCK.route.name} points={TOURIST_MOCK.route.points} />
        </div>

        <aside>
          <div style={{ marginBottom: '32px' }}>
             <h2 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '16px' }}>Servicios Mejor Valorados</h2>
             <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {TOURIST_MOCK.marketplace.trending.map(item => (
                   <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '12px', backgroundColor: '#fff', borderRadius: '8px' }}>
                      <span style={{ fontSize: '14px', fontWeight: '600' }}>{item.name}</span>
                      <span style={{ color: '#f59e0b', fontWeight: 'bold' }}>★ {item.rating}</span>
                   </div>
                ))}
             </div>
          </div>
          <EventCalendar events={TOURIST_MOCK.events} />
        </aside>
      </div>
    </div>
  );
}
