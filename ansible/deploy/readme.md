# Instruction - System Zapisów Deployment

### Change sudo configuration on the remote machine
1. Log in into remote machine with `ssh`
2. Open *sudoers* file with `sudo visudo` command
3. Add following line to end of the file:\
    `user ALL=(ALL:ALL) NOPASSWD: ALL`\
    where `user` is your username on the remote machine
4. Save changes
5. Log out

### Prepare ssh connection
 1. If you don't have *private_key_file*, you must generate it with `ssh-keygen` command.
 2. Copy your file into the remote machine with `ssh-copy-id user@host`\
    where `user` is your username on the remote host and `host` is your hostname.
 3. Edit *production* or/and *staging* file. Add the path to your ssh *private_key_file*.
 4. If it's necessary to change other variables with your data.
    Dictionary:
    - `ansible_user` - username of user on remote machine
    - `ansible_host` - address ip or public hostname of remote machine
    - `ansible_port` - ssh port
    - `deploy_user` - special user what will be created for our development
    - `deploy-version` - name of branch from __projektzapisy__ repository
    - `deploy_server_name` - name of domain what points on remote machine
5. For add another server to deployment edit your hosts (*staging*/*production*) like this:
```
[deploy:children]
server1
server2

[server1]
webserver

[server2]
webserver

[server1:vars]
ansible_host=examplezapisy.pl
ansible_port=22
ansible_user=install
ansible_ssh_private_key_file=/home/bart/.ssh/id_rsa
deploy_user=zapisy
deploy_version=master-dev
deploy_server_name=examplezapisy.pl

[server2:vars]
ansible_host=secondexamplezapisy.pl
ansible_port=22
ansible_user=alice
ansible_ssh_private_key_file=/home/bart/.ssh/id_rsa
deploy_user=zapisy
deploy_version=master
deploy_server_name=secondexamplezapisy.pl
```

### Configure the remote machine
1. Edit `.env` in *deploy* file. Replace these fields with correct values:
	`DROPBOX_OAUTH2_TOKEN`, `SLACK_TOKEN`, `SCHEDULER_USERNAME`, `SCHEDULER_PASSWORD`, `VOTING_RESULTS_SPREADSHEET_ID`, `CLASS_ASSIGNMENT_SPREADSHEET_ID`, `EMPLOYEES_SPREADSHEET_ID`, `GDRIVE_SERVICE_TYPE`, `GDRIVE_PROJECT_ID`, `GDRIVE_PRIVATE_KEY_ID` and `PRIVATE_KEY`

2. Run this command in *deploy* directory:
`ansible-playbook configure.yml -i hosts -T 60 -c paramiko`
### Deployment
Run this command in *deploy* directory:
```
ansible-playbook deploy.yml -i hosts -T 60 -c paramiko
```
---
`hosts` is inventory file like *staging* or *production*\
Configuration/deployment starts on every machine from the inventory file that is in `deploy:children` section.

## Restore database
To restore database, put the dump file to the `dump.7z` archive in *deploy* directory and run this command:
```
ansible-playbook restore_db.yml -i hosts -T 60 -c paramiko
```
`hosts` is inventory file like above.

## Debugging
To display additional information during configuration, deployment or restoring database add the flag `-vvv` to ansible-playbook commands.
