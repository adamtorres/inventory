# Raspberry Pi Hosted Inventory Site

## Installing Ansible Requirements

Create a python virtual environment from which to run ansible.

```
# venv
python -m venv something something.

# pyenv
pyenv virtualenv --copies 3.10.1 scp-inventory-ansible
pyenv local scp-inventory-ansible
```

Install the python requirements via `pip`.  Might take a while for the first run.  This ansible environment should be usable for other projects as there's (currently) nothing specific to the inventory project loaded into the environment.

```
pip install pip --upgrade
pip install -r requirements.txt
```

Roles and collections need to be installed separately via `ansible-galaxy`.  To install the roles, use the following.

```
ansible-galaxy role install -r requirements.yml
```


The first install of the roles might take some time depending on what gets added to the requirements and show output similar to the following.  At the moment, and on a laptop, the process took just a few seconds.

```
Starting galaxy role install process
- downloading role 'postgresql', owned by geerlingguy
- downloading role from https://github.com/geerlingguy/ansible-role-postgresql/archive/3.2.1.tar.gz
- extracting geerlingguy.postgresql to /Users/adam/SeniorCenterProjects/inventory/v3/ansible/playbooks/roles/geerlingguy.postgresql
- geerlingguy.postgresql (3.2.1) was installed successfully
```

If, when running the above, you get a warning like the following, add '--force' to the command.

```
[WARNING]: - geerlingguy.postgresql (2.2.1) is already installed - use --force to change version to 3.2.1
```

After installing them, running this again will show the roles are already installed.

```
Starting galaxy role install process
- geerlingguy.postgresql (2.2.1) is already installed, skipping.
```

Installing the collections just needs a word change.  The initial install takes a bit.  Took about a minute for this example.

```
ansible-galaxy collection install -r requirements.yml
```

The first install will show output similar to the following.

```
Process install dependency map
Starting collection install process
Installing 'community.general:1.2.0' to '/Users/adam/.ansible/collections/ansible_collections/community/general'
Installing 'google.cloud:1.0.1' to '/Users/adam/.ansible/collections/ansible_collections/google/cloud'
Skipping 'ansible.posix' as it is already installed
Installing 'ansible.netcommon:1.4.1' to '/Users/adam/.ansible/collections/ansible_collections/ansible/netcommon'
Installing 'community.kubernetes:1.1.1' to '/Users/adam/.ansible/collections/ansible_collections/community/kubernetes'
```

Subsequent runs will finish quickly.

```
Process install dependency map
Starting collection install process
Skipping 'community.general' as it is already installed
```

## Testing ansible

There is a 'hello world' playbook that does nothing much other than make sure ansible is functional.

```
ansible-playbook playbooks/hello_world.yml
```

Should produce the following output.

```
[WARNING]: No inventory was parsed, only implicit localhost is available
[WARNING]: provided hosts list is empty, only localhost is available. Note that the implicit localhost does not match 'all'

PLAY [localhost] *********************************************************************************************************************************************************

TASK [Gathering Facts] ***************************************************************************************************************************************************
ok: [localhost]

TASK [shell] *************************************************************************************************************************************************************
changed: [localhost]

PLAY RECAP ***************************************************************************************************************************************************************
localhost                  : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

## Secrets

### Ansible Vault

This accepts input from stdin and creates a vaulted value to include in variable files.  The name of the variable seems to be included in the encryption.  The following assumes there is a line in `vault.txt` with `base_server *********` where the asterisks are some really strong password and definitely not `12345`.  Just a heads up, decrypting seems to be dependent on the vault file not changing.  I've had issues adding a line to the vault file and existing vaulted strings start throwing decryption errors.

```
adam@Adams-MacBook-Air: ansible-vault encrypt_string --vault-id base_server@vault.txt --stdin-name 'pi_priv_key'
Reading plaintext input from stdin. (ctrl-d to end input, twice if your content does not already have a newline)
hello world
pi_priv_key: !vault |
          $ANSIBLE_VAULT;1.2;AES256;base_server
          66396165643462353930626532373032323537373361346332623031323930356634343466303138
          3066623839376634663538366563656166353565386231360a363963393239316630336130383064
          65383535343265643734613437656136636433633234313035326231313732376436656135353535
          3035373432326434650a356261656364373562373964626534383636366665316337633232376365
          6262
```


## Deploy everything

This should be repeatable without damaging anything.  That's the whole point behind Ansible, really.  Not specifying any tags will ignore the tags except for those with 'never'.  Add `--list-tasks` so see which tasks are run and in which order.

```
ansible-playbook --vault-password-file vault.txt -i inventory_pi site.yml
```


## Updating the a service with new code

Making code changes and deploying those changes follows these steps.

1. Make the changes on development system.
2. Commit changes to repo.
3. Push changes to git host.
4. Run ansible command to deploy.

```
ansible-playbook --vault-password-file vault.txt -i inventory_pi update_site.yml
```

## Loading data via Ansible

Loading data is done with the `inventory_app_process_items.yml` playbook.  This calls the `inventory_app` role with the `process_items` var defined `True`.  This tells the role to run a series of manage commands to process items and load data from the specified files.  This will not successfully load all data as a couple spots wouldput a hold on some records for bad prices, quantities, or unit sizes.  After fixing those issues (currently, a very manual process), running this command again without the files will pick up any unprocessed records.

Note: Relative paths search from playbooks folder and further in that tree.  Not from root of ansible project.

The following command truncates data, uploads data files, and runs the processing steps.  It uses JSON for the extra-vars so `remove_data` can be a proper True/False instead of a string.

```
ansible-playbook --vault-password-file vault.txt -i inventory_pi \
  --extra-vars '{"incoming_data_file": "../../../invoices/incoming-2022-03-31.tsv", "common_item_names_data_file": "../../../invoices/common_names-2022-03-31.tsv", "remove_data": True}' \
  playbooks/inventory_app_process_items.yml
```

If there are any unit sizes listed during the `Show unit_size issues after cleaning` task, check them over.

Force cleaning of records which have unrecognized unit sizes.  This has to be done on the pi at the moment.

```
. /srv/venv.inventory_app/bin/activate
./manage.py shell_plus --quiet -c "ia.do_clean(allow_new_units=True)"
```

After any issues are cleared up, run the processing steps without uploading any files.

```
ansible-playbook --vault-password-file vault.txt -i inventory_pi playbooks/inventory_app_process_items.yml
```

## Checking service status

The `base_server` role starts two scripts to give quick status reports on the various services.  Each role added to a given server adds its own content to these scripts.  The `short` version gives one line per service while the `detailed` version shows quite a lot.

### Short service status

```
ansible-playbook --vault-password-file vault.txt -i inventory_pi playbooks/service_status.yml
```

In the middle of the output will be a chunk similar to the following.  The main purpose of this form is a simple check for `active`/`inactive`.

```
TASK [service_status : Show short service status] ************************************************************************************************************************
ok: [pi-bb131f] =>
  stdout_short_service_status.stdout: |-
    ====================================================================================
    Service status 2022-04-10 23:15:09
    active - postgresql@13-main
    active - inventory_app_http
    active - nginx
```

### Detailed service status

If you need more information because something isn't working properly, the detailed status might help.  To get the detailed version, the `status_type` variable needs to change.

```
ansible-playbook --vault-password-file vault.txt -i inventory_pi playbooks/service_status.yml --extra-vars="status_type=detailed"
```

Detailed output can get long so this example output only shows one service.  Currently, this is simply the output from `systemctl status --no-pager <service name>`.  Details included:

* service file (contains starting and stopping details)
* active/inactive
* when started
* uptime
* pid
* command line
* recent log entries

```
  stdout_detailed_service_status.stdout: |-
    ====================================================================================
    Service status 2022-04-10 23:14:29
    ------- postgresql@13-main ------- postgresql@13-main ------- postgresql@13-main -------
     postgresql@13-main.service - PostgreSQL Cluster 13-main
         Loaded: loaded (/lib/systemd/system/postgresql@.service; enabled-runtime; vendor preset: enabled)
         Active: active (running) since Sat 2022-04-09 11:49:15 MDT; 1 day 11h ago
       Main PID: 44279 (postgres)
          Tasks: 7 (limit: 8985)
            CPU: 4min 25.417s
         CGroup: /system.slice/system-postgresql.slice/postgresql@13-main.service
                 44279 /usr/lib/postgresql/13/bin/postgres -D /var/lib/postgresql/13/main -c config_file=/etc/postgresql/13/main/postgresql.conf
                 44281 postgres: 13/main: checkpointer
                 44282 postgres: 13/main: background writer
                 44283 postgres: 13/main: walwriter
                 44284 postgres: 13/main: autovacuum launcher
                 44285 postgres: 13/main: stats collector
                 44286 postgres: 13/main: logical replication launcher

    Apr 09 11:49:13 pi-bb131f systemd[1]: Starting PostgreSQL Cluster 13-main...
    Apr 09 11:49:15 pi-bb131f systemd[1]: Started PostgreSQL Cluster 13-main.
    ------------------------------------------------------------------------------
```
