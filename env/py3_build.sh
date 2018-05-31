# Compile Python 3.x from source

echo "Building Python 3.6..."

apt-get install -y build-essential
apt-get install -y libssl-dev zlib1g-dev libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev
apt-get install -y libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev tk-dev

TMP_DIR=/tmp/py3-build
mkdir "$TMP_DIR"
cd "$TMP_DIR"
wget --no-verbose https://www.python.org/ftp/python/3.6.5/Python-3.6.5.tar.xz
tar xf Python-3.6.5.tar.xz
cd Python-3.6.5
# NOTICE Optimizations disabled for faster provisioning;
# if you want to enable them, you'll need to remove the -j switch from make below
./configure
make -j 8
make altinstall

cd
rm -rf "$TMP_DIR"
