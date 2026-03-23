# API Reference

Base URL: `/api/v1`

## Authentication

| Method | Endpoint         | Auth  | Description               |
| ------ | ---------------- | ----- | ------------------------- |
| POST   | `/auth/login`    | None  | Login, returns JWT tokens |
| POST   | `/auth/register` | Admin | Register new user         |
| POST   | `/auth/refresh`  | None  | Refresh access token      |
| GET    | `/auth/me`       | Any   | Get current user profile  |

## Alumnos

| Method | Endpoint                | Auth             | Description                        |
| ------ | ----------------------- | ---------------- | ---------------------------------- |
| GET    | `/alumnos`              | Any              | List alumnos (filterable by grado) |
| GET    | `/alumnos/{cod_alumno}` | Any              | Get single alumno                  |
| POST   | `/alumnos`              | Admin/Secretaria | Create alumno                      |
| PUT    | `/alumnos/{cod_alumno}` | Admin/Secretaria | Update alumno                      |
| DELETE | `/alumnos/{cod_alumno}` | Admin/Secretaria | Delete alumno                      |

## Docentes

| Method | Endpoint                  | Auth             | Description        |
| ------ | ------------------------- | ---------------- | ------------------ |
| GET    | `/docentes`               | Any              | List docentes      |
| GET    | `/docentes/{cod_docente}` | Any              | Get single docente |
| POST   | `/docentes`               | Admin/Secretaria | Create docente     |
| PUT    | `/docentes/{cod_docente}` | Admin/Secretaria | Update docente     |
| DELETE | `/docentes/{cod_docente}` | Admin/Secretaria | Delete docente     |

## Tutores

| Method | Endpoint               | Auth             | Description      |
| ------ | ---------------------- | ---------------- | ---------------- |
| GET    | `/tutores`             | Any              | List tutores     |
| GET    | `/tutores/{cod_tutor}` | Any              | Get single tutor |
| POST   | `/tutores`             | Admin/Secretaria | Create tutor     |
| PUT    | `/tutores/{cod_tutor}` | Admin/Secretaria | Update tutor     |
| DELETE | `/tutores/{cod_tutor}` | Admin/Secretaria | Delete tutor     |

## Cursos

| Method | Endpoint              | Auth             | Description                               |
| ------ | --------------------- | ---------------- | ----------------------------------------- |
| GET    | `/cursos`             | Any              | List cursos (filterable by grado, activo) |
| GET    | `/cursos/{cod_curso}` | Any              | Get single curso                          |
| POST   | `/cursos`             | Admin/Secretaria | Create curso                              |
| PUT    | `/cursos/{cod_curso}` | Admin/Secretaria | Update curso                              |
| DELETE | `/cursos/{cod_curso}` | Admin/Secretaria | Delete curso                              |

## Materias

| Method | Endpoint                  | Auth             | Description                                 |
| ------ | ------------------------- | ---------------- | ------------------------------------------- |
| GET    | `/materias`               | Any              | List materias (filterable by grado, activo) |
| GET    | `/materias/{cod_materia}` | Any              | Get single materia                          |
| POST   | `/materias`               | Admin/Secretaria | Create materia                              |
| PUT    | `/materias/{cod_materia}` | Admin/Secretaria | Update materia                              |
| DELETE | `/materias/{cod_materia}` | Admin/Secretaria | Delete materia                              |

## Notas

| Method | Endpoint           | Auth             | Description                                         |
| ------ | ------------------ | ---------------- | --------------------------------------------------- |
| GET    | `/notas`           | Any              | List notas (filterable by alumno, materia, periodo) |
| GET    | `/notas/{nota_id}` | Any              | Get single nota                                     |
| POST   | `/notas`           | Admin/Secretaria | Create nota                                         |
| POST   | `/notas/bulk`      | Admin/Secretaria | Bulk create notas                                   |
| PUT    | `/notas/{nota_id}` | Admin/Secretaria | Update nota                                         |
| DELETE | `/notas/{nota_id}` | Admin/Secretaria | Delete nota                                         |

## Periodos Academicos

| Method | Endpoint                  | Auth             | Description    |
| ------ | ------------------------- | ---------------- | -------------- |
| GET    | `/periodos`               | Any              | List periodos  |
| POST   | `/periodos`               | Admin/Secretaria | Create periodo |
| PUT    | `/periodos/{cod_periodo}` | Admin/Secretaria | Update periodo |

## Documentos

| Method | Endpoint                        | Auth             | Description              |
| ------ | ------------------------------- | ---------------- | ------------------------ |
| GET    | `/documentos`                   | Any              | List generated documents |
| GET    | `/documentos/plantillas`        | Any              | List available templates |
| POST   | `/documentos/plantillas/upload` | Admin/Secretaria | Upload .docx template    |
| POST   | `/documentos/generar`           | Admin/Secretaria | Generate single document |
| POST   | `/documentos/generar/masivo`    | Admin/Secretaria | Mass generation          |
| GET    | `/documentos/verificar/{hash}`  | **Public**       | Verify document by hash  |
| POST   | `/documentos/analizar`          | Admin/Secretaria | OCR + LLM analysis       |

## Email

| Method | Endpoint        | Auth             | Description             |
| ------ | --------------- | ---------------- | ----------------------- |
| POST   | `/email/enviar` | Admin/Secretaria | Send document via Gmail |

## Health

| Method | Endpoint  | Auth | Description  |
| ------ | --------- | ---- | ------------ |
| GET    | `/health` | None | Health check |
