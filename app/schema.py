"""
Migrações incrementais leves (sem Alembic).
Garante compatibilidade com bancos criados antes de novas colunas.
"""
import logging
from sqlalchemy import inspect, text

from app.extensions import db

logger = logging.getLogger(__name__)


def upgrade_schema():
    """Aplica alterações de schema em bancos já existentes."""
    inspector = inspect(db.engine)
    tables = set(inspector.get_table_names())

    if "pets" in tables:
        columns = {col["name"] for col in inspector.get_columns("pets")}
        if "owner_contact" not in columns:
            db.session.execute(text(
                "ALTER TABLE pets ADD COLUMN owner_contact VARCHAR(50)"
            ))
            db.session.commit()
            logger.info("Schema: coluna pets.owner_contact adicionada")
