# DevOps Intern — Take-Home Task

Bine ai venit! Acest task este parte din procesul de selecție pentru poziția de **DevOps Intern**.

Scopul nostru nu este să vedem dacă știi „răspunsul corect”, ci **cum investighezi, cum citești logs, cum izolezi probleme și cum comunici ce-ai făcut**.

---

## Contextul

Suntem o companie AI-first și folosim zilnic asistenți AI (ChatGPT, Cursor, Copilot etc.). **Te încurajăm să-i folosești și tu** pentru acest task, exact așa cum ai face într-o zi normală de muncă.

Singurele reguli:

1. **Înțelege ce livrezi.** Dacă AI-ul îți spune să schimbi ceva și tu nu știi de ce, asta e o problemă.
2. **Fii transparent.** În `NOTES.md` scrie scurt ce-ai făcut tu și unde te-a ajutat AI-ul.
3. **Citește logs-urile.** Răspunsurile sunt aproape întotdeauna acolo.

## Cum începi
1.	Dezarhivează fișierul atașat la acest email
2.	Citește documentația din arhivă înainte să începi

## Task-ul

Ai primit o aplicație web simplă (FastAPI + Redis) care **ar trebui** să poată fi rulată cu Docker și să aibă un pipeline CI care trece.

**Nimic nu funcționează acum.** Pe parcursul task-ului vei întâlni probleme în:

- `Dockerfile`
- `docker-compose.yml`
- `.github/workflows/ci.yml`

### Ce trebuie să faci

1. **Pornește aplicația cu `docker compose up`** și asigură-te că răspunde la `http://localhost:8000/health`.
2. **Verifică că `http://localhost:8000/visits` funcționează** (folosește Redis pentru a număra vizitele).
3. **Adaugă un healthcheck** în `docker-compose.yml` pentru serviciul web (folosește endpoint-ul `/health`).
4. **Extinde /visits ednpoint** astfel incat sa existe functionalitatea de read `/visits/count` reset `/visits/reset` ** 
5. **Creaza CI pipeline** ce sa ruleze automat la fiecare git push.
6. **Completează `NOTES.md`** — copiază `NOTES.md.template` în `NOTES.md` și scrie un writeup scurt (vezi mai jos).

### Definition of Done

Înainte să livrezi, verifică:

- [ ] `docker compose up --build` pornește ambele servicii fără erori.
- [ ] `GET http://localhost:8000/health` întoarce `200` cu `{"status": "ok", "redis": true}`.
- [ ] `GET http://localhost:8000/visits` incrementează la fiecare request.
- [ ] `docker compose ps` arată serviciul `web` ca `healthy`.
- Adaugă un fișier `.env.example` și mută hardcoded values în variabile de mediu.
- Optimizează `Dockerfile` (cache layers, image size).
- Adaugă un step de linting în CI.
- [ ] **Extinde API-ul cu două endpoint-uri noi pentru counter (cu teste):**
- [ ] `GET /visits/count` — întoarce numărul curent de vizite **fără** să-l incrementeze. 
- [ ] `POST /visits/reset` — resetează counter-ul la `0` și întoarce `{"visits": 0}`. 
- [ ] **Adaugă un UI minimal pe path-ul `/index`:**. 
  - [ ] Returnează o pagină HTML care obtine datele din backend endpoint (`/visits`).
  - [ ] Adauga buton de reset ce apeleaza  (`/reset`).
- [ ] Nice to have CI pipeline succesful on github.
- [ ] `NOTES.md` e completat.

Mai bine livrezi corect partea de bază decât să te grăbești.

---

## Cum testezi local

Ai nevoie de:
- Docker & Docker Compose v2 (comanda `docker compose`, nu vechiul `docker-compose`)
- (Opțional pentru testare directă) Python 3.11+

Rulează:

```bash
docker compose up --build
```

Ar trebui să vezi serviciul web pornind și răspunzând la:
- http://localhost:8000/health
- http://localhost:8000/visits (incrementează la fiecare refresh)

Pentru CI: după ce ai pus codul pe un repo GitHub al tău, workflow-ul ar trebui să ruleze automat.

---

## Cum livrezi
Răspunde la email-ul inițial cu soluția ta, până duminică 7 iunie, ora 23:59. O poți livra cum îți e mai comod:
   - un link către un repo public (GitHub, GitLab, Bitbucket sau altele), sau
   - O arhivă .zip atașată la răspuns
   
Înainte de deadline, asigură-te că:
   - Ai documentat cum rulezi totul și ce decizii ai luat
   - Soluția e completă și o putem rula local
   - Răspunsul tău e trimis înainte de deadline

**Deadline: duminică, 7 iunie, ora 23:59.** Dacă ai nevoie de mai mult timp, scrie-ne — preferăm să livrezi ceva îngrijit decât să te grăbești.

---

## Cum evaluăm

Punctăm 7 dimensiuni, fiecare 1-5:

| Criteriu | Ce căutăm |
|---|---|
| **Corectitudine** | Aplicația pornește, CI e verde, healthcheck funcționează. |
| **Debugging** | În NOTES.md explică **cum** ai găsit problemele, nu doar **ce** ai schimbat. |
| **Fundamente Docker** | Imaginea e curată, layers logice, nu rulează ca root fără motiv etc. |
| **Networking** | Înțelegi porturi, servicii, DNS-ul intern din compose. |
| **Git workflow** | Commits mici, mesaje clare, istoric coerent. |
| **NOTES.md** | Scurt, clar, onest despre folosirea AI-ului și deciziile luate. |
| **Fundamente CI/CD** | Pipeline-ul e gândit, nu doar copy-paste. |

---

## Ce NU contează

- Să optimizezi imaginea sub o anumită mărime.
- Să adaugi Kubernetes / Terraform / etc. — nu e cerut.
- Să faci pipeline-ul foarte complex.

**Mai bine simplu, corect și bine explicat decât complex și impresionant.**

---

## Sfaturi

- Citește **toate logs-urile**. `docker compose up` îți spune aproape totul.
- Dacă o eroare e neclară, izolează serviciul: `docker compose up web` separat.
- Dacă te blochezi 30 de minute pe ceva, scrie în NOTES.md și treci mai departe.
- Pentru CI, uită-te la output-ul exact al fiecărui step.
- Întreabă orice neclaritate.

Succes! Suntem curioși să vedem cum gândești.
