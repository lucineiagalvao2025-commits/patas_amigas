# 🐾 Patas Amigas

## Sobre o projeto

O Patas Amigas é um sistema web desenvolvido como projeto acadêmico do curso de Análise e Desenvolvimento de Sistemas (ADS). Seu objetivo é facilitar o gerenciamento de uma clínica veterinária, organizando cadastros e agendamentos em um único ambiente.

## Funcionalidades

- Cadastro e consulta de tutores.
- Cadastro e consulta de animais de estimação.
- Cadastro e consulta de veterinários.
- Cadastro e consulta de serviços veterinários.
- Criação e consulta de agendamentos.
- Atualização do status dos agendamentos.
- Interface web adaptável a diferentes tamanhos de tela.

## Tecnologias utilizadas

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- HTML
- CSS
- Git e GitHub

## Requisitos

- Python instalado.
- Git instalado.
- Navegador web atualizado.

## Como executar o projeto

1. Abra o terminal na pasta do projeto.
2. Crie um ambiente virtual:

   ```powershell
   python -m venv .venv
   ```

3. Ative o ambiente virtual:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

4. Instale as dependências:

   ```powershell
   pip install -r requirements.txt
   ```

5. Inicie a aplicação:

   ```powershell
   python app.py
   ```

6. Abra o navegador no endereço:

   http://127.0.0.1:5000

## Banco de dados

Na configuração padrão, a aplicação utiliza SQLite para armazenar os dados localmente. O banco é utilizado pela aplicação conforme sua configuração.

## Objetivo acadêmico

Este projeto tem como finalidade aplicar conhecimentos de programação, banco de dados, desenvolvimento web, versionamento de código e organização de software.

## Repositório

Código-fonte disponível no GitHub:

https://github.com/lucineiagalvao2025-commits/patas_amigas

## Observação

Este é um MVP acadêmico. Antes de utilizar o sistema em uma clínica real, são necessários testes adicionais, controles de acesso, proteção de dados e outras medidas de segurança.

## Qualidade e revisão técnica

O sistema possui validações para evitar cadastros inconsistentes,
como peso inválido, data de nascimento futura e agendamentos sem data e horário.

A aplicação também conta com testes automatizados utilizando pytest,
permitindo verificar o funcionamento das principais funcionalidades
e identificar problemas durante a evolução do projeto.