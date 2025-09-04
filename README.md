# 🏠 Sistema de Gestão de Aluguéis V2

**Plataforma completa e profissional para gestão de aluguéis, proprietários, imóveis e participações. Arquitetura moderna, escalável e com interface responsiva para desktop e mobile.**

[![Versão](https://img.shields.io/badge/versão-2.0-blue.svg)](./VERSION)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)
[![Licença](https://img.shields.io/badge/licença-MIT-green.svg)](./LICENSE)

---

## 📋 Visão Geral

O Sistema de Gestão de Aluguéis V2 é uma solução completa para administração imobiliária, oferecendo funcionalidades robustas para gestão de proprietários, imóveis, aluguéis mensais e participações societárias. A plataforma conta com backend modular FastAPI, frontend responsivo e versão mobile PWA.

### ✨ Características Principais

- 🔐 **Autenticação Segura**: Sistema JWT com login obrigatório.
- 📱 **Interface Responsiva**: Desktop e versão mobile PWA.
- 📊 **Dashboard Interativo**: Gráficos e métricas em tempo real.
- 📈 **Relatórios Avançados**: Filtros por período e proprietário.
- 📤 **Importação Excel**: Drag & drop com validação automática.
- 🐳 **Docker Ready**: Orquestração completa com Docker Compose.

---

## 🏗️ Arquitetura do Sistema

### Estrutura de Pastas

```text
AlugueisV2/
├── backend/                    # API FastAPI modular
│   ├── main.py                # Aplicação principal
│   ├── models_final.py        # Modelos de dados
│   ├── routers/               # Endpoints organizados
│   └── ...
├── frontend/                   # Interface web principal
│   ├── index.html             # Página principal
│   ├── mobile/                # Versão PWA mobile
│   └── src/
│       ├── css/
│       └── js/
│           ├── app.js         # Aplicação principal
│           ├── modules/       # Módulos funcionais
│           └── services/      # Serviços
├── database/                   # Scripts BD e backups
├── docs/                       # Documentação técnica
├── scripts/                    # Scripts automação
├── docker-compose.yml          # Orquestração containers
└── README.md                   # Este arquivo
```

---

## 🛠️ Stack Tecnológica

### Backend
- **🐍 Python 3.10+**
- **⚡ FastAPI**
- **🗄️ PostgreSQL 15+**
- **🔗 SQLAlchemy**
- **📊 Pandas**
- **🔐 JWT**

### Frontend
- **🌐 HTML5/CSS3/JavaScript ES6+**
- **🎨 Bootstrap 5**
- **📊 Chart.js**
- **📱 PWA**

### DevOps & Infraestrutura
- **🐳 Docker & Docker Compose**
- **🌐 Nginx**

---

## 🚀 Instalação e Configuração

### Pré-requisitos

- **Docker** & **Docker Compose** instalados
- **Git** para clonagem do repositório

### Instalação Rápida

1. **Clone o repositório**
   ```bash
   git clone https://github.com/Mlocoes/AlugueisV2.git
   cd AlugueisV2
   ```

2. **Inicie o sistema completo**
   ```bash
   docker-compose up -d --build
   ```

3. **Acesse a aplicação**
   - 🌐 **Frontend Desktop**: [http://192.168.0.7:3000](http://192.168.0.7:3000)
   - 📱 **Versão Mobile**: [http://192.168.0.7:3000/mobile](http://192.168.0.7:3000/mobile)
   - 📚 **Documentação API**: [http://192.168.0.7:8000/docs](http://192.168.0.7:8000/docs)

### Usuário Padrão

- **Usuário**: `admin`
- **Senha**: `admin`

---

## 🧩 Módulos e Funcionalidades

### 🏠 Gestão de Proprietários
- CRUD completo de proprietários.
- Dados pessoais, contato e informações bancárias.
- Sistema de busca avançada.

### 🏢 Gestão de Imóveis
- CRUD completo de imóveis.
- Informações detalhadas: localização, características, valores.

### 💰 Gestão de Aluguéis
- Registro mensal por proprietário e imóvel.
- Cálculos automáticos de valores.

### 📊 Sistema de Participações
- Gestão de co-propriedade e sociedade.
- Controle por versões com histórico.
- Percentuais de participação por imóvel.

### 📈 Dashboard e Relatórios
- Gráficos interativos com Chart.js.
- Resumos por proprietário e período.
- Filtros avançados (ano, proprietário).

### 📤 Importação de Dados
- Upload via drag & drop.
- Templates Excel pré-formatados.
- Validação automática de dados.

### 🔐 Sistema de Autenticação
- Login obrigatório com JWT.
- Sessões seguras.
- Controle de tipos de usuário.

---

## �️ Solução de Problemas

### Importação de Alquileres (0 registros importados)

**Problema**: Al importar Excel de alquileres se leen los registros correctamente pero se importan 0.

**Causa**: Error en trigger `calcular_taxa_proprietario_automatico()` que buscaba columna `participacao` inexistente.

**Solución**: 
- Para **nuevas instalaciones**: ya está corregido en `database/init-scripts/000_estrutura_nova.sql`
- Para **instalaciones existentes**: ejecutar `database/migrations/009_fix_trigger_taxa_proprietario.sql`

```sql
-- Aplicar corrección manualmente si necesario:
CREATE OR REPLACE FUNCTION calcular_taxa_proprietario_automatico()
RETURNS TRIGGER AS $$
BEGIN
    SELECT (porcentagem / 100.0) * NEW.taxa_administracao_total
    INTO NEW.taxa_administracao_proprietario
    FROM participacoes 
    WHERE proprietario_id = NEW.proprietario_id 
    AND imovel_id = NEW.imovel_id 
    LIMIT 1;
    
    IF NEW.taxa_administracao_proprietario IS NULL THEN
        NEW.taxa_administracao_proprietario := 0;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### Verificación de Importación Exitosa

```bash
# Verificar registros importados
docker exec -t alugueisV1_postgres psql -U alugueisv1_usuario -d alugueisv1_db -c "SELECT COUNT(*) FROM alugueis;"
```

---

## �📄 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.
