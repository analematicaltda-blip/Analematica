import api from './api';

export interface Department {
  id: number;
  name: string;
  municipalities: Municipality[];
}

export interface Municipality {
  id: number;
  name: string;
}

export const getDepartments = async (): Promise<Department[]> => {
  try {
    const response = await api.get<{ results: Department[] }>('/departments/');
    return response.data.results || response.data;
  } catch (error) {
    console.error('Error fetching departments:', error);
    throw error;
  }
};

export const getMunicipalitiesByDepartment = async (departmentId: number): Promise<Municipality[]> => {
  try {
    // La API de departamentos ya devuelve los municipios anidados.
    // Buscamos en el array completo para encontrar el que corresponde.
    const response = await api.get<{ results: Department[] }>('/departments/');
    const departments = response.data.results || response.data;
    const department = departments.find(dep => dep.id === departmentId);
    return department ? department.municipalities : [];
  } catch (error) {
    console.error(`Error fetching municipalities for department ${departmentId}:`, error);
    throw error;
  }
};