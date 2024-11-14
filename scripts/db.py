# scripts/db.py
import typer
from alembic.config import Config
from alembic import command

app = typer.Typer()

@app.command()
def migrate(message: str = None):
    """Create a new migration"""
    alembic_cfg = Config("alembic.ini")
    command.revision(alembic_cfg, message=message, autogenerate=True)

@app.command()
def upgrade():
    """Apply all migrations"""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

@app.command()
def downgrade():
    """Revert last migration"""
    alembic_cfg = Config("alembic.ini")
    command.downgrade(alembic_cfg, "-1")

if __name__ == "__main__":
    app()