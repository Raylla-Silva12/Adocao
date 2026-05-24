"""
Script para gerenciar o banco de dados.
"""
import os
import click
from sqlalchemy import text
from app import create_app
from app.extensions import db
from app.models import Admin, Pet
from app.auth import register_admin


app = create_app()


@click.group()
def cli():
    """Gerenciador de banco de dados."""
    pass


@cli.command()
def init_db():
    """Inicializa o banco de dados."""
    with app.app_context():
        db.create_all()
        click.echo("✓ Banco de dados inicializado!")


@cli.command()
def drop_db():
    """Remove todas as tabelas."""
    if click.confirm("Tem certeza que deseja deletar todas as tabelas?"):
        with app.app_context():
            db.drop_all()
            click.echo("✓ Banco de dados limpo!")


@cli.command()
def seed_admin():
    """Cria um admin padrão."""
    with app.app_context():
        email = click.prompt("Email do admin")
        password = click.prompt("Senha", hide_input=True, confirmation_prompt=True)
        
        try:
            admin = register_admin(email, password)
            click.echo(f"✓ Admin criado: {admin.email}")
        except ValueError as e:
            click.echo(f"✗ Erro: {e}")


@cli.command()
def upgrade():
    """Aplica alterações incrementais no schema (colunas novas)."""
    with app.app_context():
        db.session.execute(text(
            "ALTER TABLE pets ADD COLUMN IF NOT EXISTS owner_contact VARCHAR(50)"
        ))
        db.session.commit()
        click.echo("✓ Schema atualizado (owner_contact em pets).")


@cli.command()
def reset_db():
    """Reseta o banco de dados (drop + create + seed)."""
    if click.confirm("Tem certeza que deseja resetar o banco de dados?"):
        with app.app_context():
            db.drop_all()
            click.echo("✓ Banco de dados limpo!")
            
            db.create_all()
            click.echo("✓ Banco de dados recriado!")
            
            email = os.getenv("ADMIN_EMAIL", "admin@example.com")
            password = os.getenv("ADMIN_PASSWORD", "admin123")
            
            try:
                admin = register_admin(email, password)
                click.echo(f"✓ Admin criado: {admin.email}")
            except ValueError as e:
                click.echo(f"✗ Erro ao criar admin: {e}")


if __name__ == "__main__":
    cli()
