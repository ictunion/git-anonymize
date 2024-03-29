#!/usr/bin/env python3

import git_filter_repo
import tomli
import argparse
import re
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
            See: https://ictunion.cz
        '''
    )

    parser.add_argument("repository", help="path to git repository to alter")
    parser.add_argument("-c", "--config", default="public-contributors.toml", help="path to configuration toml file")
    parser.add_argument(
        "-o", "--output", default="anonymized", help="path to location where altered repository should be created"
    )
    parser.add_argument("-n", "--name", default="Annonymous", help="name to use instead in commits")
    parser.add_argument("-e", "--email", default="anyone@world.org", help="email to use instead in commits")
    parser.add_argument(
        "-r",
        "--refs",
        default=["HEAD"],
        nargs='+',
        help="git refs (branches, tags etc.) to include in anonymized version separated by space like `-r main HEAD`"
    )
    return parser

def add_to_set(the_set, value):
    # Single value is just added
    if isinstance(value, str):
        the_set.add(str.encode(value))
    # If this is not string, lets assume it's list
    else:
        for string in value:
            # We simply recurse
            # this means we also technically support nested strings
            add_to_set(the_set, string)

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
        add_to_set(allowed_emails, value['email'])
        add_to_set(allowed_names, value['name'])

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

    # TODO: Ideally we would also respect allowed_names & allowed_emails
    # in this filtering. But regexps are kind of hard to get right so
    # we do the safer and simpler thing now and anonymize every Co-author.
    # If this would be implemented definitely in future definitely don't forget
    # to add test in test/golden.sh!
    def message_callback(message):
        # Strip github user mentions
        message_str = re.sub(r'\B@((?!.*(-){2,}.*)[a-z0-9][a-z0-9-]{0,38}[a-z0-9])', '[anonymized]', message.decode())
        out = ""
        for line in message_str.split('\n'):
            # GitHub or Git sometimes adds Co-authored-by or Signed-off-by
            # followed by email and name of the author of the commit
            # We do this to prevent leaking of identifiable information
            # from such commit messages
            if line.startswith(('Co-authored-by', 'Signed-off-by')):
                out = out + '[anonymized]\n'
            else:
                out = out + line + '\n'

        return str.encode(out)

    # Args deduced from:
    filter_args = git_filter_repo.FilteringOptions.default_options()
    filter_args.force = True
    filter_args.partial = True
    filter_args.refs = args.refs
    filter_args.repack = False
    filter_args.replace_refs = 'update-no-add'
    filter_args.source = str.encode(args.repository)
    filter_args.target = str.encode(args.output)

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
