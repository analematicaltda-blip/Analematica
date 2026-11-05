import { httpClient } from '../../../../../../../../sarita-platform/shared-sdk/src/api/httpClient';

export const hotelService = {
  getRoomTypes: () => httpClient.get('/mi-negocio/operativa/esp/hoteles/room-types/'),
  getRooms: () => httpClient.get('/mi-negocio/operativa/esp/hoteles/rooms/'),
  createRoom: (data: any) => httpClient.post('/mi-negocio/operativa/esp/hoteles/rooms/', data),
  updateRoom: (id: number, data: any) => httpClient.patch(`/mi-negocio/operativa/esp/hoteles/rooms/${id}/`, data),
  deleteRoom: (id: number) => httpClient.delete(`/mi-negocio/operativa/esp/hoteles/rooms/${id}/`),

  // Catálogo unificado (apps/turismo)
  getUnifiedProvider: () => httpClient.get('/providers/tourism-providers/me/'),
};
