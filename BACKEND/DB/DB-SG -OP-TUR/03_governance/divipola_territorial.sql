-- ==============================================================================
-- db/03_governance/divipola_territorial.sql
-- Integración Territorial Oficial DANE (DIVIPOLA) en Base de Datos Central
-- ==============================================================================

CREATE TABLE IF NOT EXISTS governance.divipola_colombia (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cod_dpto VARCHAR(5) NOT NULL,
    nom_dpto VARCHAR(100) NOT NULL,
    cod_mpio VARCHAR(10) NOT NULL UNIQUE,
    nom_mpio VARCHAR(150) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_divipola_mpio ON governance.divipola_colombia (cod_mpio);
CREATE INDEX IF NOT EXISTS idx_divipola_dpto ON governance.divipola_colombia (cod_dpto);
