

# CPSC 558 - Final Project (Just Some Tests)

This repo is just for testing and experiments. This is not the "real" final project repo.

## Installation

### Mininet

Mininet seems to be configured for only Python2 by default, and doesn't build correctly on Ubuntu 19.

We also needed to use Python 3 to get Ryu working properly.

Therefore, Mininet shouldn't be installed from repos, but instead built from scratch on Ubuntu 16.

#### Installation on Ubuntu 16.04

Mininet has problems building on newer versions of Ubuntu, so it is my hope an older version of Ubuntu would work instead.

* Create fresh installation of Ubuntu 16.04 inside VirtualBox
    * Make sure to set bridged networking or some mode so the VM can pull updates, and is visible by your machine
    * Probably want to create the machine on an SSD so updates/config don't take forever (or at least the VDI file)

* Install, Start SSH daemon, Add SSH key
    * ```sudo apt install openssh-server -y && sudo systemctl start sshd```
    * Add your SSH key to the root account's authorized_keys file to avoid entering your password

* Open a terminal in this repo
    * Set/export the environment variable UBUNTU_VM_HOST to point to the VM's IP or hostname
    * Execute the make recipie ```make setup-ubuntu-vm```





