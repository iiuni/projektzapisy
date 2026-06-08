# Stawianie Systemu Zapisów

W tej sekcji opiszemy jak można skonfigurować maszynę zdalną z systemem Ubuntu i postawić na niej System Zapisów.

## Przygotowywanie maszyny

Każdy admin ma swoje własne konto z uprawnieniami sudo bez hasła na maszynie zdalnej. Ze względów bezpieczeństwa, administratorzy muszą korzystać z weryfikacji kluczem publicznym przy logowaniu do serwera.

### Zmiana konfiguracji sudo na maszynie zdalnej

1. Zaloguj się do maszyny zdalnej używając `ssh`

**Pierwsze logowanie:**

2. Otwórz plik _sudoers_ używając komendy `sudo visudo`
3. Dodaj poniższą linijkę na koniec pliku: 
   ```
   %adm ALL=(ALL:ALL) NOPASSWD: ALL
   ```
4. Zapisz zmiany

**Dla każdego nowego użytkownika:**

5. Dodaj użytkownika do grupy `adm`:
   ```
   sudo usermod -a -G adm username
   ```
   gdzie `username` to nazwa użytkownika na maszynie zdalnej
6. Wyloguj się

### Przygotuj połączenie ssh

Powinieneś łączyć się z maszynami zdalnymi tylko i wyłącznie używając kluczy SSH (nigdy hasłem).

1. Jeśli nie masz pliku klucza prywatnego (_private_key_file_), musisz wygenerować go na swoim komputerze poleceniem `ssh-keygen`
2. Przekopiuj swój klucz publiczny do maszyny zdalnej poleceniem `ssh-copy-id user@host`, gdzie `user` to twoja nazwa użytkownika a `host` to nazwa hosta maszyny zdalnej.

## Definiowanie Inwentarza

Ansible to narzędzie, które wykonuje odgórnie zdefiniowane akcje (zebrane w _playbooki_) na maszynach zdalnych. Akcje te definiowane są w pewnym _inwentarzu_.
My używamy dwóch plików inwentarza: jednego dla serwera ze [_staging_](hosts/staging), drugiego dla [_production_](hosts/staging). 
Poniżej jest opisane, jak można połączyć się z jednym z nich.

1. Zmodyfikuj plik _hostfile_ (plik inwentarza taki jak `production` lub `staging`) w katalogu _hosts_. Dodaj tą ścieżkę do swojego pliku ssh _private_key_file_.
2. Jeśli jest to konieczne, podmień inne zmienne swoimi danymi.
   **Słowniczek**:
   - `ansible_user` — nazwa użytkownika na maszynie zdalnej
   - `ansible_host` — adres ip lub publiczna nazwa hosta maszyny zdalnej
   - `ansible_port` — port ssh
   - `deploy_user` — specjalny użytkownik który zostanie utworzony na nasze potrzeby
   - `deploy_version` — nazwa brancha z repozytorium **projektzapisy**
   - `deploy_server_name` — domena wskazująca na maszynę zdalną
3. Upewnij się, że wszystkie zmienne w [`hosts/group_vars/all`](hosts/group_vars/all) mają poprawne wartości. Niektóre zmienne są przechowywane w naszym repozytorium po zaszyfrowaniu. Jeśli chcesz ich używać, upewnij się, że masz hasło. ([zobacz więcej](#zaszyfrowane-zmienne)).

### Konfiguracja maszyny zdalnej

W tym kroku zainstalujemy i skonfigurujemy wszystkie potrzebne paczki na twojej maszynie zdalnej. Możesz wykonać ten krok również przy potrzebie aktualizacji konfiguracji. W katalogu _infra_ użyj polecenia:

```
ansible-playbook playbooks/configure.yml -i hosts/hostfile
```

### Aktualizacja konfiguracji własnymi certyfikatami OpenSSL 

Po odpaleniu playbooka `configure.yml` na maszynie zdalnej zostaną utworzone samo-podpisane certyfikaty OpenSSL. Żeby zastąpić te pliki swoimi certyfikatami:

1. Umieść swój prywatny klucz OpenSSL w katalogu _playbooks/ssl_ i zmień jego nazwę na `zapisy.key`
2. Umieść swój plik certyfikatu OpenSSL w katalogu _playbooks/ssl_ i zmień jego nazwę na `zapisy.crt`.
3. Odpal komendę:

```
ansible-playbook playbooks/update_ssl.yml -i hosts/hostfile
```

## Deployment

Deployment to proces przesyłania i uruchamiania nowej wersji aplikacji (u nas Systemu Zapisy) na maszynie zdalnej. 
Deployment może zostać rozpoczęty automatycznie, np. poprzez Github Actions. Żeby ręcznie rozpocząć deployment, w katalogu _infra_ wykonaj komendę:

```
ansible-playbook playbooks/deploy.yml -i hosts/hostfile
```

## Przywrócenie bazy danych

Żeby przywrócić bazę danych, wrzuć plik zrzutu bazy danych do archiwum `dump.7z` w katalogu _playbooks_ i wykonaj komendę:

```
ansible-playbook playbooks/restore_db.yml -i hosts/hostfile
```

## Dodatkowe informacje

### Debugowanie

Żeby wyświetlić dodatkowe informacje w czasie konfiguracji, deploymentu lub przywracania bazy danych, dodaj flagę `-vvv` do poleceń ansible-playbook i ustaw zmienną środowiskową `ANSIBLE_STDOUT_CALLBACK=debug` dla lepszej czytelności.

Logi są przechowywane w folderze _logs_ w każdej wersji deploymentu.
Wszystkie wersje znajdziesz w folderze `/home/deploy_user/deploy/releases` na maszynie zdalnej, gdzie `deploy_user` jest wartością zdefiniowaną w pliku inwentarza.

Inne przydatne komendy do użycia na maszynie zdalnej:

- `journalctl -xe` — pokazuje najnowsze logi wszystkich usług
- `journalctl -u example.service -fe` — pokazuje i śledzi najnowsze logi z usługi example-service
- `systemctl status example.service` — pokazuje status usługi example-service.

UWAGA:
`hosts/example` służy do uruchamiania Systemu Zapisów na próbę, bez potrzeby uwierzytelniania;

### Zaszyfrowane zmienne

System Zapisy używa kilka zewnętrznych usług, z których wszystkie wymagają jakiejś formy uwierzytelniania. Potrzebne dane są wymienione w [`hosts/group_vars/all`](hosts/group_vars/all), ale z oczywistych powodów nie są tam przechowywane.

Zamiast tego, przechowujemy je po szyfrowaniu z hasłem (przy użyciu [_AnsibleVault_](https://docs.ansible.com/ansible/latest/user_guide/vault.html)) w pliku [`hosts/group_vars/vault`](hosts/group_vars/vault). 
Wszyscy hostowie w grupie `vault` (co dotyczy zarówno _staging_ i _production_, ale nie _example_) nadpiszą placeholdery z `hosts/group_vars/all` tymi zaszyfrowanymi wartościami (więc użycie ich będzie wymagało hasła; [użyj `--ask-vault-pass` lub `--vault-password-file` przy odpalaniu playbooków](https://docs.ansible.com/ansible/latest/user_guide/vault.html#using-encrypted-variables-and-files)).

### Deployowanie konretnego _brancha_ na maszynie zdalnej

Jeśli chcesz na deploymencie korzystać z konkretnego brancha z GitHuba (chociażby własnego), oto kilka słów:

W pliku [_playbooks/deploy.yml_]() jedna z naszych playbookowych akcji to:
   ```
   - name: Clone the project to the new release folder
      become: yes
      become_user: "{{ deploy_user }}"
      git:
        repo: 'https://github.com/iiuni/projektzapisy.git'
        dest: "{{ deploy_helper.new_release_path }}"
        version: "{{ deploy_version }}"
   ```
   
'deploy_version' jest zdefiniowane w katalogu 'hosts', i np. dla _production_ jest to domyślnie

   ```
   deploy_version=master
   ```
   
Możesz zmodyfikować tą zmienną ręcznie - pamiętaj jednak, że taki playbook dosięgnie jedynie branche które zostały już spushowane na GitHubie - więc jeśli 'git push' nie zostało wykonane na swoich lokalnych zmianach, nie będą one widoczne w deploymencie maszyny zdalnej.


## Przykład

Żeby przetestować deployment lokalnie (używając maszyny wirtualnej), należy zastosować poniższe instrukcje.

1. Zainstaluj VirtualBox, Vagrant, oraz Ansible.
2. W katalogu `infra/hosts` wykonaj `vagrant up`.
3. W katalogu `infra`, wykonaj poniższe polecenia:
   ```bash
   ansible-playbook playbooks/configure.yml -i hosts/example
   ansible-playbook playbooks/deploy.yml -i hosts/example
   # przed resztą poleceń najpierw umieść plik zrzutu bazy danych w `playbooks/dump.7z`
   ansible-playbook playbooks/restore_db.yml -i hosts/example
   ```
4. Sprawdź adres [192.168.33.10](http://192.168.33.10/) w swojej przeglądarce
