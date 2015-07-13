# depot-pm

a pacakge manager helps you to install packages from multiple package managers quickly



## Installation

```shell
pip install -U depot-pm
```



## Usage

* check version

```shell
depot-pm version
```



* install packages

```bash
depot-pm install [package-file]
```

By default, depot-pm will find ```depot.yaml``` or ```depot.json``` from current working directory.
if depot-pm could not find these config files at currnet working directory, it will find in upper directory
until it reaches ```/```.



## Congif file (depoy.yaml)

Check the sample file in source root (depot.yaml)


### Packages

It should contains at least one section: ```pacakges```. The packages section is a dictionary which
uses **installer name** as its key and **packages ot be installed** as value. (a list). So if you want to
use ```pip``` to install ```django 1.7``` and ```boto```, you should type:

```yaml
packages:
  pip:
    - django==1.7
    - boto
```

So the sample file (depoy.yaml) will produce following commands on OS X (which uses ```brew``` but not ```yum```):
```shell
which python3 1>/dev/null 2>&1 || brew install python3
brew install youtube-dl
pip install taskr boto
gem install cocoapods
npm install -g less
```
Note that it will check whether python3 exists or not before installing python 3.

and following on CentOS (uses ```yum```):
```shell
sudo yum install -y wget
pip install taskr boto
gem install cocoapods
npm install -g less
```

The format of package name could be any acceptable form of each installers.


### Installers

The ```installers``` section defines an installer. Installer configurations has following keys:

Key | Description | Default Value
----|-------------|---------------
sudo | boolean flag indicating wheather this installer should run with sudo command   | False
os | boolean flag indicating this installer is an OS specific installer which be run before other installers. (non OS specific ones) | False
multiple | the installer could install multiple packages at ones | True
syntax | the template to generate command. Use [python's string format syntax](https://docs.python.org/3/library/string.html#formatspec) | {} install {}
command | the command name of this installer | {INSTALLER_NAME}

Currenty we have:

Installers | Config
-----------|--------
pip        | {DEFAULT}
pip3       | {DEFAULT}
gem        | {DEFAULT}
npm        | {DEFAULT} but ```syntax``` is ```{} install -g {}```
brew       | {DEFAULE} but ```os``` is changed to ```true```
yum        | {DEFAULE} but ```os``` and ```sudo``` are changed to ```true```. ```syntax``` is ```{} install -y {}```



## Contact

Use the issue tracker to contact me :smile:



## TODO

* check package.json, requirements.txt, and other package file support.
