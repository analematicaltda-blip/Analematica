"""Opt-in on-device example. IDs must come from the real authenticated domain."""
import os
import flet as ft
from sgacd_vault import DocumentScope,DocumentVault,VaultError

def main(page:ft.Page):
    page.title='Documentos cifrados locales'
    tenant=os.environ.get('SGACD_VAULT_TENANT_UUID')
    account=os.environ.get('SGACD_VAULT_ACCOUNT_UUID')
    if not tenant or not account:
        page.add(ft.Text('Seleccione una organización y cuenta autenticadas antes de utilizar el almacén. No se generan identidades de ejemplo.'))
        return
    vault=DocumentVault(DocumentScope(tenant,account))
    page.overlay.append(vault)
    notice=ft.Text('Solo se intercambian identificadores. El documento no se envía al servidor.')
    documents=ft.Dropdown(label='Documento local',options=[])
    async def perform(method):
        try:
            reply=await method()
            if reply['status']=='stored':
                documents.options.append(ft.dropdown.Option(reply['document_id']));documents.value=reply['document_id']
            elif reply['status']=='listed':documents.options=[ft.dropdown.Option(value) for value in reply['documents']]
            notice.value={'stored':'Documento cifrado y guardado en este dispositivo.','listed':'Listado local actualizado.','verified':'Integridad comprobada; no se ha exportado el contenido.','provisioned':'Llave creada. Conserve la política de recuperación de esta cuenta.'}[reply['status']]
        except VaultError as error:notice.value='No se pudo confirmar la operación: '+str(error)+'. Actualice el listado antes de repetir.'
        page.update()
    async def provision(event):await perform(lambda:vault.provision(confirm_new_key=True))
    async def import_document(event):await perform(vault.import_document)
    async def refresh(event):await perform(vault.list_documents)
    async def verify(event):
        if documents.value:await perform(lambda:vault.verify_document(documents.value))
    page.add(ft.Text('Almacén local de documentos'),notice,
             ft.ElevatedButton('Crear llave nueva (requiere confirmación local)',on_click=provision),
             ft.ElevatedButton('Seleccionar y cifrar documento',on_click=import_document),
             ft.ElevatedButton('Actualizar listado',on_click=refresh),documents,
             ft.ElevatedButton('Comprobar documento con la protección del dispositivo',on_click=verify))

if __name__=='__main__':ft.app(target=main)
