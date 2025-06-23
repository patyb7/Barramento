# database/schema.py

import logging
import asyncpg
# Remova imports não utilizados se houver, como typing, datetime, pydantic.BaseModel, Field se não forem usados diretamente aqui

from app.database.manager import DatabaseManager # Importe DatabaseManager

logger = logging.getLogger(_name_)

# 1. Defina o SQL para CRIAR A TABELA
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS validacoes_gerais (
    id SERIAL PRIMARY KEY,
    regra_negocio VARCHAR(255) NOT NULL,
    regra_negocio_descricao TEXT,
    regra_negocio_parametros JSONB,
    usuario_criacao VARCHAR(255),
    usuario_atualizacao VARCHAR(255),
    dado_original VARCHAR(255) NOT NULL,
    dado_normalizado VARCHAR(255) NOT NULL,
    mensagem TEXT,
    origem_validacao VARCHAR(100),
    tipo_validacao VARCHAR(100) NOT NULL,
    is_valid BOOLEAN NOT NULL DEFAULT FALSE,
    data_validacao TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    app_name VARCHAR(100) NOT NULL,
    client_identifier VARCHAR(255),
    regra_negocio_codigo VARCHAR(255),
    regra_negocio_descricao_detalhada TEXT,
    validation_details JSONB DEFAULT '{}',
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
"""

# 2. Defina o SQL para CRIAR ÍNDICES
CREATE_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_validacoes_gerais_tipo_validacao ON validacoes_gerais (tipo_validacao);
CREATE INDEX IF NOT EXISTS idx_validacoes_gerais_app_name ON validacoes_gerais (app_name);
CREATE INDEX IF NOT EXISTS idx_validacoes_gerais_data_validacao DESC ON validacoes_gerais (data_validacao DESC);
CREATE INDEX IF NOT EXISTS idx_validacoes_gerais_dado_original_tipo_app ON validacoes_gerais (dado_original, tipo_validacao, app_name);
CREATE INDEX IF NOT EXISTS idx_validacoes_gerais_dado_normalizado_tipo_app ON validacoes_gerais (dado_normalizado, tipo_validacao, app_name);
"""

# 3. Defina o SQL para CRIAR A FUNÇÃO (se você quiser usar a função de atualização de updated_at)
CREATE_UPDATE_FUNCTION_SQL = """
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

# 4. Defina o SQL para CRIAR O TRIGGER (se você quiser usar o trigger de atualização de updated_at)
CREATE_TRIGGER_SQL = """
DROP TRIGGER IF EXISTS trg_validacoes_gerais_updated_at ON validacoes_gerais;
CREATE TRIGGER trg_validacoes_gerais_updated_at
BEFORE UPDATE ON validacoes_gerais
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
"""


async def initialize_database(db_manager: DatabaseManager):
    conn = None
    try:
        conn = await db_manager.get_connection()
        logger.info("Executando DDL para criar tabela 'validacoes_gerais', indices e triggers se nao existirem...")

        # 1. Executa a criação da tabela
        await conn.execute(CREATE_TABLE_SQL)
        logger.info("Tabela 'validacoes_gerais' verificada/criada.")

        # 2. Executa a criação dos índices
        await conn.execute(CREATE_INDEX_SQL)
        logger.info("Índices para 'validacoes_gerais' verificados/criados.")

        # 3. Executa a criação da função (descomente se quiser usar)
        await conn.execute(CREATE_UPDATE_FUNCTION_SQL)
        logger.info("Função 'update_updated_at_column' verificada/criada.")

        # 4. Executa a criação do trigger (descomente se quiser usar)
        await conn.execute(CREATE_TRIGGER_SQL)
        logger.info("Trigger 'trg_validacoes_gerais_updated_at' verificada/criada.")

        logger.info("Esquema do banco de dados verificado/inicializado com sucesso.")

    except asyncpg.exceptions.PostgresError as e:
        logger.critical(f"Falha CRÍTICA ao inicializar o esquema do banco de dados (asyncpg): {e}", exc_info=True)
        raise # Re-raise a exceção para ser capturada no api_main.py e interromper a aplicação
    except Exception as e:
        logger.critical(f"Erro inesperado durante a inicialização do banco de dados (geral): {e}", exc_info=True)
        raise
    finally:
        if conn:
            await db_manager.put_connection(conn) # Garante que a conexão é retornada ao pool

# ... (qualquer outro código abaixo, como modelos Pydantic ou outras funções)
