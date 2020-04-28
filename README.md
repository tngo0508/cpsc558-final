

# CPSC 558 - Final Project

Our final project repo. Woot.

* Mike Peralta mikeperalta@csu.fullerton.edu
* Thomas Ngo tngo0508@csu.fullerton.edu

## Professor Instructions

First, you can use the command ```make``` in the root of this repo for a list of commands that GNU Make will help you run.

Essentially, you'd need to go through the following steps:

1. Setup a fresh Ubuntu 16.04 VM (Sorry !!!)
2. You already made sure the VM can reach the internet in Step 1; Also make sure the host can reach the VM (we used bridged mode)
3. Setup the root account's password or SSH key so the user on your current machine can SSH into the VM using the root user
4. Set the environment variable UBUNTU_VM_HOST to the IP address or hostname of your Ubuntu 16 VM
    (you'll see Make mention the value it's reading)
5. Open a terminal and execute ```$ make``` to see a list of available make shortcuts
6. Instruct the Ubuntu 16 VM to install updates and build Mininet from source for Python 3 with:

    ```bash
    $ make setup-ubuntu-vm

   ```

7. Wait endlessly. Maybe watch a show or call a friend.

8. Run the topology test with:

    ```$ make topo```
    
    You should see a message upon success, and a png render of the topology at "repo/render/topology.png"

8. Run all other tests with:
    
    ```$ make run```
    
    You should see various outputs (hopefully) proving that our Ryu hub, switch, and QoS switch seem to be working.
    
    Also you'll [TODO: describe log output that proves success]

## General Notes

### Mininet

Mininet seems to be configured for only Python2 by default, and doesn't build correctly on Ubuntu 19.

We also needed to use Python 3 to get Ryu working properly.

Therefore, Mininet shouldn't be installed from repos, but instead built from scratch on Ubuntu 16.

#### Installation on Ubuntu 16.04

Mininet has problems building on newer versions of Ubuntu,
    so we used Ubuntu 16.04.
A basic procedure is as follows:

* Create fresh installation of Ubuntu 16.04 inside VirtualBox
    * Make sure to set bridged networking or some mode so the VM can pull updates, and is visible by your machine
    * Probably want to create the machine on an SSD so updates/config don't take forever (or at least the VDI file)
    * Probably want to use VirtualBox (not KVM) so we can do a Snapshot ***just*** after updates are installed, to decrease the hassle of running installation tests over and over and over again.

* Install, Start SSH daemon, Add SSH key
    * ```$ sudo apt install openssh-server -y && sudo systemctl start sshd```
    * Add your SSH key to the root account's authorized_keys file to avoid entering your password

* Open a terminal in this repo
    * Set/export the environment variable UBUNTU_VM_HOST to point to the VM's IP or hostname
    * Execute the make recipe to setup the VM: ```make setup-ubuntu-vm```
    * Execute the make recipe to run the topology test: ```make topo```
    * Execute the make recipe to run all other tests: ```make run```





