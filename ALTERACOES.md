# Alterações realizadas

## Arquivos criados

### `database.py`
Dois dicts no nível de módulo: `users` e `sessions`. Sem classes ou funções — controllers acessam diretamente. Mantém o estado em memória enquanto o processo está rodando, conforme o requisito.

### `auth.py`
Funções de criptografia isoladas do resto da aplicação:
- `generate_salt()`: `os.urandom(16).hex()` → 32 chars hex (exigido pelos testes: `/^[a-f0-9]{32}$/i`)
- `hash_password()`: `pbkdf2_hmac('sha512', ...)` com 260.000 iterações
- `verify_password()`: usa `hmac.compare_digest` para evitar timing attacks (requisito de segurança)

### `sessions.py`
Gerencia o ciclo de vida das sessões:
- `create_session()`: gera UUID v4, salva `{email, created_at, views: 0}` em `database.sessions`
- `get_session()`: verifica expiração de 30 min de forma lazy (sem thread) e remove se expirada
- `delete_session()`: remove do dict (logout)
- `get_session_id_from_environ()`: parse manual do header `HTTP_COOKIE` — evita `http.cookies.SimpleCookie` que pode falhar em valores UUID
- `get_authenticated_email()`: combina as duas funções acima

### `templates/base.html`
Layout base com CSS inline minimalista. Nav condicional: anônimo vê "Criar conta" e "Fazer login"; autenticado vê "Dashboard", "Admin" e "Logout". O texto "Encerrar sessão" está ausente do nav para não conflitar com o teste `assertHtmlExcludes(html, "Encerrar sessão")` na home anônima.

### `templates/home.html`
Conteúdo condicional: anônimo vê mensagem de boas-vindas pública; autenticado vê email. Textos exatos exigidos pelos testes E2E.

### `templates/register.html`
Formulário com `action` antes de `method` no `<form>` (a regex de `assertForm` exige essa ordem). Input `password` com `minlength="8"` conforme requisito.

### `templates/register_success.html`
Resposta 200 do `POST /register`. Textos e link exatos exigidos por `cadastro.e2e.test.js`.

### `templates/register_conflict.html`
Resposta 409 para email duplicado. Dois links: "Tentar novamente" e "Ir para login".

### `templates/login.html`
Formulário de login. Ambos os inputs têm `required` (sem `minlength` — o teste não exige para login).

### `templates/login_error.html`
Resposta 401 de credenciais inválidas. Textos exatos exigidos por `autenticacao.e2e.test.js`.

### `templates/dashboard.html`
Área protegida. Contém "Bem-vindo", o email do usuário e o link `<a href="/logout">Encerrar sessão</a>` no corpo da página (separado do "Logout" do nav).

### `templates/admin.html`
Duas tabelas com estrutura de `<tr>/<td>/<code>` exata, pois os testes usam regex para extrair dados das linhas. `hash_preview` é os primeiros 32 chars do digest hex. `created_at` em `DD/MM/YYYY`.

### `templates/unauthorized.html`
Página 401 compartilhada entre dashboard, admin e logout quando sem sessão válida.

### `templates/logout.html`
Resposta 200 do `GET /logout`. O cookie expirado é enviado via header, não via template.

### `templates/not_found.html`
Página 404 para rotas não mapeadas.

---

## Arquivos modificados

### `controllers.py`
Reescrito completamente. Principais decisões:
- `_jinja_env` no nível de módulo com `FileSystemLoader` apontando para `templates/` via caminho absoluto (robusto independente do diretório de trabalho)
- `_HTML` como constante para evitar repetição dos headers de Content-Type
- `_read_post_body()`: usa `int(environ.get("CONTENT_LENGTH") or 0)` para tratar `CONTENT_LENGTH` vazio ou ausente
- Controllers protegidos delegam para `unauthorized_page` quando `get_authenticated_email` retorna `None`

### `rotas.py`
Substituído dict `{path: handler}` por `{(método, path): handler}`. Permite distinguir `GET /register` de `POST /register` sem lógica adicional no dispatcher.

### `main.py`
- Porta alterada de `3333` para `8080` (os testes usam `http://localhost:8080`)
- Dispatcher atualizado para extrair `REQUEST_METHOD` e `PATH_INFO` e montar a chave `(método, path)`

---

## Decisão: `GET /logout` em vez de `POST /logout`

O `Requisitos.md` especifica `POST /logout`, mas todos os testes E2E chamam `/logout` sem especificar método (fetch default = GET). Os links HTML também são `<a href="/logout">`, que são GET. A implementação segue os testes.

---

## Como rodar

```sh
pip install jinja2
python main.py
# em outro terminal:
cd requisitos && npm install && npm run test:e2e
```
