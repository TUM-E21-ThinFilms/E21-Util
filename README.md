# Utility library

Utility library for various purposes for the thin film laboratoy of e21 
at Technical University of Munich.

## Installation 
```shell
git clone https://github.com/TUM-E21-ThinFilms/E21-Util.git e21_util
cd e21_util/
python setup.py install
```

## Configuration

### Changing the lock path
The default path for lock files is `/etc/e21/lock/`. You can change this
parameter by setting the constant `LOCK_DIR` under `e21_util/paths.py`.  

## Usage

### Serial Connection
A serial connection can be established by
 
```python
from e21_util.serial_connection import Serial

con = Serial(path, baudrate, databits, parity, stopbits, timeout)
```

Note that every serial connection has a lock file associated to prevent 
multiple processes to access the same device at the same time. See 
`InterProcessTransportLock` for implementation details in `lock.py`


Refer to the manual of pyserial [here](https://pyserial.readthedocs.io/en/latest/shortintro.html#opening-serial-ports) for additional information on the usage 
of the `Serial` class.