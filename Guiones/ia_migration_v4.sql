-- Esquema SQL v4 - Nora de Nexora (Socia Contable y Secretaria Odontológica)

-- 1. TABLA ia_entidades
CREATE TABLE IF NOT EXISTS ia_entidades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cuit TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    tipo TEXT CHECK (tipo IN ('paciente', 'proveedor')),
    saldo NUMERIC(15, 2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 2. TABLA ia_turnos
CREATE TABLE IF NOT EXISTS ia_turnos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id UUID REFERENCES ia_entidades(id) ON DELETE CASCADE,
    fecha TIMESTAMP WITH TIME ZONE NOT NULL,
    tratamiento TEXT,
    estado TEXT DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'completado')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 3. TABLA ia_dispositivos
CREATE TABLE IF NOT EXISTS ia_dispositivos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre TEXT NOT NULL,
    tipo TEXT CHECK (tipo IN ('luz', 'aire', 'camara')),
    estado_ip TEXT,
    red_local_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Actualización de tablas existentes (ia_clientes, ia_documentos, ia_mensajes) se asume realizada en v1-v3.
