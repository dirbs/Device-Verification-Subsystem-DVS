__all__ = ["request", "summary"]

from ..models import *
from flask_sqlalchemy import declarative_base

# avoid circular imports, define both dependent tables in one go
Base = declarative_base(class_registry={"status": request.Request})