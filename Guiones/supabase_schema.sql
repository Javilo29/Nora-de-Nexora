-- Esquema SQL para Supabase (AGENTE IA) con Protocolo de Aislamiento

-- Tabla de Clientes
CREATE TABLE IF NOT EXISTS ia_clientes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre TEXT NOT NULL,
    cuit TEXT UNIQUE NOT NULL,
    telefono TEXT,
    perfil_educativo BOOLEAN DEFAULT false, -- Nuevo campo
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Tabla de Documentos
CREATE TABLE IF NOT EXISTS ia_documentos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cliente_id UUID REFERENCES ia_clientes(id) ON DELETE CASCADE,
    url_storage TEXT, -- Enlace al archivo en Supabase Storage (Bucket ia_files)
    tipo TEXT CHECK (tipo IN ('factura', 'estado_contable')),
    total NUMERIC(15, 2),
    estado TEXT DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'procesado')),
    received_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Tabla de Mensajes (Feedback Inteligente)
CREATE TABLE IF NOT EXISTS ia_mensajes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cliente_id UUID REFERENCES ia_clientes(id) ON DELETE CASCADE,
    contenido TEXT NOT NULL,
    direccion TEXT CHECK (direccion IN ('entrante', 'saliente')),
    canal TEXT CHECK (canal IN ('whatsapp', 'email')),
    marca_educativa BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Habilitar Row Level Security (RLS) si es necesario
-- ALTER TABLE clientes ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE documentos ENABLE ROW LEVEL SECURITY;
