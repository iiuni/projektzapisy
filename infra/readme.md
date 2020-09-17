# System Zapisów Deployment

This manual will allow you to configure the remote machine with the Ubuntu system and deploy System Zapisów on it.

## Setting up the machine

Every admin has his own account with no-password sudo privileges on the remote machine. For security, the admin has to use public-key authentication to log in to the server.

### Change sudo configuration on the remote machine

1. Log in into remote machine with `ssh`

__For the first time:__

2. Open *sudoers* file with `sudo visudo` command
3. Add following line to the end of the file:\
`%adm ALL=(ALL:ALL) NOPASSWD: ALL`
4. Save changes

__Each time:__

5. Add your user to the `adm` group:\
`sudo usermod -a -G adm username`\
where `username` is your username on the remote machine
6. Log out


### Prepare ssh connection

1. If you don't have *private_key_file*, you must generate it with the `ssh-keygen` command (on your own machine).
2. Copy your public key into the remote machine with `ssh-copy-id user@host`\
where `user` is your username and `host` is your hostname on the remote host.
3. Edit *production* or/and *staging* file in *hosts* directory. Add the path to your ssh *private_key_file*.
4. If it's necessary, change other variables with your data. \
	Dictionary:
	- `ansible_user` - username of user on remote machine
	- `ansible_host` - address ip or public hostname of remote machine
	- `ansible_port` - ssh port
	- `deploy_user` - special user what will be created for our development
	- `deploy_version` - name of branch from __projektzapisy__ repository
	- `deploy_server_name` - name of domain what points on remote machine
	- `rollbar_token` - *post_server_item* token from Rollbar settings or __none__ value
	- `newrelic_license_key` - New Relic license key used for the monitoring agent.
5. To add another server to deployment edit your hosts (*staging*/*production*) like this:

```
[deploy:children]
server1
server2

[deploy:vars]
deploy_env=staging

[server1]
webserver1

[server2]
webserver2

[server1:vars]
ansible_host=examplezapisy.pl
ansible_port=22
ansible_user=install
ansible_ssh_private_key_file=/home/bart/.ssh/id_rsa
deploy_user=zapisy
deploy_version=master-dev
deploy_server_name=examplezapisy.pl
rollbar_token=none

[server2:vars]
ansible_host=secondexamplezapisy.pl
ansible_port=22
ansible_user=alice
ansible_ssh_private_key_file=/home/bart/.ssh/id_rsa
deploy_user=zapisy
deploy_version=master
deploy_server_name=secondexamplezapisy.pl
rollbar_token=893748923424832894234234
```
 Configuration/deployment/restoring starts on every machine from the inventory file that is in the `deploy:children` section.

### Configure the remote machine

1. Edit `.env` file in *playbooks* directory. Replace these fields with correct values:
`DROPBOX_OAUTH2_TOKEN`, `SLACK_TOKEN`, `SLACK_CHANNEL_ID` (id of channel where slackbot will push notifications), `SCHEDULER_USERNAME`, `SCHEDULER_PASSWORD`, `VOTING_RESULTS_SPREADSHEET_ID`, `CLASS_ASSIGNMENT_SPREADSHEET_ID`, `EMPLOYEES_SPREADSHEET_ID` and all fields with __GDRIVE\___ prefix.

2. Run this command in *infra* directory:\
`ansible-playbook playbooks/configure.yml -i hosts/hostfile -T 60 -c paramiko` \
where `hostfile` is inventory file like *staging* or *production*

### Update configuration with your own OpenSSL certificates
After run `configure.yml` playbook, self-signed OpenSSL certificates will be created on the remote machine. To replace these files with your certificates:
1. Place your OpenSSL private key in the *playbooks/ssl* folder and rename it as `zapisy.key`.
2. Place your OpenSSL certificate file in the *playbooks/ssl* folder and rename it as `zapisy.crt`.
3. Place your DH parameters file (`dhparam.pem`) in the *playbooks/ssl* directory.
4. Run this command: \
	`ansible-playbook playbooks/update_ssl.yml -i hosts/hostfile -T 60 -c paramiko`\
	where `hostfile` is inventory file like *staging* or *production*

## Deployment

Deployment can be started automatically e.g by GitHub Actions.

To start deployment by hand, run this command in *infra* directory:
```
ansible-playbook playbooks/deploy.yml -i hosts/hostfile -T 60 -c paramiko
```
where `hostfile` is inventory file like *staging* or *production*

## Restore database

To restore the database, put the dump file into the `dump.7z` archive in *playbooks* directory and run this command:
```
ansible-playbook playbooks/restore_db.yml -i hosts/hostfile -T 60 -c paramiko
```
where `hostfile` is inventory file like *staging* or *production*


## Debugging
To display additional information during configuration, deployment, or restoring database add the flag `-vvv` to ansible-playbook commands and set environment variable `ANSIBLE_STDOUT_CALLBACK=debug` to more readable output.

Logs are stored in the *logs* folder in every deployment release. All releases can be found in `/home/deploy_user/deploy/releases` directory on the remote machine, where `deploy_user` is value from inventory file.

Other useful commands for use on the remote machine:
- `journalctl -xe` - shows the latest logs from all services
- `journalctl -u example.service -fe`- shows and follows the latest logs from example service
- `systemctl status example.service` - shows the status of example service


## Example
To test deployment on your machine follow the instructions below.

1. Install VirtualBox and Vagrant.
2. Run `vagrant up` command in the *hosts* directory.
3. Run these commands in turn in the *infra* directory:
	- `ansible-playbook playbooks/configure.yml -i hosts/example -T 60 -c paramiko`
	- `ansible-playbook playbooks/deploy.yml -i hosts/example -T 60 -c paramiko`
4. Check the [192.168.33.10](http://192.168.33.10/) address in your web browser.
