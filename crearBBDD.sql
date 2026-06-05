-- ============================================
-- BASE DE DATOS: faces
-- ============================================

-- Ejecutar conectado a otra DB (ej: postgres)
DROP DATABASE IF EXISTS faces;
CREATE DATABASE faces;

-- Extensión obligatoria para el tipo vector
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- TABLA: usuarios
-- ============================================

CREATE TABLE usuarios (
    id            SERIAL PRIMARY KEY,
    code_usuario  VARCHAR(50) UNIQUE,
    vector_128    vector(128),
    password      TEXT
);

-- Índice para búsqueda por similitud facial
CREATE INDEX idx_usuarios_vector
    ON usuarios
    USING hnsw (vector_128 vector_cosine_ops);

-- ============================================
-- TABLA: videos
-- ============================================

CREATE TABLE videos (
    id          SERIAL PRIMARY KEY,
    fecha_video TIMESTAMP,
    ruta_video  TEXT,
    code_usuario VARCHAR(50) REFERENCES usuarios(code_usuario)
);