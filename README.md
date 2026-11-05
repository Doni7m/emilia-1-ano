# Emília faz 1 aninho — convite online com senha

Site estático para o GitHub Pages. O convite fica **criptografado** dentro do `index.html`:
quem abre o link vê só o envelope e precisa digitar a **data de nascimento da Emília (DD/MM/AAAA)**.
Sem a data, ninguém vê fotos, endereço ou telefone, nem olhando o código-fonte.

## Como está organizado

```
emilia-1-ano/
├── index.html        ← GERADO pelo build.py. É o único arquivo do convite que vai pro GitHub.
├── assets/
│   ├── og.jpg        ← imagem da prévia no WhatsApp (pública)
│   └── favicon.png   ← ícone da aba (óculos, sem foto)
├── build.py          ← junta tudo e criptografa
├── .gitignore        ← impede a pasta fonte/ de ir para o GitHub
└── fonte/            ← FICA SÓ NO SEU COMPUTADOR
    ├── config.js     ← data, hora, local, WhatsApp, tamanhos… (edite aqui)
    ├── senha.txt     ← a senha (não vai para o GitHub)
    ├── convite.html  ← o conteúdo do convite
    ├── casca.html    ← o envelope com o campo de senha
    ├── style.css, app.js, carregador.js
    └── fotos/
```

## 1. Preencher os dados

Edite **`fonte/config.js`**: `dataHora`, `local`, `confirmarAte`, `whatsapp` (só dígitos com código do país, ex.: `351912345678`), `listaPresentesUrl` (opcional) e `tamanhos`.

## 2. Gerar o index.html

```bash
pip install cryptography     # só na primeira vez
python3 build.py
```

Sempre que mudar algo em `fonte/`, rode `python3 build.py` de novo e faça commit do `index.html`.

## 3. Publicar no GitHub Pages

```bash
git init
git add .
git status                  # confira: NÃO pode aparecer nada de fonte/
git commit -m "Convite Emília 1 aninho"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/emilia-1-ano.git
git push -u origin main
```

No GitHub: **Settings → Pages → Source: Deploy from a branch → `main` / `(root)` → Save**.
O site fica em `https://SEU-USUARIO.github.io/emilia-1-ano/`.

> Se for subir pelo site do GitHub (arrastando arquivos), envie só `index.html`, a pasta `assets/` e o `README.md`. Nunca a pasta `fonte/`.

## 4. Prévia do WhatsApp

Em `fonte/casca.html`, na linha `og:image`, troque `SEU-USUARIO` pelo seu usuário, rode `python3 build.py` e faça push.

## Como funciona a senha

- A data vira uma chave (PBKDF2-SHA256, 310 mil iterações) que decifra o convite (AES-256-GCM) no próprio celular do convidado.
- Aceita a data com barras, traços, pontos ou só números (ex.: `05/03/2024`, `05-03-2024`, `05.03.24`, `05032024`).
- Depois de abrir uma vez, o aparelho lembra e entra direto.
- Para trocar a senha: edite `fonte/senha.txt` e rode `python3 build.py`.

**Limite honesto:** uma data de nascimento é uma senha fraca. Ela barra curiosos, gente que recebeu o link repassado e robôs. Não segura alguém determinado que saiba que a senha é uma data e se dê ao trabalho de testar milhares delas. Para um convite de aniversário isso é proteção suficiente. A imagem `assets/og.jpg` (prévia do WhatsApp) é pública e mostra a foto da Emília com chapeuzinho; se preferir, troque por uma sem foto.

## Testar no computador

```bash
python3 -m http.server 8000     # abra http://localhost:8000
```
Para ver o envelope de novo depois de abrir: abra numa aba anônima.

## Respostas também por e-mail (opcional)

Crie um formulário grátis em <https://formspree.io>, cole o código (o que vem depois de `/f/`) em `formspreeId` no `fonte/config.js` e rode o build.
