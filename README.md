# Webdev Cookie

Aplicação web WSGI construída em Python puro, sem frameworks externos. Demonstra autenticação com sessões em memória, hashing seguro de senhas e roteamento customizado.

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Servidor | Python WSGI (stdlib) |
| Roteamento | `Router` customizado (`router.py`) |
| Hashing | PBKDF2 + SHA-512 + salt aleatório |
| Sessões | Dicionário em memória + cookie `sessionId` |

## Features

- **Cadastro** — cria conta com e-mail e senha; senha nunca armazenada em texto puro
- **Login** — valida credenciais com comparação segura contra timing attacks; redireciona para `/dashboard`
- **Sessões** — cookie `sessionId` com flags `HttpOnly`, `SameSite=Strict`; expiram após 30 minutos
- **Logout** — remove sessão da memória e expira o cookie
- **Rotas protegidas** — `/dashboard`, `/admin` e `/logout` retornam 401 para visitantes anônimos
- **Painel admin** — lista usuários (salt + hash truncado) e sessões ativas (ID, e-mail, data, views)
- **Roteamento declarativo** — decoradores `@router.get(path)` / `@router.post(path)`

## Rotas

| Método | Rota | Acesso |
|---|---|---|
| GET | `/` | Público |
| GET | `/register` | Público |
| POST | `/register` | Público |
| GET | `/login` | Público |
| POST | `/login` | Público |
| GET | `/dashboard` | Autenticado |
| GET | `/admin` | Autenticado |
| GET | `/logout` | Autenticado |

## Como rodar

```bash
# Inicia o servidor (passando o host e a porta)
python main.py 0.0.0.0 8080

