"""Database-level protection for live sale-owned space claims, including bulk CRUD."""
from sqlalchemy import inspect,text
from .crm import CRMError

def install(connection):
    if not {'reservas','sga_sale_space_claim'}<=set(inspect(connection).get_table_names()):return False
    if connection.dialect.name=='sqlite':
        connection.execute(text("CREATE TRIGGER IF NOT EXISTS sga_sale_space_delete_guard BEFORE DELETE ON reservas WHEN EXISTS(SELECT 1 FROM sga_sale_space_claim WHERE reservation_id=OLD.id AND released=0) BEGIN SELECT RAISE(ABORT,'SALE_SPACE_CLAIM_ACTIVE'); END"))
        connection.execute(text("CREATE TRIGGER IF NOT EXISTS sga_sale_space_update_guard BEFORE UPDATE OF id,inquilino_id,escenario_parte_id,usuario_id_reserva,fecha_inicio,fecha_fin ON reservas WHEN EXISTS(SELECT 1 FROM sga_sale_space_claim WHERE reservation_id=OLD.id AND released=0) AND (NEW.id IS NOT OLD.id OR NEW.inquilino_id IS NOT OLD.inquilino_id OR NEW.escenario_parte_id IS NOT OLD.escenario_parte_id OR NEW.usuario_id_reserva IS NOT OLD.usuario_id_reserva OR NEW.fecha_inicio IS NOT OLD.fecha_inicio OR NEW.fecha_fin IS NOT OLD.fecha_fin) BEGIN SELECT RAISE(ABORT,'SALE_SPACE_CLAIM_ACTIVE'); END"))
    elif connection.dialect.name=='postgresql':
        connection.execute(text("""CREATE OR REPLACE FUNCTION sga_sale_space_guard() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN
        IF EXISTS(SELECT 1 FROM sga_sale_space_claim WHERE reservation_id=OLD.id AND released=false) THEN
        IF TG_OP='DELETE' THEN RAISE EXCEPTION 'SALE_SPACE_CLAIM_ACTIVE'; END IF;
        IF (NEW.id,NEW.inquilino_id,NEW.escenario_parte_id,NEW.usuario_id_reserva,NEW.fecha_inicio,NEW.fecha_fin) IS DISTINCT FROM (OLD.id,OLD.inquilino_id,OLD.escenario_parte_id,OLD.usuario_id_reserva,OLD.fecha_inicio,OLD.fecha_fin) THEN RAISE EXCEPTION 'SALE_SPACE_CLAIM_ACTIVE'; END IF;
        END IF; IF TG_OP='DELETE' THEN RETURN OLD; END IF; RETURN NEW; END $$"""))
        connection.execute(text("""DO $$ BEGIN IF NOT EXISTS(SELECT 1 FROM pg_trigger WHERE tgname='sga_sale_space_delete_guard' AND tgrelid='reservas'::regclass) THEN CREATE TRIGGER sga_sale_space_delete_guard BEFORE DELETE ON reservas FOR EACH ROW EXECUTE FUNCTION sga_sale_space_guard(); END IF; IF NOT EXISTS(SELECT 1 FROM pg_trigger WHERE tgname='sga_sale_space_update_guard' AND tgrelid='reservas'::regclass) THEN CREATE TRIGGER sga_sale_space_update_guard BEFORE UPDATE ON reservas FOR EACH ROW EXECUTE FUNCTION sga_sale_space_guard(); END IF; END $$"""))
    else:raise CRMError('SALE_SPACE_GUARD_DIALECT_REQUIRED',503)
    return True

def require(db):
    if db.bind.dialect.name=='sqlite':count=db.execute(text("SELECT count(*) FROM sqlite_master WHERE type='trigger' AND name IN ('sga_sale_space_delete_guard','sga_sale_space_update_guard')")).scalar()
    elif db.bind.dialect.name=='postgresql':count=db.execute(text("SELECT count(*) FROM pg_trigger WHERE tgname IN ('sga_sale_space_delete_guard','sga_sale_space_update_guard') AND tgrelid='reservas'::regclass AND NOT tgisinternal")).scalar()
    else:count=0
    if count!=2:raise CRMError('SALE_SPACE_GUARDS_INSTALL_REQUIRED',503)
