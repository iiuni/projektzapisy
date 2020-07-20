# System Zapisów Deployment

## Setting up the machine

### Change sudo configuration on the remote machine

1. Log in into remote machine with `ssh`

__for the first time:__

2. Create group `zapisy-admin`: `sudo groupadd zapisy-admin`
3. Open *sudoers* file with `sudo visudo` command
4. Add following line to end of the file:\
`%zapisy-admin ALL=(ALL:ALL) NOPASSWD: ALL`
5. Save changes

__for each time:__

6. Add your user to the `zapisy-admin` group:\
`sudo usermod -a -G zapisy-admin username`\
where `username` is your username on the remote machine
8. Log out


### Prepare ssh connection

1. If you don't have *private_key_file*, you must generate it with the `ssh-keygen` command.
2. Copy your file into the remote machine with `ssh-copy-id user@host`\
where `user` is your username on the remote host and `host` is your hostname.
3. Edit *production* or/and *staging* file. Add the path to your ssh *private_key_file*.
4. If it's necessary, change other variables with your data. \
	Dictionary:
	- `ansible_user` - username of user on remote machine
	- `ansible_host` - address ip or public hostname of remote machine
	- `ansible_port` - ssh port
	- `deploy_user` - special user what will be created for our development
	- `deploy-version` - name of branch from __projektzapisy__ repository
	- `deploy_server_name` - name of domain what points on remote machine
	- `rollbar_token` - *post_server_item* token from Rollbar settings or __none__ value
5. For add another server to deployment edit your hosts (*staging*/*production*) like this:

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

1. Edit `.env` in *deploy* file. Replace these fields with correct values:
`DROPBOX_OAUTH2_TOKEN`, `SLACK_TOKEN`, `SLACK_CHANNEL_ID` (id of channel where slackbot will push notifications), `SCHEDULER_USERNAME`, `SCHEDULER_PASSWORD`, `VOTING_RESULTS_SPREADSHEET_ID`, `CLASS_ASSIGNMENT_SPREADSHEET_ID`, `EMPLOYEES_SPREADSHEET_ID` and all fields with __GDRIVE\___ prefix.

2. Run this command in *deploy* directory:\
`ansible-playbook configure.yml -i hosts -T 60 -c paramiko` \
where `hosts` is inventory file like *staging* or *production*

### Update configuration with your own OpenSSL certificates
After run `configure.yml` playbook, self-signed OpenSSL certificates will be created on the remote machine. To replace these files with your certificates:
1. Place your OpenSSL private key in the *ssl* folder and rename it as `zapisy.key`.
2. Place your OpenSSL certificate file in the *ssl* folder and rename it as `zapisy.crt`.
3. Place your DH parameters file (`dhparam.pem`) in the *ssl* directory.
4. Run this command: \
	`ansible-playbook update_ssl.yml -i hosts -T 60 -c paramiko`\
	where `hosts` is inventory file like *staging* or *production*

## Deployment

Deployment can be started automatically e.g by GitHub Actions.

To start deployment by hand, run this command in *deploy* directory:
```
ansible-playbook deploy.yml -i hosts -T 60 -c paramiko
```
where `hosts` is inventory file like *staging* or *production*

## Restore database

To restore the database, put the dump file into the `dump.7z` archive in *deploy* directory and run this command:
```
ansible-playbook restore_db.yml -i hosts -T 60 -c paramiko
```
where `hosts` is inventory file like *staging* or *production*


## Debugging
To display additional information during configuration, deployment, or restoring database add the flag `-vvv` to ansible-playbook commands.

Logs are stored in the *logs* folder in every deployment release. All releases can be found in `/home/zapisy/deploy/releases` directory.

Other useful commands:
- `journalctl -xe` - shows the latest logs from all services
- `journalctl -u example.service -fe`- shows and follows the latest logs from example service
- `systemctl status example.service` - shows the status of example service

