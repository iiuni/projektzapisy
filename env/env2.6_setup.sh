##########################################################
# download and compile python v2.6.9
##########################################################

SRC=$HOME/src

# get python itself
cd $HOME
mkdir pythons
mkdir src
cd $SRC
wget -q https://www.python.org/ftp/python/2.6.9/Python-2.6.9.tgz
tar -zxf Python-2.6.9.tgz
rm Python-2.6.9.tgz
cd Python-2.6.9
#make distclean
export LDFLAGS="-L/usr/lib/$(dpkg-architecture -qDEB_HOST_MULTIARCH)"
./configure --prefix=$HOME/pythons/Python-2.6.9
make --silent
make install
$HOME/pythons/Python-2.6.9/bin/python setup.py install
unset LDFLAGS
#########################################################
# get pip
cd $SRC
wget -q https://bootstrap.pypa.io/get-pip.py
$HOME/pythons/Python-2.6.9/bin/python get-pip.py
#########################################################
# get virtualenv
$HOME/pythons/Python-2.6.9/bin/pip install virtualenv
#########################################################

# set up virtualenv
cd $HOME
$HOME/pythons/Python-2.6.9/bin/virtualenv env2.6
source env2.6/bin/activate
#####################

# get requirements

pip install --no-binary django -r /vagrant/env/requirements-2.6-1.4.2.txt

pip install setuptools

# get PIL
cd $SRC
wget -q http://effbot.org/downloads/Imaging-1.1.7.tar.gz
tar -zxf Imaging-1.1.7.tar.gz
cd Imaging-1.1.7
python setup.py build
python setup.py install

# get django-endless-pagination-1.1
cd $SRC
wget -q https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/django-endless-pagination/django-endless-pagination-1.1.tar.gz
tar -zxf django-endless-pagination-1.1.tar.gz
cd django-endless-pagination-1.1
python setup.py build
python setup.py install

# get vobject dependency
cd $SRC
wget -q https://labix.org/download/python-dateutil/python-dateutil-2.1.tar.gz
tar -zxf python-dateutil-2.1.tar.gz
cd python-dateutil-2.1
python setup.py build
python setup.py install

# get vobject-0.8.1c
cd $SRC
wget -q https://pypi.python.org/packages/source/v/vobject/vobject-0.8.1c.zip#md5=348062e5f33c710a192e8f76b154d0e2
unzip vobject-0.8.1c.zip
cd vobject-0.8.1c
python setup.py build
python setup.py install

# get xhtml2pdf dependency (reportlab-2.6)
cd $SRC
wget -q https://pypi.python.org/packages/source/r/reportlab/reportlab-2.6.tar.gz#md5=cdf8b87a6cf1501de1b0a8d341a217d3
tar -zxf reportlab-2.6.tar.gz
cd reportlab-2.6
python setup.py build
python setup.py install

# get xhtml2pdf-0.0.4
cd $SRC
wget -q https://pypi.python.org/packages/source/x/xhtml2pdf/xhtml2pdf-0.0.4.tar.gz#md5=36b015a4e2918460711cbc5eebe026ce
tar -zxf xhtml2pdf-0.0.4.tar.gz
cd xhtml2pdf-0.0.4
# hack for broken dependencies (we already have them -- PIL & reportlab)
sed -i 's/, "pil", "reportlab"]/]/' setup.py
python setup.py build
python setup.py install

# get lxml-3.0.1
cd $SRC
wget -q https://pypi.python.org/packages/source/l/lxml/lxml-3.0.1.tar.gz#md5=0f2b1a063ab3b6b0944cbc4a9a85dcfa
tar -zxf lxml-3.0.1.tar.gz
cd lxml-3.0.1
python setup.py build
python setup.py install


echo "Python-2.6 environment set up."
