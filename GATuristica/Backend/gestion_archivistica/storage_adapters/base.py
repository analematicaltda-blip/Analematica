from abc import ABC, abstractmethod

class BaseStorageAdapter(ABC):
    """
    Define la interfaz abstracta (el "contrato") que cualquier adaptador
    de almacenamiento en la nube debe cumplir.
    """

    @abstractmethod
    def upload(self, encrypted_content: bytes, cloud_filename: str) -> str:
        """
        Sube el contenido de un archivo (ya cifrado) al proveedor de la nube.
        Returns: El identificador único (ID/clave) del archivo en el proveedor.
        """
        pass

    @abstractmethod
    def download(self, external_id: str) -> bytes:
        """
        Descarga un archivo desde el proveedor de la nube usando su ID externo.
        """
        pass

    @abstractmethod
    def delete(self, external_id: str) -> bool:
        """
        Elimina permanentemente un archivo del proveedor de la nube.
        """
        pass
