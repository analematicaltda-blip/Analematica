from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.api import deps
from app.crud.dropdown import crud_dropdowns, CRUDBase
from app.core.cache import cache_service

from app.models import user as user_model

def create_dropdown_router(
    crud_instance: CRUDBase,
    schema: schemas.Dropdown,
    create_schema: schemas.DropdownCreate,
    update_schema: schemas.DropdownUpdate,
    dropdown_type: str = ""
) -> APIRouter:

    router = APIRouter()

    @router.get("/", response_model=List[schema])
    def read_items(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: user_model.Usuario = Depends(deps.get_current_active_user),
    ) -> Any:
        """
        Retrieve all items for a specific dropdown for the current tenant, utilizing TTL cache.
        """
        tenant_id = current_user.inquilino_id
        cache_key = f"dropdown:{dropdown_type}:tenant:{tenant_id}:skip:{skip}:limit:{limit}"
        cached_data = cache_service.get(cache_key)
        if cached_data is not None:
            return cached_data

        items = crud_instance.get_multi_by_tenant(db, inquilino_id=tenant_id, skip=skip, limit=limit)
        cache_service.set(cache_key, items, ttl=300)
        return items

    @router.post("/", response_model=schema)
    def create_item(
        *,
        db: Session = Depends(deps.get_db),
        item_in: create_schema,
        current_user: user_model.Usuario = Depends(deps.role_required(["admin_empresa", "admin_general"])),
    ) -> Any:
        """
        Create a new dropdown item with tenant validation and cache invalidation.
        """
        if getattr(item_in, "inquilino_id", current_user.inquilino_id) != current_user.inquilino_id:
            raise HTTPException(status_code=403, detail="Cannot create item for another tenant.")

        item = crud_instance.create(db=db, obj_in=item_in)
        cache_service.invalidate_prefix(f"dropdown:{dropdown_type}:tenant:{current_user.inquilino_id}")
        return item

    @router.put("/{item_id}", response_model=schema)
    def update_item(
        *,
        db: Session = Depends(deps.get_db),
        item_id: int,
        item_in: update_schema,
        current_user: user_model.Usuario = Depends(deps.role_required(["admin_empresa", "admin_general"])),
    ) -> Any:
        """
        Update a dropdown item with tenant validation and cache invalidation.
        """
        db_item = crud_instance.get(db=db, id=item_id)
        if not db_item or getattr(db_item, "inquilino_id", current_user.inquilino_id) != current_user.inquilino_id:
            raise HTTPException(status_code=404, detail="Item not found")
        item = crud_instance.update(db=db, db_obj=db_item, obj_in=item_in)
        cache_service.invalidate_prefix(f"dropdown:{dropdown_type}:tenant:{current_user.inquilino_id}")
        return item

    @router.delete("/{item_id}", response_model=schema)
    def delete_item(
        *,
        db: Session = Depends(deps.get_db),
        item_id: int,
        current_user: user_model.Usuario = Depends(deps.role_required(["admin_empresa", "admin_general"])),
    ) -> Any:
        """
        Delete a dropdown item with tenant validation and cache invalidation.
        """
        db_item = crud_instance.get(db=db, id=item_id)
        if not db_item or getattr(db_item, "inquilino_id", current_user.inquilino_id) != current_user.inquilino_id:
            raise HTTPException(status_code=404, detail="Item not found")

        item = crud_instance.remove(db=db, id=item_id)
        cache_service.invalidate_prefix(f"dropdown:{dropdown_type}:tenant:{current_user.inquilino_id}")
        return item

    return router

# Create a main router to aggregate all dropdown routers
router = APIRouter()

# Instantiate a sub-router for each dropdown type
for name, crud_obj in crud_dropdowns.items():
    dropdown_specific_router = create_dropdown_router(
        crud_instance=crud_obj,
        schema=schemas.Dropdown,
        create_schema=schemas.DropdownCreate,
        update_schema=schemas.DropdownUpdate,
        dropdown_type=name
    )
    # Use the name of the dropdown as the prefix for its endpoints
    router.include_router(
        dropdown_specific_router,
        prefix=f"/{name}",
        tags=[f"Dropdown Management: {name.replace('_', ' ').capitalize()}"]
    )
