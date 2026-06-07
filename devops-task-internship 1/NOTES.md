# NOTES — Onofrei Ștefan-Alexandru

---

## 1. Probleme găsite și fixate

### Problemă #1 (Dockerfile — cale greșită spre requirements)
- **Simptom:** `docker compose up --build` eșua cu `COPY failed: file not found: app/requirements.txt`.
- **Cum am diagnosticat-o:** Eroarea din build log era explicită. Am verificat structura arhivei: `requirements.txt` era la root, nu în `app/`.
- **Cum am fixat-o:** Am mutat `requirements.txt` în `app/` (unde se află și `main.py`), aliniind structura cu ce așteaptă Dockerfile-ul. Alternativ se putea schimba path-ul în Dockerfile, dar am preferat să păstrez structura `app/` consistentă.

### Problemă #2 (Dockerfile — CMD cu modul greșit)
- **Simptom:** Containerul pornea dar returna `ModuleNotFoundError: No module named 'main'`.
- **Cum am diagnosticat-o:** `docker logs` arăta eroarea la startup. WORKDIR era `/code`, iar aplicația stă în `app/main.py` — deci modulul uvicorn trebuia să fie `app.main:app`.
- **Cum am fixat-o:** Am schimbat CMD în `uvicorn app.main:app --host 0.0.0.0 --port 8000` și am eliminat `WORKDIR /code/app` care schimba directorul de lucru în mod inutil.

### Problemă #3 (docker-compose.yml — REDIS_HOST greșit)
- **Simptom:** `/health` returna `{"status": "ok", "redis": true}` chiar și când Redis nu era accesibil. `/visits` dădea `ConnectionRefusedError`.
- **Cum am diagnosticat-o:** Am observat `REDIS_HOST=localhost` — în rețeaua Docker Compose, serviciile comunică prin numele lor (DNS intern), nu prin `localhost`. `localhost` din perspectiva containerului `web` e propriul container.
- **Cum am fixat-o:** Schimbat în `REDIS_HOST=redis` (numele serviciului din compose).

### Problemă #4 (Bug în /health — redis_ok mereu True)
- **Simptom:** Endpoint-ul `/health` raporta `"redis": true` chiar și când Redis era down.
- **Cum am diagnosticat-o:** Am citit codul — `except redis.RedisError: redis_ok = True` era evident greșit.
- **Cum am fixat-o:** Schimbat în `redis_ok = False`. Fără fix, healthcheck-ul nu ar fi detectat niciodată o problemă cu Redis.

---

## 2. Healthcheck-ul adăugat

- **Cum funcționează:** Folosește `python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"` — stdlib pură, fără dependențe extra (curl nu era în imaginea slim). Docker marchează containerul ca `healthy` când comanda returnează exit code 0.
- **De ce această configurare:** `interval: 10s` e suficient de frecvent fără să supraîncarce. `start_period: 10s` îi dă uvicorn timp să pornească înainte ca eșecurile să conteze. `retries: 3` evită false-negative-uri tranzitorii. Am adăugat și healthcheck pe Redis (`redis-cli ping`) cu `depends_on: condition: service_healthy` — web-ul nu pornește până Redis nu e ready.

---

## 3. Folosirea AI-ului

- **Ce am folosit:** Claude (Anthropic)
- **Unde a ajutat cel mai mult:** Generarea boilerplate-ului pentru UI-ul HTML inline și structura CI pipeline-ului GitHub Actions.
- **Unde a dat răspuns greșit / unde am corectat:** A generat inițial testul pentru `/visits/count` fără să verifice că `incr` nu e apelat — am adăugat `mock_redis.incr.assert_not_called()` manual, pentru că asta e tocmai ce diferențiază `/count` de `/visits`.
- **Cum am verificat:** Am rulat `pytest` local și am citit fiecare test să înțeleg ce aserțiune face și de ce.

---

## 4. Ce-aș face cu mai mult timp

1. **Non-root user** — adăugat în Dockerfile, dar fără testare pe edge cases de permisiuni.
2. **Secret management** — Redis ar putea necesita parolă; acum e fără auth, inacceptabil în prod.
3. **Structured logging** — `uvicorn` logează request-uri, dar nu avem logs pentru erori Redis cu context.
4. **Rate limiting pe `/visits`** — un client poate incrementa contorul la infinit.
5. **Docker image scan în CI** — `trivy` sau `grype` pentru vulnerabilități în dependențe.

---

## 5. Întrebări / observații

- `NOTES.md.template` menționează 4 probleme predefinite — am găsit mai multe (bug-ul din health, plus lipsă tests pentru endpoint-urile noi). Am documentat tot.
- Endpoint-ul `/visits/reset` e `POST` (modifică stare) — corect semantic REST, dar README-ul îl numea uneori `/reset` fără prefix. Am ales `/visits/reset` pentru consistență cu `/visits/count`.
