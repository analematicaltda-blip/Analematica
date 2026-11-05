-- 90_super_admin/16_testing/super_admin_validation.sql
-- Validation scripts for Super Admin structure

DO $$
BEGIN
    -- Verify that new tables have the mandatory SCTA columns
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'system_modules' AND column_name = 'hash_integridad'
    ) THEN
        RAISE EXCEPTION 'Mandatory SCTA columns missing in system_modules';
    END IF;

    -- Verify Military Hierarchy activation
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'ai_core' AND table_name = 'agent_military_hierarchy'
    ) THEN
        RAISE EXCEPTION 'AI Military Hierarchy table missing';
    END IF;

    RAISE NOTICE 'Super Admin Structural Validation Passed';
END $$;
