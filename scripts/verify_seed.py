"""Quick verification that seeded data is accessible via the API."""
import json
import sys
import httpx

base = "http://localhost:8000"
results = []

try:
    r = httpx.post(f"{base}/api/v1/auth/login", json={"email": "admin@gestor.edu", "password": "Test1234!"})
    token = r.json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}
    results.append(("Login", "OK"))
except Exception as e:
    print(f"FATAL: Login failed - {e}", file=sys.stderr)
    sys.exit(1)

for name, url in [("Alumnos", "/api/v1/alumnos"), ("Docentes", "/api/v1/docentes"),
                   ("Tutores", "/api/v1/tutores"), ("Cursos", "/api/v1/cursos"),
                   ("Materias", "/api/v1/materias"), ("Notas", "/api/v1/notas")]:
    r = httpx.get(f"{base}{url}", headers=h)
    results.append((name, len(r.json())))

r = httpx.get(f"{base}/api/v1/notas/periodos", headers=h)
results.append(("Periodos", len(r.json())))

# Output as JSON for clean parsing
print(json.dumps(dict(results), indent=2, ensure_ascii=False))
