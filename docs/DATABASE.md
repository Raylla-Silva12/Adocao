# Modelo de Dados (Banco)

Banco PostgreSQL: **`adocao_gatos`** (Cloud SQL)  
Stack: Flask + SQLAlchemy

---

## Diagrama ER (Mermaid)

Copie o bloco abaixo em [Mermaid Live Editor](https://mermaid.live), GitLab, GitHub ou Notion:

```mermaid
erDiagram
    ADMINS {
        varchar_36 id PK "UUID — chave primária"
        varchar_255 email UK "NOT NULL — login único"
        varchar_255 password_hash "NOT NULL — senha criptografada"
        boolean is_active "DEFAULT true"
        timestamp created_at "NOT NULL"
        timestamp updated_at "atualizado automaticamente"
    }

    PETS {
        varchar_36 id PK "UUID — chave primária"
        varchar_255 name "NOT NULL — INDEX"
        varchar_50 species "NOT NULL — gato | cao"
        varchar_255 breed "opcional"
        integer age_years "opcional"
        text description "opcional — visível no site"
        varchar_255 temperament "opcional"
        boolean is_vaccinated "DEFAULT false"
        boolean is_neutered "DEFAULT false"
        varchar_500 photo_url "obrigatório no cadastro admin"
        varchar_50 owner_contact "obrigatório — SOMENTE ADMIN"
        varchar_50 status "NOT NULL — INDEX — available | pending | adopted"
        timestamp created_at "NOT NULL"
        timestamp updated_at "atualizado automaticamente"
    }
```

> **Nota:** `pets` e `admins` são tabelas **independentes** (sem foreign key entre elas).

---

## Visão geral do banco (Mermaid)

```mermaid
flowchart TB
    subgraph GCP["Google Cloud"]
        CR["Cloud Run — app Flask"]
        CS[(Cloud SQL PostgreSQL\nadocao_gatos)]
        GCS[("Cloud Storage\nfotos dos pets")]
    end

    CR -->|"SQLAlchemy"| CS
    CR -->|"upload_file()"| GCS

    subgraph Tabelas["Tabelas"]
        P[pets]
        A[admins]
    end

    CS --> P
    CS --> A
```

---

## Visibilidade do campo `owner_contact` (Mermaid)

```mermaid
flowchart LR
    A[Admin preenche no painel] --> B["POST/PUT /api/pets + JWT"]
    B --> C[(pets.owner_contact)]
    C --> D["GET /api/pets + JWT"]
    D --> E[Admin vê o contato]
    C --> F["GET /api/pets sem JWT"]
    F --> G[JSON sem owner_contact]
    C --> H[Páginas HTML /pets]
    H --> I[Site público — sem contato]
```

---

## Visibilidade dos campos

| Campo | Site público | API pública | Admin autenticado |
|-------|:------------:|:-----------:|:-----------------:|
| name, species, breed, age_years, description, temperament | Sim | Sim | Sim |
| is_vaccinated, is_neutered, photo_url, status | Sim | Sim | Sim |
| **owner_contact** | **Não** | **Não** | **Sim** |

---

## SQL — tabela `pets`

```sql
CREATE TABLE pets (
    id              VARCHAR(36)  PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    species         VARCHAR(50)  NOT NULL,
    breed           VARCHAR(255),
    age_years       INTEGER,
    description     TEXT,
    temperament     VARCHAR(255),
    is_vaccinated   BOOLEAN      DEFAULT FALSE,
    is_neutered     BOOLEAN      DEFAULT FALSE,
    photo_url       VARCHAR(500),
    owner_contact   VARCHAR(50),
    status          VARCHAR(50)  NOT NULL DEFAULT 'available',
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP
);

CREATE INDEX idx_pets_status ON pets(status);
CREATE INDEX idx_pets_name   ON pets(name);
```

## SQL — tabela `admins`

```sql
CREATE TABLE admins (
    id            VARCHAR(36)  PRIMARY KEY,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active     BOOLEAN      DEFAULT TRUE,
    created_at    TIMESTAMP    NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMP
);

CREATE UNIQUE INDEX idx_admins_email ON admins(email);
```

---

## Migração — adicionar `owner_contact`

```bash
python manage_db.py upgrade
```

```sql
ALTER TABLE pets ADD COLUMN IF NOT EXISTS owner_contact VARCHAR(50);
```
