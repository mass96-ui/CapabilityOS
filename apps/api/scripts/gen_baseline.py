from __future__ import annotations

import app.models
from sqlalchemy import create_engine, text
from sqlalchemy.schema import CreateTable
from app.database.base import Base

engine = create_engine("sqlite:///:memory:")
for table in Base.metadata.sorted_tables:
    stmt = CreateTable(table).compile(dialect=engine.dialect)
    print(f'op.execute(text("""{stmt}"""))')
    print()
