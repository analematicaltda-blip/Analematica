import httpClient from '../index';

export const saritaEndpoints = {
  triggerMission: (type: string, parameters: any) => httpClient.post('/sarita/directive/', {
      domain: 'prestadores',
      mission: { type },
      parameters
  }),
  getMissionStatus: (id: string) => httpClient.get(`/sarita/missions/${id}/`),
};
