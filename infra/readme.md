# System Zapisów Deployment

This manual will allow you to configure the remote machine with the Ubuntu
system and deploy System Zapisów on it.

## Setting up the machine

Every admin has his own account with no-password sudo privileges on the remote
machine. For security, the admin has to use public-key authentication to log in
to the server.

### Change sudo configuration on the remote machine

1. Log in into remote machine with `ssh`

**For the first time:**

2. Open _sudoers_ file with `sudo visudo` command
3. Add following line to the end of the file:
   ```
   %adm ALL=(ALL:ALL) NOPASSWD: ALL
   ```
4. Save changes

**For every new user:**

5. Add the user to the `adm` group:
   ```
   sudo usermod -a -G adm username
   ```
   where `username` is the username on the remote machine
6. Log out

### Prepare ssh connection

You should only connect to the remote machines using SSH keys (as opposed to passwords).

1. If you don't have a _private_key_file_, you must generate it with the
   `ssh-keygen` command (on your own computer).
2. Copy your public key into the remote machine with `ssh-copy-id user@host`
   where `user` is your username and `host` is the hostname of the remote machine.

## Defining an Inventory

Ansible is a tool that performs a defined set of actions (composed into
_playbooks_) on remote machines defined in an _inventory_. We use two inventory
files: one for the [_staging_](hosts/staging) server, one for the
[_production_](hosts/staging). If you want to connect to one of them, perform
the following steps:

1. Edit _hostfile_ (an inventory file like `production` or `staging`) in _hosts_
   directory. Add the path to your ssh _private_key_file_.
2. If necessary, change other variables with your data.
   **Glossary**:
   - `ansible_user` — username on remote machine
   - `ansible_host` — ip or public hostname of remote machine
   - `ansible_port` — ssh port
   - `deploy_user` — special user which will be created for our development
   - `deploy_version` — name of branch from **projektzapisy** repository
   - `deploy_server_name` — domain pointing to the remote machine
3. Make sure that all the variables in
   [`hosts/group_vars/all`](hosts/group_vars/all) have desired values. Some
   variables are stored in our repository encrypted. If you wish to make use of
   them, make sure, you have the password ([see more](#encrypted-variables)).

### Configure the remote machine

In this step you will install and configure all the necessary packages on your
remote machine. This can also be used when your configuration should be updated.
Run this command in _infra_ directory:

```
ansible-playbook playbooks/configure.yml -i hosts/hostfile
```

### Update configuration with your own OpenSSL certificates

After running the `configure.yml` playbook, self-signed OpenSSL certificates
has been created on the remote machine. To replace these files with your
certificates:

1. Place your OpenSSL private key in the _playbooks/ssl_ folder and rename it as
   `zapisy.key`.
2. Place your OpenSSL certificate file in the _playbooks/ssl_ folder and rename
   it as `zapisy.crt`.
3. Run this command:
   ```
   ansible-playbook playbooks/update_ssl.yml -i hosts/hostfile
   ```

## Deployment

Deployment is an action of sending and running a new version of the application
(System Zapisy in our case) on the remote machine. Deployment can be started
automatically e.g by GitHub Actions. To start deployment by hand, run this
command in _infra_ directory:

```
ansible-playbook playbooks/deploy.yml -i hosts/hostfile
```

## Restore database

To restore the database, put the dump file into the `dump.7z` archive in _playbooks_ directory and run this command:

```
ansible-playbook playbooks/restore_db.yml -i hosts/hostfile
```

## Other Notes

### Debugging

To display additional information during configuration, deployment, or restoring
database add the flag `-vvv` to ansible-playbook commands and set environment
variable `ANSIBLE_STDOUT_CALLBACK=debug` for more readable output.

Logs are stored in the _logs_ folder in every deployment release. All releases
can be found in `/home/deploy_user/deploy/releases` directory on the remote
machine, where `deploy_user` is the value defined in the inventory file.

Other useful commands to use on the remote machine:

- `journalctl -xe` — shows the latest logs from all services.
- `journalctl -u example.service -fe` — shows and follows the latest logs from
  example service.
- `systemctl status example.service` — shows the status of example service.

### Encrypted variables

System Zapisy uses some number of external services which all require some form
of authentication. The necessary credentials for this authentication are listed
in [`hosts/group_vars/all`](hosts/group_vars/all) but are (obviously) not stored
there.

Instead we store them password-encrypted (using [_Ansible
Vault_](https://docs.ansible.com/ansible/latest/user_guide/vault.html)) in file
[`hosts/group_vars/vault`](hosts/group_vars/vault). All hosts in `vault` group
(which applies to both _staging_ and _production_—but not _example_) will
override placeholders from `hosts/group_vars/all` with these encrypted values
(so using them will require the password; [use `--ask-vault-pass` or
`--vault-password-file` when running
playbooks](https://docs.ansible.com/ansible/latest/user_guide/vault.html#using-encrypted-variables-and-files)).

## Example

To test deployment locally (using a virtual machine) follow the instructions
below.

1. Install VirtualBox and Vagrant.
2. Run `vagrant up` command in the _hosts_ directory.
3. Run these commands in turn in the _infra_ directory:
   ```
   ansible-playbook playbooks/configure.yml -i hosts/example
   ansible-playbook playbooks/deploy.yml -i hosts/example
   ```
4. Check the [192.168.33.10](http://192.168.33.10/) address in your web
   browser.
