# set up virtualenv
cd $HOME
virtualenv -p python3 env3.5
source env3.5/bin/activate

# get requirements
pip install -r /vagrant/zapisy/requirements.development.txt

echo "Python-3.5 environment has been set up."
