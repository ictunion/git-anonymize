#!/usr/bin/env python3

import git_filter_repo
import tomli
import argparse
from argparse import RawTextHelpFormatter
import sys
import os
import subprocess
import re

# Configure command line argument parser

def build_parser():
    parser = argparse.ArgumentParser(
        formatter_class=RawTextHelpFormatter,
        prog="git-anonymize",
        description="Anonymize git history",
        epilog='''
            Developed by volunteers from `Odborová organizace pracujících v ICT`.
            The sectorial union of workers in IT & communications.
            See: http://ictunion.cz
        '''
    )

    parser.add_argument("repository", help="path to git repository to alter")
    parser.add_argument("-c", "--config", default="public-commiters.toml", help="path to configuration toml file")
    parser.add_argument("-o", "--output", default="anonymized", help="path to location where altered repository should be created")
    parser.add_argument("-n", "--name", default="Annonymous", help="name to use instead in commits")
    parser.add_argument("-e", "--email", default="anyone@world.org", help="email to use instead in commits")
    return parser

def read_config(path):
    conf = {};

    try:
        with open(path, "rb") as f:
            conf = tomli.load(f)
    except FileNotFoundError:
        sys.stderr.write("Allow config not found - anonymizing everyting")

    allowed_emails = set()
    allowed_names = set()

    for key in conf:
        value = conf[key];
        allowed_emails.add(str.encode(value["email"]))
        allowed_names.add(str.encode(value["name"]))

    return {
        "allowed_emails": allowed_emails,
        "allowed_names": allowed_names
    }

def setup_target(target):
    # Ensure existance of the output directiory
    os.makedirs(target, exist_ok=True)
    # Initialize git in target
    subprocess.call(["git", "init"], cwd=target)


def rewrite_history(args, allowed_emails, allowed_names):
    default_name = str.encode(args.name)
    default_email = str.encode(args.email)

    def name_callback(name):
        if name in allowed_names:
            return name
        else:
            return default_name

    def email_callback(email):
        if email in allowed_emails:
            return email
        else:
            return default_email

    def message_callback(message):
        message_str = message.decode()
        out = ""
        for line in message_str.split('\n'):
            if not line.startswith('Co-authored-by'):
                out = out + line + '\n'
            else:
                out = out + '[anonymized]\n'

        return str.encode(out)

    # Args deduced from:
    filter_args = git_filter_repo.FilteringOptions.default_options()
    filter_args.force = True
    filter_args.partial = True
    filter_args.refs = ['HEAD']
    filter_args.repack=False
    filter_args.replace_refs='update-no-add'
    filter_args.source=str.encode(args.repository)
    filter_args.target=str.encode(args.output)

    git_filter_repo.RepoFilter(
        filter_args,
        email_callback=email_callback,
        name_callback=name_callback,
        message_callback=message_callback,
    ).run()

def main():
    args = build_parser().parse_args()
    conf = read_config(args.config)

    # Ensure output dir
    # unless source repository and target output are the same
    # if they are same we do dangerous in place change
    if args.repository != args.output:
        setup_target(args.output)
    else:
        sys.stderr.write("Source repository and output repository are the same! Changing in place")

    rewrite_history(args, conf["allowed_emails"], conf["allowed_names"])

if __name__ == "__main__":
    main()
