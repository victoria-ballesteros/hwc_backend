# HWC SERVER
Este proyecto implementa una arquitectura hexagonal (también conocida como puertos y adaptadores), un patrón de diseño que permite mantener el núcleo del negocio completamente independiente de los detalles técnicos y frameworks externos. La arquitectura está organizada en capas concéntricas donde el dominio (lógica de negocio) permanece en el centro, protegido de cambios en tecnologías externas.

## ESTRUCTURA DEL PROYECTO

app/ <br>
├── adapters/              # Capa de infraestructura <br>
│   ├── database/          # Adaptadores de persistencia <br>
│   │   └── postgres/      # PostgreSQL específico <br>
│   │       ├── models/    # Modelos SQLAlchemy <br>
│   │       ├── repositories/  # Implementaciones de repositorios <br>
│   │       └── connection.py  # Conexión a DB <br>
│   └── routing/           # Adaptadores web (FastAPI) <br>
│       ├── routers/       # Endpoints <br>
│       └── utils/         # Utilidades de routing <br>
│ <br>
├── domain/                # Capa de dominio (core business) <br>
│   ├── core/             # Núcleo del dominio <br>
│   │   ├── exceptions/   # Excepciones de negocio <br>
│   │   ├── services/     # Servicios de dominio <br>
│   │   ├── config.py     # Configuración <br>
│   │   └── enums.py      # Enumeraciones <br>
│   ├── dtos/             # Data Transfer Objects <br>
│   └── ports/            # Puertos (interfaces) <br>
│       ├── driven/       # Puertos hacia afuera (DB, APIs externas) <br>
│       └── driving/      # Puertos hacia adentro (casos de uso) <br>
│ <br>
└── main.py               # Punto de entrada <br>

<img width="796" height="597" alt="WHC SERVER ARCHITECTURE drawio" src="https://github.com/user-attachments/assets/1b2f5ea8-bb01-479f-8485-0a30fc330cca" />

## Ejecución

### Construir la imagen Docker:
```bash
docker compose up --build
```
### Acceder a los docs expuestos en:
```bash
http://localhost:8000/docs#/
```

## Convenciones
1. Interfaces: Sufijo ABC (Abstract Base Class)
2. Implementaciones: Sin sufijo especial
3. DTOs: Sufijo DTO
4. Modelos: Nombres en singular (ej: Test)
5. Repositorios: Sufijo Repository

## TODOs
1. Mejora del README.
2. Carga y esquematización de modelos.
