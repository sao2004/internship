# NOTES — Onofrei Ștefan-Alexandru

Copiază acest fișier ca `NOTES.md` și completează-l.

Vrem să fie scurt — maxim 1 pagină. Mai mult contează claritatea decât lungimea.

---

## 1. Bug-urile găsite

Pentru fiecare bug, scrie 2-3 propoziții:

### Bug #1
- **Unde era:** In main.py, linia 32.
- **Cum l-am găsit:** Am observat dupa ce am rulat testele ca apare *FAILED tests/test_app.py::test_create_event_returns_201 - assert 200 == 201*. Asa am identificat bug-ul.
- **Cum l-am fixat:** Am modificat codul pentru a returna status code 201 în loc de 200.

### Bug #2
- **Unde era:** In storage.py, linia 51.
- **Cum l-am găsit:** Am rulat testele și am observat că bug-ul apare la list events si are offset de 1 raspunsul, deci aveam hint ca ar fi o problema de indexare.
- **Cum l-am fixat:** Am modificat codul (am sters acel 1) ca sa inceapa de la 0.

### Bug #3
- **Unde era:**
- **Cum l-am găsit:**
- **Cum l-am fixat:**

---

## 2. Endpoint-ul nou

- **Decizii de design:** (ce-ai considerat? ce ai ales și de ce?)
- **Cazuri edge pe care le-ai acoperit:**
- **Teste adăugate:** (ce verifică fiecare)

---

## 3. Folosirea AI-ului

Fii cinstit. Nu pierzi puncte dacă spui adevărul, dimpotrivă.

- **Ce ai folosit:** (ChatGPT / Cursor / Copilot / altele)
- **Prompturi reprezentative folosite:** (scrie prompturile pe care le consideri relevante + context scurt: la ce te-au ajutat)
- **Unde te-a ajutat cel mai mult:**
- **Unde te-a încurcat sau ți-a dat un răspuns greșit:** (foarte interesant pentru noi!)
- **Cum ai verificat ce-a generat:**
- **Anexă opțională — export chat:** (dacă vrei, poți adăuga un export de chat relevant)

---

## 4. Ce-ai face cu mai mult timp

(Lista scurtă, 3-5 puncte. Arată-ne că ai văzut limitele actuale.)

---

## 5. Întrebări / observații

(Orice nu a fost clar, orice ai vrea să discuți cu noi.)
