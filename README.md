# Patas Amigas — MVP web

Aplicação web inicial para cadastro de tutores, pets, veterinários e serviços, além de criação/consulta de agendamentos com verificação de conflito de horário.

## Funcionalidades
- Painel inicial com totais e próximos agendamentos.
- Cadastro e busca de tutores.
- Cadastro e busca de pets vinculados a tutores.
- Cadastro e busca de veterinários.
- Cadastro de serviços com valor e duração.
- Criação e consulta de agendamentos.
- Verificação de conflito de horário do veterinário considerando a duração do serviço.
- Alteração de status para Agendado, Concluído ou Cancelado.
- Layout responsivo para desktop e celular.

## Requisitos
Python 3.10 ou superior (recomendado Python 3.12).

## Executar localmente no Windows
1. Extraia o ZIP.
2. Abra a pasta `patas_amigas_mvp` no Explorador de Arquivos.
3. Na barra de endereço da pasta, digite `cmd` e pressione Enter.
4. Execute:
   ```bat
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
   ```
5. Abra `http://127.0.0.1:5000` no navegador.

Por padrão, o aplicativo usa SQLite e cria `patas_amigas.db` automaticamente, então pode ser testado sem configurar o MySQL primeiro.

## Usar MySQL
1. No MySQL Workbench, crie o banco `patas_amigas` (se ainda não existir):
   ```sql
   CREATE DATABASE patas_amigas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
2. Crie e ative o ambiente virtual e instale os requisitos como acima.
3. Configure a variável `DATABASE_URL` antes de iniciar o app. Exemplo no Prompt de Comando:
   ```bat
   set DATABASE_URL=mysql+pymysql://usuario:senha@localhost/patas_amigas?charset=utf8mb4
   python app.py
   ```
   Substitua `usuario` e `senha` pelos dados locais do seu MySQL. Não publique senhas no GitHub.
4. O aplicativo cria suas próprias tabelas ao iniciar. Ele não importa automaticamente dados das tabelas SQL antigas do projeto; será necessário adaptar/importar os dados se quiser reaproveitá-los.

## Publicar no GitHub
Envie os arquivos do projeto para o repositório `projeto-patas-amigas`. Não envie `.env`, senhas, tokens nem o arquivo de banco local `.db`.

## Limitações importantes
- Esta é uma primeira versão acadêmica para desenvolvimento e demonstração, não um sistema pronto para uso real em clínica.
- Ainda não há login/autenticação, permissões por usuário, recuperação de senha, auditoria ou proteção completa para produção.
- Teste os fluxos e valide os dados antes de apresentar como funcionalidade concluída.
- O app tem um modelo de dados próprio. As tabelas antigas podem ter nomes/campos diferentes; confira antes de migrar dados.
