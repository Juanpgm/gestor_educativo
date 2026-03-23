# Database Schema

## Entity Relationship

```
┌──────────┐    M:N    ┌──────────┐
│  Alumno  │◄────────► │  Tutor   │
└────┬─────┘           └──────────┘
     │ 1:N
     ▼
┌──────────┐           ┌───────────────┐
│   Nota   │──────────►│PeriodoAcademico│
└────┬─────┘           └───────────────┘
     │ N:1
     ▼
┌──────────┐    M:N    ┌──────────┐
│ Materia  │◄────────► │ Docente  │
└────┬─────┘           └──────────┘
     │ M:N
     ▼
┌──────────────┐
│ materia_grados│  (grado values)
└──────────────┘

┌──────────┐
│  Curso   │  (standalone)
└──────────┘

┌──────────┐           ┌───────────┐
│ Alumno   │──1:N────► │Documento  │
│          │           │Generado   │
└──────────┘           └───────────┘

┌───────────┐          ┌──────────┐
│ Plantilla │          │ Usuario  │
└───────────┘          └──────────┘

┌──────────┐           ┌──────────┐
│ AuditLog │           │ CostLog  │
└──────────┘           └──────────┘
```

## Tables

### alumnos

| Column           | Type           | Notes         |
| ---------------- | -------------- | ------------- |
| cod_alumno       | VARCHAR(20) PK |               |
| identificacion   | TEXT           | Encrypted PII |
| nombre           | VARCHAR(100)   |               |
| apellidos        | VARCHAR(100)   |               |
| grado            | VARCHAR(20)    |               |
| fecha_nacimiento | DATE           |               |
| fecha_ingreso    | DATE           |               |
| fecha_egreso     | DATE           | Nullable      |
| email            | TEXT           | Encrypted PII |
| telefono         | TEXT           | Encrypted PII |
| direccion        | TEXT           | Encrypted PII |
| created_at       | TIMESTAMP      | auto          |
| updated_at       | TIMESTAMP      | auto          |

### docentes

Same PII pattern as alumnos, with cod_docente PK.

### tutores

Same PII pattern, with cod_tutor PK + parentesco field.

### notas

| Column      | Type                                   | Notes             |
| ----------- | -------------------------------------- | ----------------- |
| id          | SERIAL PK                              |                   |
| cod_alumno  | VARCHAR(20) FK                         |                   |
| cod_materia | VARCHAR(20) FK                         |                   |
| cod_periodo | VARCHAR(20) FK                         |                   |
| nota        | DECIMAL(4,2)                           | Range: 0.00–10.00 |
| UNIQUE      | (cod_alumno, cod_materia, cod_periodo) |                   |

### periodos_academicos

| Column       | Type           |
| ------------ | -------------- |
| cod_periodo  | VARCHAR(20) PK |
| nombre       | VARCHAR(100)   |
| anio         | INTEGER        |
| fecha_inicio | DATE           |
| fecha_fin    | DATE           |
| activo       | BOOLEAN        |

### cursos

| Column       | Type           |
| ------------ | -------------- |
| cod_curso    | VARCHAR(20) PK |
| nombre_curso | VARCHAR(100)   |
| descripcion  | TEXT           |
| grado        | VARCHAR(20)    |
| activo       | BOOLEAN        |

### materias

| Column         | Type           |
| -------------- | -------------- |
| cod_materia    | VARCHAR(20) PK |
| nombre_materia | VARCHAR(100)   |
| descripcion    | TEXT           |
| activo         | BOOLEAN        |

### usuarios

| Column        | Type                | Notes                      |
| ------------- | ------------------- | -------------------------- |
| id            | SERIAL PK           |                            |
| email         | VARCHAR(200) UNIQUE | Indexed                    |
| password_hash | TEXT                | bcrypt                     |
| nombre        | VARCHAR(100)        |                            |
| apellidos     | VARCHAR(100)        |                            |
| rol           | ENUM                | admin, secretaria, docente |
| activo        | BOOLEAN             |                            |

### documentos_generados

| Column            | Type               | Notes                      |
| ----------------- | ------------------ | -------------------------- |
| id                | SERIAL PK          |                            |
| cod_alumno        | VARCHAR(20) FK     |                            |
| tipo              | ENUM               | diploma, certificado_notas |
| archivo_path      | TEXT               | Path to generated .docx    |
| hash_verificacion | VARCHAR(64) UNIQUE | SHA-256                    |
| qr_data           | TEXT               | QR code binary data        |
| metadata_doc      | JSONB              | Template context           |
| fecha_generacion  | TIMESTAMP          | Auto-set on creation       |

### plantillas

| Column                | Type         | Notes                      |
| --------------------- | ------------ | -------------------------- |
| id                    | SERIAL PK    | Auto-increment             |
| nombre                | VARCHAR(100) |                            |
| tipo                  | ENUM         | diploma, certificado_notas |
| idioma                | ENUM         | es, en                     |
| archivo_template_path | TEXT         | .docx template path        |
| archivo_original_path | TEXT         | Original uploaded file     |
| variables_mapeadas    | JSONB        | Jinja2 vars                |
| descripcion           | TEXT         | Optional description       |

### Association Tables

- **alumno_tutores**: cod_alumno + cod_tutor
- **docente_materias**: cod_docente + cod_materia + cod_periodo
- **materia_grados**: cod_materia + grado

### System Tables

- **audit_log**: usuario_id, accion, entidad, detalles (JSONB), ip
- **cost_log**: operacion, costo_estimado, tokens_usados, metadata_extra (JSONB)
