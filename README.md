# Última Xícara — Atividade 4 (Flask + MySQL com Docker)

Site da cafeteria em Flask, agora com banco MySQL: o formulário da página
de contato (`/contato`) grava as mensagens no banco e a página `/listar`
mostra o que foi salvo. A aplicação e o banco rodam em
containers Docker, e as credenciais ficam só no arquivo `.env`
(carregado com `python-dotenv`), nunca no código.

## Estrutura

```
├── app.py                  → app Flask, conexão com o banco e rotas
├── Dockerfile              → imagem do Flask
├── docker-compose.yml      → sobe o Flask (web) e o MySQL (db)
├── db/init.sql             → cria a tabela `mensagens` na 1ª execução
├── requirements.txt        → Flask, python-dotenv, mysql-connector-python
├── .env.example            → nomes das variáveis (sem valores)
├── .env                    → valores reais (NÃO versionado, só na EC2)
├── .gitignore / .dockerignore
├── templates/              → base, index, cardapio, sobre-nos, contatos, listar
└── static/                 → css e imagens
```

## Variáveis do `.env`

| Variável | O que é | Valor no Docker |
|---|---|---|
| `DB_HOST` | endereço do MySQL | `db` (nome do serviço) |
| `DB_PORT` | porta do MySQL | `3306` |
| `DB_USER` | usuário da aplicação (não é o root) | ex.: `appuser` |
| `DB_PASSWORD` | senha desse usuário | escolha uma senha forte |
| `DB_NAME` | banco da aplicação | ex.: `atividade4` |
| `DB_ROOT_PASSWORD` | senha do root (só o container do MySQL usa) | escolha outra senha forte |
| `DB_BIND` | em qual interface a porta 3306 do host é publicada | `127.0.0.1` (padrão) |
| `SECRET_KEY` | chave das mensagens flash do Flask | frase longa e aleatória |

Dica: nas senhas, evite `$`, `#`, aspas e espaços.

## Passo a passo na EC2 (uma instância com Docker)

**1. Security Group:** libere somente `22/tcp` (SSH) e `5000/tcp` (Flask).
**Não** libere a 3306.

**2. Pare o app da Atividade 3** (ele usa a porta 5000):
```bash
pkill -f app.py
sudo systemctl disable --now flask-app   # só se você tiver criado esse serviço
```

**3. Instale o Docker:**
```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2 git
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```
Saia do SSH e entre de novo (para o grupo `docker` valer). Se o pacote
`docker-compose-v2` não existir na sua versão do Ubuntu, use:
`curl -fsSL https://get.docker.com | sudo sh`

**4. Baixe o projeto e crie o `.env`:**
```bash
git clone https://github.com/SEU_USUARIO/SEU_REPO.git
cd SEU_REPO            # pasta onde está o docker-compose.yml
cp .env.example .env
nano .env              # preencha com os valores da tabela acima
```

**5. Suba tudo:**
```bash
docker compose up -d --build
docker compose ps                # web e db devem estar "running"/"healthy"
docker compose logs -f web       # Ctrl+C para sair dos logs
```
Os containers têm `restart: unless-stopped`: continuam no ar depois que
você fecha o SSH e voltam sozinhos se a instância reiniciar.

**6. Teste no navegador:** `http://IP_PUBLICO:5000/contato`. Envie
pelo menos 5 mensagens e confira em `http://IP_PUBLICO:5000/listar`.

**7. Print do SELECT no banco:**
```bash
docker compose exec db sh -c 'mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" -e "SELECT * FROM mensagens;"'
```

**8. Provar que a 3306 não está exposta** (no seu computador):
- Windows: `Test-NetConnection IP_PUBLICO -Port 3306` (deve falhar)
- Mac/Linux: `nc -vz -w 5 IP_PUBLICO 3306` (deve dar timeout)

## Comandos úteis

```bash
git pull && docker compose up -d --build   # aplicar mudanças do GitHub
docker compose restart web                 # reiniciar só o Flask
docker compose down                        # parar (os dados do banco ficam)
docker compose down -v                     # parar E apagar o banco (recomeçar do zero)
```
O `db/init.sql` só roda na primeira vez que o volume do banco é criado. Se
mudar a tabela, apague o banco com `down -v` e suba de novo.

## Variante: duas instâncias EC2 (se o professor exigir)

O mesmo projeto serve. Crie `app-seunome` e `db-seunome` na mesma VPC e com a
mesma chave. Security Groups: App com `22` e `5000` (qualquer origem); DB com
`22` e `3306` **somente a partir do Security Group da App**.

Na instância **DB** (instale Docker, clone o repositório e crie o `.env`
com `DB_BIND=0.0.0.0` e as senhas):
```bash
docker compose up -d db
```

Na instância **App** (`.env` com `DB_HOST=IP_PRIVADO_DA_DB`):
```bash
docker compose up -d --build --no-deps web
```

Para restringir o usuário ao IP privado da App, na instância DB:
```bash
docker compose exec db sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "RENAME USER '"'"'$MYSQL_USER'"'"'@'"'"'%'"'"' TO '"'"'$MYSQL_USER'"'"'@'"'"'IP_PRIVADO_DA_APP'"'"';"'
```

## Checklist de entrega

- [ ] Link da aplicação: `http://IP_PUBLICO:5000`
- [ ] Link da listagem: `http://IP_PUBLICO:5000/listar`
- [ ] Link do repositório no GitHub (com `.env.example`, sem `.env`)
- [ ] Print do terminal com o resultado do SELECT
- [ ] Print das regras de entrada do Security Group
