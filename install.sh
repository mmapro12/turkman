./build_deb.sh

sudo dpkg -i {PACKAGE_FILE}
sudo apt install -r
turkman db sync
