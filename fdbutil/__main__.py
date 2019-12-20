#!/usr/bin/env python3

import argparse
import sys
from fdbutil.fdbutil import FdbUtil


def parse_args():
    """ Standard arg parsing """

    parser = argparse.ArgumentParser(
        description="utility for fdb process management",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-d",
        "--confdir",
        default="/etc/foundationdb",
        help="directory containing fdb configuration files. Default: %(default)s",
    )
    parser.add_argument(
        "-s",
        "--suffix",
        default=".cluster",
        help="suffix for cluster configuration files. Default: %(default)s",
    )
    parser.add_argument(
        "-t", "--tier", default="ssd", help="fdb tier to query. Default: %(default)s",
    )

    # TODO: arg for host, will default to localhost for now

    subparsers = parser.add_subparsers(
        dest="subcommand",
        title="subcommands",
        help="available subcommands. use <subcommand> --help for usage",
    )

    missing_parser = subparsers.add_parser(
        "missing", help="for detecting missing processes"
    )
    missing_parser.add_argument(
        "-m",
        "--metrics",
        action="store_true",
        help="output format as a json metric with the tier as a point tag",
    )

    # This code will be implemented soon.
    # kill_parser = subparsers.add_parser(
    #     "kill", help="for killing one or more processes"
    # )
    # kill_parser.add_argument(
    #     "process", action="store", help="process or processtype to kill"
    # )

    args = parser.parse_args()

    if args.subcommand is None:
        parser.print_help()
        sys.exit(0)
    else:
        return args


def main():
    """ main function to call when invoking the script """

    args = parse_args()

    futil = FdbUtil(args)

    # call the method named after the subcommand
    getattr(futil, args.subcommand)(args)


if __name__ == "__main__":
    main()
