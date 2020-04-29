

# CPSC 558 - Final Project

Our final project repo. Woot.

* Mike Peralta mikeperalta@csu.fullerton.edu
* Thomas Ngo tngo0508@csu.fullerton.edu

## Professor Instructions

First, you can use the command ```make``` in the root of this repo for a list of commands that GNU Make will help you run.

You will use your host machine to control your VM.
All changes will be made to the remote VM,
and all changes will be run there as well.
No changes or tests will be performed on your host machine.

Essentially, you'd need to go through the following steps:

1. Setup a fresh Ubuntu 16.04 VM (Sorry !!!)
2. Make sure the VM can reach the internet, and is reachable by your host machine (we used bridged mode)
3. Setup the root account's password or SSH key so the user on your current machine can SSH into the VM using the root user
4. Set the environment variable UBUNTU_VM_HOST to the IP address or hostname of your Ubuntu 16 VM
    (you'll see Make mention the value it's reading)
5. Open a terminal and execute ```$ make``` to see a list of available make shortcuts
6. Instruct the Ubuntu 16 VM to install updates and build Mininet from source for Python 3 with:

    ```bash
    $ make setup-ubuntu-vm
   ```

7. Wait endlessly. Maybe watch a show or call a friend.
    
    If you see an error similar to:
    
     ```Unable to acquire the dpkg frontend lock (/var/lib/dpkg/lock-frontend), is another process using it?```,
     
     ... your Ubuntu VM is probably still updating.

8. Run the topology test with:

    ```$ make topo```
    
    You should see a message upon success, and a png render of the topology at "repo/render/topology.png"

8. Run all other tests with:
    
    ```$ make run```
    
    You should see various outputs (hopefully) proving that our Ryu hub, switch, and QoS switch seem to be working.
    
    Also you'll [TODO: describe log output that proves success]

## General Notes

### Repo Layout

* The ***controllers*** subdirectory contains our Ryu controllers (the main point of this project)

* The ***nodes*** subdirectory contains Python classes that implement functionality of our various nodes, such as:
    * File Server and Client
    * Video Server and Client
    * The Tattle Tail node
    * Supporting base classes

* The ***scripts*** subdirectory contains misc setup scripts

Of our controllers, we have the following source files:

* *Demo_SimpleSwitch.py* is code ripped directly from a tutorial site, and used as our inspiration. This is ***not*** to be considered our original work, and will not be integrated in the final test run configuration.
* *DumbHub.py* is a controller implementing a simple hub, that merely broadcasts all packets received. Should hopefully suffer from congestion issues.
* *SimpleSwitch.py* is one step above the *DumbHub*. It will learn MAC addresses and will maintain a forwarding table that allows it to send traffic only to the most appropriate output port.
* *QSwitch.py* is one step above the *SimpleSwitch*. It will attempt to prioritize UDP packets over TCP packets.

### Explanation of tests

The tests invoked via ```make run``` are designed to prove our controllers are working as intended.
Each test will use one of the above controllers, and is named after the controller used.

* The ***DumbHub*** test should show lower aggregate bandwidth than with the SimpleSwitch test.
    * The File Server/Client nodes should appear to be splitting the bandwidth with the Video Server/Client nodes
    * There may also be a little slowdown due to congestion / collisions.
    * The Tattle Tail node should also show that it received quite a bit of broadcasted data

* The ***SimpleSwitch*** test should show higher aggregate bandwidth than with the ***DumbHub*** test.
    * The File Server/Client nodes sholud not appear to be splitting line bandwidth, but only the max aggregate bandwidth of the switch.
    * The Tattle Tail node should report very little stray broadcast data as compared with the ***DumbHub*** test.

* The ***QSwitch*** test should generally present the same as the ***SimpleSwitch*** test, with one exception:
    * The Video Server/Client nodes should show significantly more bandwidth than the File Server/Client nodes.

***TODO*** Come up with some like ... logs and stuff to prove this. Probably sort logs into folders named after tests.

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





