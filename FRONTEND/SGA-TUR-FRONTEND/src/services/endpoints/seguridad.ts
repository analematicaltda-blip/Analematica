import httpClient from '../index';

export const authEndpoints = {
  login: (credentials: any) => httpClient.post('/auth/login/', credentials),
  register: (role: string, data: any) => httpClient.post(`/auth/registration/${role}/`, data),
  getUser: () => httpClient.get('/auth/user/'),
  logout: () => httpClient.post('/auth/logout/'),
};
