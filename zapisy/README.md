## Projekt Systemu Zapisów Instytutu Informatyki Uniwersytetu Wrocławskiego

### Rozpoczynanie pracy

Aby rozpocząć pracę w projekcie przejdź przez instrukcję:
https://github.com/lewymati/projektzapisy/wiki/Developer's-environment-setup

Będziesz potrzebował dump-a bazy:
https://www.dropbox.com/s/exwyayfu38nlgqh/a_dump2017_04_10__12_33_58.sql.gz?dl=0

_O nowszego dumpa można poprosić na Slacku._

### Narzędzia

* **Slack** - nasz główny komunikator: https://projektzapisy.slack.com/
* **Redmine** - publiczny tracker błędów: https://tracker-zapisy.ii.uni.wroc.pl/projects/zapisy-tracker/issues
* **Rollbar** - tracker błędów pojawiających się na produkcji: https://rollbar.com/IIUniversityofWroclaw/System-Zapisow/
* **CircleCI** - continuous integration: https://circleci.com/gh/lewymati/projektzapisy

### Workflow pracy

1. Gdy decydujemy się zająć się jakąś funkcjonalnością/bugiem przypisujemy sobie odpowiedni Issue tutaj na Githubie (jeśli go nie ma to, tworzymy go).
2. Pracujemy na swoim branchu - tworzymy go z brancha `master-dev`.
3. Po ukończeniu tworzymy Pull Requesta z bazowym branchem `master-dev`.
4. Wybieramy w PR dwie osoby, do zrobienia Code Review.
5. Po akceptacji dwóch osób możemy samodzielnie kliknąć Merge.
6. Co jakiś czas (około dwóch tygodni-miesiąca) robiony jest deploy na produkcję. Branch `master` przechowuje wersję produkcyjną.

### Wskazówki

* Napotykając na problem warto napisać na Slacku. Jest szansa, że ktoś inny już natrafił na ten problem (a jeśli nie to przynajmniej inne osoby mogą być świadome trudności)
* Starą wersję bazy danych, możesz aktualizować aplikując migracje komendą:
`./manage.py migrate`
* Zmieniając model, możesz zmienić strukturę bazy danych. Poniższą komendą możesz wygenerować automatycznie migrację:
`./manage.py schemamigration appname --auto --update`
