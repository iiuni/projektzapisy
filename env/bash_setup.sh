echo "alias prepare-env='source /home/vagrant/env2.6/bin/activate'" >> .bash_aliases
echo "alias get-settings='cp /vagrant/env/settings_local.py .'" >> .bash_aliases
echo "alias reset-database='sudo su - postgres -c \"psql -f reset_zapisy.sql\"'" >> .bash_aliases
echo "alias load-database='sudo su - postgres -c \"psql -f /vagrant/a_dump_20160301.sql fereol\"'" >> .bash_aliases

echo "source /home/vagrant/env2.6/bin/activate" >> .bashrc
