# System Zapisów [Instytutu Informatyki UWr](https://ii.uni.wroc.pl/)

System do obsługi _cyklu dydaktycznego_ w Instytucie Informatyki Uniwersystetu
Wrocławskiego. Za pomocą tego systemu: Nauczyciele tworzą swoje propozycje
nowych przedmiotów; Studenci kształtują ofertę dydaktyczną poprzez głosowanie na
te propozycje; Dyrekcja Instytutu przydziela zajęcia prowadzącym; Studenci
zapisują się na zajęcia; W końcu studenci oceniają swoich nauczycieli w
anonimowych ankietach. System zarządza też tematami prac dyplomowych i pozwala
studentom je rezerwować.

## Uruchamianie

Do postawienia _developerskiej_ wersji systemu zapisów musimy mieć
zainstalowanego [Vagranta](https://www.vagrantup.com/) oraz Virtualboxa.
Klonujemy niniejsze repozytorium na nasz komputer i odpalamy z niego polecenie
`vagrant up`. Na naszym komputerze zostanie skonfigurowana maszyna wirtualna z
uruchomionym testowym serwerem, który można odwiedzić pod adresem
[0.0.0.0:8000](http://0.0.0.0:8000). Folder `projektzapisy` na naszym komputerze
jest współdzielony z maszyną wirtualną (folder `/vagrant`), więc serwer łapie na
żywo wszystkie zmiany w robione przez nas w kodzie. Więcej informacji o maszynie
developerskiej można przeczytać [w
instrukcji](https://github.com/iiuni/projektzapisy/wiki/Developer's-environment-setup).

Jeżeli zamierzasz zajmować się _frontendem_, warto zapoznać się też z [opisem
systemu plików
statycznych](https://github.com/iiuni/projektzapisy/wiki/Pliki-statyczne-w-Systemie-Zapisów).

## Architektura systemu

System Zapisów jest podzielony na moduły (zwane aplikacjami). Każda aplikacja
definiuje swoje własne typy danych
([_modele_](https://docs.djangoproject.com/en/3.1/intro/tutorial02/#creating-models)),
którym odpowiadają automatycznie obsługiwane tabele w bazie danych. Każda
aplikacja dba o swoje własne ścieżki
([URL-e](https://docs.djangoproject.com/en/3.1/intro/tutorial01/#write-your-first-view))
i implementuje funkcje odpowiadające na zapytania HTTP (zwane
[_widokami_](https://docs.djangoproject.com/en/3.1/intro/tutorial03/#write-views-that-actually-do-something)).
Powiązania między aplikacjami są realizowane poprzez importowanie kodu z jednego
modułu do drugiego oraz przez klucze obce w bazie danych. Zwięzły opis
wszystkich aplikacji w naszym systemie
[tutaj](https://github.com/iiuni/projektzapisy/wiki/Opis-aplikacji).

### Zmiany w schemacie bazy danych

Każda zmiana w modelach musi zostać odzwierciedlona w schemacie bazy danych, co
Django rozwiązuje _migracjami_ — małymi skryptami w Pythonie, które mówią, jak
ma się zmienić schemat bazy danych. Migracje można automatycznie wygenerować
poleceniem `python zapisy/manage.py makemigrations` (w maszynie wirtualnej), ale
czasem trzeba je ręcznie przerobić, jeśli zmiana w modelach wymaga transformacji
danych.

## Maszyna produkcyjna

Proces instalacji i konfiguracji maszyny produkcyjnej jest mocno zautomatyzowany
dzięki narzędziu _Ansible_. Instrukcje w katalogu [`infra/`](infra/).

## Zespół

Zespół Systemu Zapisów tworzą w każdym semestrze studenci uczęszczający na
przedmiot [Rozwój Systemu
Zapisów](https://zapisy.ii.uni.wroc.pl/offer/895_projekt-rozwoj-systemu-zapisow/).
Lider projektu jest zarazem prowadzącym przedmiot. W naszej pracy używamy
następujących narzędzi:

- **[Slack](https://projektzapisy.slack.com/)** — nasz główny komunikator.
- **[Rollbar](https://rollbar.com/iiuni/projektzapisy/)** —
  raportuje o błędach (wyjątkach) pojawiających się na produkcji.
- **[Travis CI](https://travis-ci.com/iiuni/projektzapisy)** — testowanie kodu.
- **[New Relic](https://one.newrelic.com/)** — monitorowanie wydajności serwera.

### Schemat pracy

1. Gdy zaczynamy pracować nad jakimś zadaniem, tworzymy gałąź, która odgałęzia
   się od `master-dev`. W swojej własnej gałęzi możemy [_przepisywać
   historię_](https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History),
   szczególnie jeśli ma nam to pomóc [zaktualizować się w stosunku do
   `master-dev`](https://stackoverflow.com/a/29916361).
2. Po ukończeniu tworzymy Pull Requesta z bazową gałęzią `master-dev`.
   Zaznaczamy lidera projektu do _code-review_. PR musi być ładnie i jasno
   opisany — opis ten może w przyszłości pomóc komuś zrozumieć intencje stojące
   za zmianą w kodzie.
3. Proces _code-review_, dyskusji i nanoszenia poprawek zazwyczaj składa się z
   więcej niż jednego etapu. Należy na niego zarezerwować z grubsza tyle czasu,
   co na przygotowanie PR-a.
4. Zaakceptowane Pull Requesty będą scalane przez lidera projektu za pomocą `git
   merge --squash`. Nie musimy się zatem wstydzić rewizji (commitów) w naszej
   gałęzi.
5. Co jakiś czas (około dwóch tygodni-miesiąca) robiony jest deploy na
   produkcję. Gałąź `master` przechowuje wersję produkcyjną.
