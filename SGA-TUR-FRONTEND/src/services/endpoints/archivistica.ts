import httpClient from '../index';

export const archivisticaEndpoints = {
  getDocumentos: () => httpClient.get('/v1/mi-negocio/archivistica/documents/'),
};
