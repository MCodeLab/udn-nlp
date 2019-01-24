#! /bin/bash

reinstall(){
    # reinstall the modules
    sudo python3 setup.py install
}

runscript(){
    # run a script using the version of the modules currently installed on the system
    python3 scripts/$1.py ${@:2}
}

dev_runscript(){
    # For use when working on the util modules and nlp scripts at the same time.
    # This function ensures that the latest version of the modules is installed
    # before running the desired script.
    reinstall
    runscript $@
}