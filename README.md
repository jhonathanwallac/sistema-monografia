# Trabalho de Sistemas Distribuídos - PARTE 1
Sistema web distribuído para o Departamento de Computação gerenciar o cadastro de Monografias do Curso de Sistemas de Informação.

---
Abaixo o passo a passo para configurar o banco de dados PostgreSQL em um ambiente Linux, necessário para o funcionamento do sistema.  
Lembre-se de primeiro alterar o arquivo ".env.example" para ".env" e dentro dele colocar as variáveis de ambiente necessárias para setar as configurações de banco, etc.
---

### Instalar o PostgreSQL

Atualize os pacotes e instale o PostgreSQL:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

---

### Acessar o PostgreSQL

Acesse o terminal como o usuário `postgres`:

```bash
sudo -u postgres psql
```

---

### Criar o Banco de Dados

Execute o comando abaixo para criar o banco de dados (deve ser o mesmo nome definido no arquivo `.env`):

```sql
CREATE DATABASE db_sistema_monografia;
```

---

### Criar o Usuário do Banco

Crie o usuário `admin` com a senha `admin1234`:

```sql
CREATE USER admin WITH PASSWORD 'admin1234';
```

---

### Conceder Permissões

Dê todas as permissões ao usuário `admin` sobre o banco:

```sql
GRANT ALL PRIVILEGES ON DATABASE db_sistema_monografia TO admin;
```

---

### Configurar Conexões Locais

Edite o arquivo `pg_hba.conf`. Normalmente está localizado em:

```
/etc/postgresql/<versão>/main/pg_hba.conf
```

Adicione ou modifique a seguinte linha:

```
host    all             all             127.0.0.1/32            md5
```

---

### Reiniciar o PostgreSQL

Após salvar as alterações, reinicie o serviço:

```bash
sudo systemctl restart postgresql
```

---

### Testar Conexão

Verifique se o banco está acessível com as credenciais criadas:

```bash
psql -h localhost -p 5432 -U admin -d db_sistema_monografia
```

---

Após esses passos, o banco de dados estará configurado e pronto para ser utilizado no seu projeto Django. Lembre-se de rodar as migrations e após isso poderá subir a aplicação.

---
