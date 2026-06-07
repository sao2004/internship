# NOTES — Onofrei Ștefan-Alexandru

---

## 1. Bug-urile găsite

### Bug #1
- **Unde era:** În `main.py`, linia 32 — endpoint-ul `POST /events`.
- **Cum l-am găsit:** Am observat după ce am rulat testele că apare `FAILED tests/test_app.py::test_create_event_returns_201 - assert 200 == 201`.
- **Cum l-am fixat:** Am adăugat `status_code=201` la decoratorul `@app.post("/events", ...)`.

### Bug #2
- **Unde era:** În `storage.py`, linia 51 — metoda `list_events`.
- **Cum l-am găsit:** Am rulat testele și am observat că la paginare rezultatele aveau un offset de 1, ceea ce sugera o problemă de indexare.
- **Cum l-am fixat:** Am corectat slice-ul de la `all_events[offset + 1 : offset + limit]` la `all_events[offset : offset + limit]`.

### Bug #3
- **Unde era:** În `storage.py`, liniile 50 și 55 — metoda `list_events` și `soft_delete_event`.
- **Cum l-am găsit:** Testele de delete eșuau; evenimentele soft-deleted apăreau în continuare în listare.
- **Cum l-am fixat:** Am adăugat filtrul `e.deleted_at is None` în `list_events`, și am verificat în `soft_delete_event` că evenimentul nu e deja șters înainte de a returna `None`.

---

## 2. Endpoint-ul nou

- **Decizii de design:**
  - URL `/users/{user_id}/events` în loc de `/events?user_id=...` — evenimentele unui user sunt o resursă subordonată lui, nu un filtru pe colecția globală.
  - Filtrul `since` e strict `>` (nu `>=`) — dacă un client face polling și trimite `since=t0`, nu vrea să primească înapoi ultimul eveniment deja văzut.
  - Fără paginare pe acest endpoint — în contextul unui storage in-memory și al unui use case de polling incremental, lista e de obicei mică; paginarea ar complica clientul fără beneficiu real.
  - Soft-deleted excluse — consecvent cu `GET /events`.

- **Cazuri edge acoperite:**
  - `user_id` inexistent → `404` (nu `[]`, care ar fi ambiguu)
  - `since` absent → returnează toate evenimentele userului
  - `since` mai nou decât toate evenimentele → returnează `[]`, nu eroare
  - Evenimentele altor useri sunt excluse
  - Evenimentele soft-deleted sunt excluse indiferent de `since`

- **Teste adăugate:**
  - `test_list_user_events_returns_all_without_since` — fără filtru, toate evenimentele create sunt returnate
  - `test_list_user_events_filters_by_since` — cu `since=cutoff`, se întorc doar evenimentele create după cutoff
  - `test_list_user_events_unknown_user_returns_404` — user inexistent întoarce 404
  - `test_list_user_events_excludes_soft_deleted` — evenimentele șterse nu apar în răspuns
  - `test_list_user_events_only_returns_own_events` — evenimentele altui user nu se amestecă

---

## 3. Folosirea AI-ului

- **Ce am folosit:** Claude (claude.ai)

- **Prompturi reprezentative folosite:**
  - *"Adaugă un endpoint `GET /users/{user_id}/events?since=<ISO_date>` [+ fișierele atașate]"* — pentru generarea endpoint-ului, metodei din storage și a testelor
  - *"[traceback complet] — testul `test_list_user_events_filters_by_since` pică cu PydanticUserError"* — pentru diagnosticarea eroriii de compatibilitate Python 3.14 + Pydantic v2
  - *"Decizii de design / cazuri edge / ce verifică testele"* — pentru a structura secțiunea 2 din acest fișier

- **Unde m-a ajutat cel mai mult:** La diagnosticarea rapidă a erorii Pydantic — eroarea era legată de forward references în Python 3.14 și nu era evidentă din traceback; AI-ul a identificat că `Optional[datetime]` devine `ForwardRef` și a propus `datetime | None` ca fix. M-a ajutat si la acest Notes pentru identare si explicarea mai profesională a eroriilor.

- **Unde m-a încurcat sau mi-a dat un răspuns greșit:** La prima variantă a fix-ului pentru eroarea Pydantic, AI-ul a adăugat `from __future__ import annotations` împreună cu `datetime | None`. Aceasta e de fapt o combinație contradictorie — `from __future__ import annotations` face ca *toate* adnotările să devină lazy strings, ceea ce agravează exact problema pe care încearcă să o rezolve. A trebuit eliminat imediat.

- **Cum am verificat ce a generat:** Am rulat `pytest -v` după fiecare modificare și am urmărit că toate cele 17 teste trec; am citit codul generat înainte de a-l aplica.

---

## 4. Ce-aș face cu mai mult timp

- **Bază de date reală** — storage-ul in-memory pierde toate datele la restart; un SQLite sau PostgreSQL cu SQLAlchemy ar rezolva asta și ar face paginarea corectă (nu slice pe listă).
- **Paginare pe `/users/{user_id}/events`** — relevant dacă un user poate avea mii de evenimente.
- **Validare email la `POST /users`** — câmpul `email` e un `str` simplu; Pydantic are `EmailStr` care validează formatul.
- **Timestamps din DB, nu din aplicație** — `created_at` e setat cu `datetime.now()` în model; dacă două requesturi vin simultan, ordinea nu e garantată. Un DB care setează timestamp-ul la INSERT e mai sigur.
- **Autentificare** — oricine poate crea/șterge evenimente pentru orice user; un sistem real ar necesita cel puțin un token simplu.

---

## 5. Întrebări / observații

- Bug-urile din task au fost intenționat introduse sau erau deja în codul de bază? Mă întreb dacă e un exercițiu de code review sau de debugging din teste.
- Pentru endpoint-ul nou: în producție, `since` ca query param ISO 8601 poate cauza probleme de URL encoding (`+` din offset-ul de timezone se poate pierde). O alternativă ar fi Unix timestamp. A fost luat în considerare?
