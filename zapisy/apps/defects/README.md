### Integracja aplikacji usterek z Google Drive

Google Drive jest wykorzystywany do przechowywania zdjęć załączonych do usterek. W przypadku braku pliku z danymi uwierzytelnienia w Google API, aplikacja powinna działać poprawnie z wyłączeniem funkcjonalności dodawania i pobierania zdjęć. Plik ten można wygenerować samemu:

1. Wejdź na https://console.cloud.google.com/apis – trzeba być zalogowanym i wybrać "projekt", jeśli się go nie ma, to trzeba go założyć.
2. Kliknij "Włącz interfejsy API i usługi", znajdź i wybierz "Google Drive API".
3. W menu po lewej wybierz "Dane logowania". Kliknij "Utwórz dane logowania" → "Konto usługi". W drugim kroku przyznaj rolę "Właściciel".
4. W liście "Konta usługi" wybierz nowo utworzone konto, przejdź do zakładki "Klucze", kliknij "Dodaj klucz" → "Utwórz nowy klucz", wybierz "JSON". Plik z wygenerowanym kluczem pobierze się automatycznie.

Plik należy umieścić w głównym katalogu djangowego projektu (tj. `/zapisy/`), a nie całego repozytorium, pod nazwą `google_drive.json` (a nie tą, pod którą został pobrany). Po uruchomieniu / _provisioningu_ maszyny wirtualnej aplikacja powinna działać z pełnymi funkcjonalnościami.

**Z plikiem z danymi uwierzytelnienia należy obchodzić się ostrożnie, a w szczególności nie wrzucać do publicznego repozytorium.** W pliku `.gitignore` w tym _branchu_ znajduje się wpis `zapisy/google_drive.json`, która częściowo nas przed tym zabezpiecza. Wciąż jednak jest ryzyko, że zmienimy _branch_, zrobimy `git add .` i _spushujemy_ ten plik – i zaraz dostaniemy groźnie brzmiącego maila od automatów Google'a, że któryś z naszych kluczy dostępu właśnie wyciekł i że lepiej go zrewokować.
