from sqlalchemy.inspection import inspect

def get_model_fields(model) -> set:
    """Return a set of all field names defined in a SQLAlchemy model (Python-side)."""
    return {attr.key for attr in inspect(model).mapper.column_attrs}
