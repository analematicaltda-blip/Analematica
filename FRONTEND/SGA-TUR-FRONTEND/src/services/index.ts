import httpClient from './httpClient';
import { setupInterceptors } from './interceptors';

setupInterceptors(httpClient);

export default httpClient;
export * from './httpClient';
