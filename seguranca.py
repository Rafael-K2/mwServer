import hashlib
import os
import secrets
import string
from pathlib import Path


def _resolver_dados_dir(dados_dir=None):
    if dados_dir:
        path = Path(dados_dir)
    else:
        path = Path(__file__).resolve().parent / "dados"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _gerar_senha(tamanho=24):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(tamanho))


def _hash_senha(senha: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, 200_000)
    return f"pbkdf2_sha256$${salt.hex()}$${digest.hex()}"


def _verificar_hash_senha(senha: str, valor_armazenado: str) -> bool:
    if not valor_armazenado.startswith("pbkdf2_sha256$$"):
        return False
    _, salt_hex, digest_hex = valor_armazenado.split("$$")
    salt = bytes.fromhex(salt_hex)
    digest = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, 200_000)
    return digest.hex() == digest_hex


def _salvar_hash_senha(arquivo: Path, senha: str) -> None:
    arquivo.write_text(_hash_senha(senha), encoding="utf-8")


def obter_senha_ou_gerar(nome_var, nome_perfil, dados_dir=None, senha_padrao=None):
    """Retorna a senha real para uso do sistema e salva apenas um hash no arquivo."""
    valor_env = os.getenv(nome_var)
    if valor_env:
        return valor_env

    dados_path = _resolver_dados_dir(dados_dir)
    arquivo = dados_path / f"senha_{nome_perfil}.txt"

    if arquivo.exists():
        valor = arquivo.read_text(encoding="utf-8").strip()
        if valor.startswith("pbkdf2_sha256$$"):
            if senha_padrao:
                return senha_padrao
            return None
        senha = valor
        _salvar_hash_senha(arquivo, senha)
        return senha

    for nome_compat in (f"{nome_var.lower()}.txt", f"{nome_perfil}_senha.txt"):
        compat_path = dados_path / nome_compat
        if compat_path.exists():
            valor = compat_path.read_text(encoding="utf-8").strip()
            if valor.startswith("pbkdf2_sha256$$"):
                if senha_padrao:
                    return senha_padrao
                return None
            senha = valor
            _salvar_hash_senha(arquivo, senha)
            return senha

    senha = senha_padrao or _gerar_senha()
    _salvar_hash_senha(arquivo, senha)
    return senha