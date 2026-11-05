import httpClient from '../index';

export const voiceEndpoints = {
  sendIntent: (text: string) => httpClient.post('/v1/marketing/intent/', { text }),
  sendAudio: (audioBlob: Blob) => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'command.wav');
    return httpClient.post('/v1/marketing/audio/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  getMissionStatus: (id: string) => httpClient.get(`/api/sarita/missions/${id}/`),
  getVoiceLogs: () => httpClient.get('/api/voice/logs/'),
};
