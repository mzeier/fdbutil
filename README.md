# fdbutil

## Description

fdbutil is a general use utility for controlling and manipulating foundationdb.  It will start as a method for identifying missing
fdb processes but will grow to other functions such as killing processes, identifying live but "stuck" processes.

## Usage

### Top level help
```
$ ./fdbutil.py --help
usage: fdbutil.py [-h] [-t TIER] [-d CONFDIR] [-s SUFFIX] [-c CONF]
                  {missing} ...

utility for fdb process management

optional arguments:
  -h, --help            show this help message and exit
  -t TIER, --tier TIER  fdb tier to query. Default: ssd
  -d CONFDIR, --confdir CONFDIR
                        directory containing fdb configuration files. Default: /etc/foundationdb
  -s SUFFIX, --suffix SUFFIX
                        suffix for cluster configuration files. Default: .cluster
  -c CONF, --conf CONF  foundationdb server configuration file. Default: foundationdb.conf

subcommands:
  {missing}             available subcommands. use <subcommand> --help for usage
    missing             for detecting missing processes
```

## Subcommands

### `missing`

This subcommand identifies missing processes across one or all tiers.

#### Usage
```
$ ./fdbutil.py missing --help
usage: fdbutil.py missing [-h] [-m]

optional arguments:
  -h, --help     show this help message and exit
  -m, --metrics  output format as a json metric with the tier as a point tag
  ```
#### Examples

```
$ ./fdbutil.py --tier all missing
missing processes for ssd tier: None
missing processes for memory tier: 4613, 4653
```

```
$ ./fdbutil.py --tier memory missing --metrics | jq .
[
  {
    "4600": 0,
    "4601": 0,
    "4602": 0,
    "4603": 0,
    "4604": 0,
    "4605": 0,
    "4606": 0,
    "4607": 0,
    "4608": 0,
    "4609": 0,
    "4610": 0,
    "4611": 0,
    "4612": 0,
    "4613": 1,
    "4614": 0,
    "4615": 0,
    "4650": 0,
    "4651": 0,
    "4652": 0,
    "4653": 1,
    "4654": 0,
    "4655": 0,
    "4656": 0,
    "4657": 0,
    "tier": "memory"
  }
]
```
