# Modelo de Dados (Banco)

O banco PostgreSQL (`adocao_gatos`) possui duas tabelas principais: **pets** e **admins**.

## Fluxograma (ER)

```mermaid
erDiagram
    ADMINS {
        varchar id PK "UUID"
        varchar email UK "login do admin"
        varchar password_hash "senha criptografada"
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    PETS {
        varchar id PK "UUID"
        varchar name "nome do pet"
        varchar species "gato | cao"
        varchar breed "raça (opcional)"
        int age_years "idade (opcional)"
        text description "descrição pública"
        varchar temperament "temperamento"
        boolean is_vaccinated
        boolean is_neutered
        varchar photo_url "URL da foto"
        varchar owner_contact "contato do responsável — só admin"
        varchar status "available | pending | adopted"
        datetime created_at
        datetime updated_at
    }
```

## Visibilidade dos campos

| Campo | Site público | API pública (`GET /api/pets`) | Admin autenticado |
|-------|--------------|--------------------------------|-------------------|
| name, species, breed, age, description, temperament | Sim | Sim | Sim |
| is_vaccinated, is_neutered, photo_url, status | Sim | Sim | Sim |
| **owner_contact** | **Não** | **Não** | **Sim** |

O campo `owner_contact` guarda o telefone (ou outro contato) de quem colocou o pet para adoção. Ele **nunca** aparece nas páginas HTML do site nem nas respostas da API sem JWT válido.

## SQL da tabela `pets`

```sql
CREATE TABLE pets (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    species VARCHAR(50) NOT NULL,
    breed VARCHAR(255),
    age_years INTEGER,
    description TEXT,
    temperament VARCHAR(255),
    is_vaccinated BOOLEAN DEFAULT FALSE,
    is_neutered BOOLEAN DEFAULT FALSE,
    photo_url VARCHAR(500),
    owner_contact VARCHAR(50),
    status VARCHAR(50) NOT NULL DEFAULT 'available',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP
);

CREATE INDEX idx_pets_status ON pets(status);
CREATE INDEX idx_pets_name ON pets(name);
```

## Atualizar banco existente (produção)

Se o projeto já estava no ar antes desta alteração, rode:

```bash
python manage_db.py upgrade
```

Ou direto no PostgreSQL / Cloud SQL:

```sql
ALTER TABLE pets ADD COLUMN IF NOT EXISTS owner_contact VARCHAR(50);
```

## Fluxo de dados — contato do responsável

```mermaid
flowchart LR
    A[Admin preenche contato no painel] --> B[POST/PUT /api/pets com JWT]
    B --> C[(PostgreSQL pets.owner_contact)]
    C --> D[GET /api/pets com JWT]
    D --> E[Painel admin exibe contato]
    C --> F[GET /api/pets sem JWT]
    F --> G[Resposta JSON sem owner_contact]
    C --> H[Páginas /pets HTML]
    H --> I[Site público — sem contato]
```
