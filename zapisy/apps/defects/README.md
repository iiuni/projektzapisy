### Synchronizacja z Google drive z aplikacją usterek

Google Drive jest wykorzystywany do przechowywania zdjęć załączonych do usterek. W przypadku braku pliku, aplikacja nie będzie działać poprawnie tylko przy dodawaniu/pobieraniu zdjęć. Plik z danymi potrzebnymi do autoryzacji w Google Drive powinien zostać umieszczony w głównym folderze **Django**(nie projektu). Plik można odebrać u prowadzącego zajęcia lub wygenerować go samemu:

1. Wejść w [link](https://cloud.google.com/docs/authentication#service-accounts) i dodać konto usługi.
2. Kliknąć w wygerowane konto i otworzyć zakładkę klucze.
3. Dodaj klucz -> Utwórz nowy klucz - pobierze nowy klucz dostępu
4. Odpalić projekt zapisy z nowym kluczem
5. Tutaj użytkownik otrzyma błąd w którym będzie podany link do strony z przyciskiem, który uaktywni usługę Google Drive w stworzonym wcześniej koncie.
