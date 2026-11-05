"""Monta o index.html público a partir da pasta fonte/.

O convite (fotos, endereço, WhatsApp, textos) vai CRIPTOGRAFADO dentro da página.
Só a data de nascimento da Emília abre. A pasta fonte/ NÃO vai para o GitHub.

Uso:
    pip install cryptography        (uma vez)
    python3 build.py                (gera index.html)
    python3 build.py --previa X     (gera também um arquivo único de prévia em X)
"""
import argparse, base64, json, mimetypes, os, pathlib, re

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import hashlib

RAIZ = pathlib.Path(__file__).parent
FONTE = RAIZ / "fonte"
ITERACOES = 310_000


def data_uri(caminho: pathlib.Path) -> str:
    mime = "image/webp" if caminho.suffix == ".webp" else (mimetypes.guess_type(caminho.name)[0] or "application/octet-stream")
    return f"data:{mime};base64," + base64.b64encode(caminho.read_bytes()).decode()


def normaliza(senha: str) -> str:
    """Mesma regra do navegador: só dígitos, ano com 4 casas -> '05032024'."""
    d = re.sub(r"\D", "", senha)
    if len(d) == 6:
        d = d[:4] + "20" + d[4:]
    if len(d) != 8:
        raise SystemExit(f"Senha inválida em fonte/senha.txt: use DD/MM/AAAA (recebi {senha!r})")
    return d


def cifra(texto: str, senha: str) -> str:
    sal, iv = os.urandom(16), os.urandom(12)
    chave = hashlib.pbkdf2_hmac("sha256", senha.encode(), sal, ITERACOES, dklen=32)
    dados = AESGCM(chave).encrypt(iv, texto.encode("utf-8"), None)
    return f"v1.{ITERACOES}." + base64.b64encode(sal + iv + dados).decode()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--previa", help="caminho de um HTML único para prévia (sem doctype/head)")
    args = ap.parse_args()

    senha = normaliza((FONTE / "senha.txt").read_text(encoding="utf-8").strip())

    # parte secreta: o convite com as fotos embutidas + configuração + lógica
    html = (FONTE / "convite.html").read_text(encoding="utf-8")
    html = re.sub(r'src="(fotos/[^"]+)"', lambda m: f'src="{data_uri(FONTE / m.group(1))}"', html)
    app = (FONTE / "config.js").read_text(encoding="utf-8") + "\n" + (FONTE / "app.js").read_text(encoding="utf-8")
    cofre = cifra(json.dumps({"html": html, "app": app}, ensure_ascii=False), senha)

    # parte pública: envelope + campo de senha
    pagina = (FONTE / "casca.html").read_text(encoding="utf-8")
    pagina = pagina.replace("/*ESTILO*/", (FONTE / "style.css").read_text(encoding="utf-8"))
    pagina = pagina.replace("/*CARREGADOR*/", (FONTE / "carregador.js").read_text(encoding="utf-8"))
    pagina = pagina.replace("/*COFRE*/", cofre)

    destino = RAIZ / "index.html"
    destino.write_text(pagina, encoding="utf-8")
    print(f"index.html gerado ({destino.stat().st_size // 1024} KB) — convite criptografado com a data de nascimento.")

    if args.previa:
        p = pagina
        p = re.sub(r'(href)="(assets/[^"]+)"', lambda m: f'{m.group(1)}="{data_uri(RAIZ / m.group(2))}"', p)
        for tag in ["<!doctype html>", '<html lang="pt">', "</html>", "<head>", "</head>", "</body>"]:
            p = p.replace(tag, "")
        p = p.replace('<body class="travado">', '<script>document.body.classList.add("travado")</script>')
        p = re.sub(r'<meta charset="utf-8">\s*<meta name="viewport"[^>]*>', "", p, count=1)
        pathlib.Path(args.previa).write_text(p.strip() + "\n", encoding="utf-8")
        print("prévia:", args.previa)


if __name__ == "__main__":
    main()
