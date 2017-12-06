
# set up virtualenv
cd $HOME
virtualenv env2.7
source env2.7/bin/activate

# get requirements
pip install -r /vagrant/zapisy/requirements.development.txt

echo "Python-2.7 environment has been set up."
