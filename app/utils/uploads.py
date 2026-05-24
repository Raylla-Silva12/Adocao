"""
Utilitários para uploads de arquivos.
Suporta upload local e Google Cloud Storage.
"""
import os
import uuid
from pathlib import Path
from werkzeug.utils import secure_filename
from app.config import Config

# Extensões de arquivo permitidas
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}


def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_unique_filename(filename):
    """Gera um nome único para o arquivo."""
    ext = filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4()}.{ext}"
    return unique_name


def upload_file_local(file):
    """
    Faz upload do arquivo para o sistema de arquivos local.
    Retorna o caminho relativo do arquivo.
    """
    if not file or not allowed_file(file.filename):
        raise ValueError("Arquivo inválido")
    
    upload_folder = Config.UPLOAD_FOLDER
    os.makedirs(upload_folder, exist_ok=True)
    
    filename = secure_filename(file.filename)
    unique_filename = get_unique_filename(filename)
    
    filepath = os.path.join(upload_folder, unique_filename)
    file.save(filepath)
    
    return f"/uploads/{unique_filename}"


def upload_file_gcs(file):
    """
    Faz upload do arquivo para Google Cloud Storage.
    Retorna a URL pública do arquivo.
    """
    try:
        from google.cloud import storage
    except ImportError:
        raise ImportError("google-cloud-storage não está instalado")
    
    if not file or not allowed_file(file.filename):
        raise ValueError("Arquivo inválido")
    
    bucket_name = Config.GCS_BUCKET
    if not bucket_name:
        raise ValueError("GCS_BUCKET não configurado")
    
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    filename = secure_filename(file.filename)
    unique_filename = get_unique_filename(filename)
    blob = bucket.blob(f"pets/{unique_filename}")
    
    blob.upload_from_string(
        file.read(),
        content_type=file.content_type
    )
    
    return blob.public_url


def upload_file(file, use_gcs=False):
    """
    Faz upload do arquivo.
    Se use_gcs=True, usa Google Cloud Storage; caso contrário, usa sistema local.
    """
    if use_gcs and Config.GCS_BUCKET:
        return upload_file_gcs(file)
    return upload_file_local(file)


def delete_file_local(filepath):
    """Deleta um arquivo local."""
    try:
        if filepath.startswith("/uploads/"):
            filepath = filepath[9:]  # Remove /uploads/
        full_path = os.path.join(Config.UPLOAD_FOLDER, filepath)
        if os.path.exists(full_path):
            os.remove(full_path)
    except Exception as e:
        print(f"Erro ao deletar arquivo: {e}")


def delete_file_gcs(file_url):
    """Deleta um arquivo do Google Cloud Storage."""
    try:
        from google.cloud import storage
    except ImportError:
        return
    
    try:
        client = storage.Client()
        bucket = client.bucket(Config.GCS_BUCKET)
        
        # Extrai o nome do blob da URL
        if "pets/" in file_url:
            blob_name = file_url.split("pets/")[1]
            blob = bucket.blob(f"pets/{blob_name}")
            blob.delete()
    except Exception as e:
        print(f"Erro ao deletar arquivo GCS: {e}")


def delete_file(file_url):
    """Deleta um arquivo."""
    if file_url.startswith("http"):
        delete_file_gcs(file_url)
    else:
        delete_file_local(file_url)
