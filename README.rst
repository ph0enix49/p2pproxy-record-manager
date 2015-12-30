# p2pproxy-record-manager
App to manage record settings for p2pproxy https://github.com/const586/p2pproxy

Web application with a frontend to add/edit/remove recording schedules. 

Features:
* Choose a channel to record by specifying date and time.
* Get the list of channels and EPG for each channel.
* Select a program to record by clicking a button in EPG view.
* Displays P2P Proxy status.
* Review past, ongoing and scheduled recordings.

Installation
============
This application could be installed inside a virtual environment or systemwide.

To install in a virtual environment or systemwide using pip:
* Ensure you have a virtualenvwrapper package installed (virtual env option)
* Create a virtualenv (optional but recommended):
    mkvirtualenv record-manager
* Install:
  from repo:
    pip install git+https://github.com/ph0enix49/p2pproxy-record-manager.git
  from tarball:
    pip install p2pproxy-record-manager-<version>.tar.gz
  from locally cloned repo:
    pip install .
* You may need to prepend "sudo" if you are installing systemwide
    
To install systemwide via python setup:
* Clone this repo from github:
    git clone https://github.com/ph0enix49/p2pproxy-record-manager.git
* Or download a tarball and unpack.
* Install:
    sudo python setup.py
    
You can also configure upstart to launch the application upon boot. Copy
contrib/record-manager to /etc/init and modify parameters as required. It
is recommended that you launch the application manually to test all parameters
before configuring upstart.