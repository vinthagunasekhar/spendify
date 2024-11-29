import typer
from alembic.config import Config
from alembic import command
import os
from dotenv import load_dotenv

load_dotenv()

app = typer.Typer()

@app.command()
def migrate(message: str = None):
    """Create a new migration"""
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), '..', 'alembic.ini'))
    command.revision(alembic_cfg, message=message, autogenerate=True)

@app.command()
def upgrade():
    """Apply all migrations"""
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), '..', 'alembic.ini'))
    command.upgrade(alembic_cfg, "head")

@app.command()
def downgrade():
    """Revert last migration"""
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), '..', 'alembic.ini'))
    command.downgrade(alembic_cfg, "-1")

@app.command()
def stamp(revision: str = "head"):
    """Stamp the revision table with the given revision; don't run any migrations"""
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), '..', 'alembic.ini'))
    command.stamp(alembic_cfg, revision)

if __name__ == "__main__":
    app()