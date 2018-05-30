#!python

"""
Filenotify watches a directory structure and notifies users about changes in each directoryself.

- Each directory has its own configuration file that contains the mailaddresses that will be notifiedself.
- Each directory also contains a manifest file that contains information about known files
- When run, the contents of the manifest file are compared to the actual files in the directory. Any differences are notified and the manifest is then updated
"""

# 17:10 - 18:10 = 1h
# 15:00 -

import os
import sys
import argparse
import logging

logger = logging.getLogger("filenotify")

class FileNotify:

    def __init__(self, base_dir, manifest_file=".MANIFEST", config_file = "mailaddresses.txt"):
        self.base_dir = os.path.realpath(base_dir)
        self.manifest_file = manifest_file
        self.config_file = config_file
        logger.debug("initialized. base_dir='{}'".format(self.base_dir))

    def read_manifest(self, manifest_dir):
        """
        parse manifest file

        returns manifest dict
        """
        pass
    def write_manifest(self, manifest_dir, manifest_dict):
        """
        write manifest of directory
        """
        pass

    def diff_manifest(self, old_manifest, new_manifest):
        """
        compare two manifest structures

        return new structure only containing new or changed files from old to new
        files with changed modification time are mentioned
        removed files are NOT mentioned
        returns {} if no changes.
        """
        pass

    def create_manifest(self, manifest_dir):
        """
        create manifest from directoryself

        returns manifest structure

        manifest structure is

           dict = {
            file_base_name: change_datetime
           }


        """
        pass

    def read_config(self,config_dir):
        """
        read directory config file

        returns configfileparser instance

        config file structure:

        text file with one email address per line.
        lines containing # are ignored
        lines not containing @ are ignored
        """

        file = os.path.join(config_dir, self.config_file)
        mailaddresses = []

        with open(file) as f:
            lines = f.readlines()

        for line in lines:
            line.strip()
            
            if "#" in line:
                next
            if not "@" in line:
                next
            mailaddresses.append(line)
        pass

    def notify(self, mailadresses=[], changes=[]):
        """
        send mail about changed files
        """
        pass

    def run(self):
        """
        run filenotify and scoop directories

        - directories that do not contain a config file are ignored
        - directories and files starting with '.' are ignored
        """
        logger.info("scanning directories...")
        for root, subdirs, files in os.walk(self.base_dir):
            base_name = os.path.basename(root)
            logger.debug("inside {}".format(root))

            # ignore dot dirs
            if base_name.startswith('.'):
                logger.info("ignoring directory {}".format(base_name))
                continue

            # look for configfile, else bail out
            if not self.config_file in files:
                logger.info("no '{}' in '{}', ignoring directory".format(self.config_file, base_name))

            # read manifest and create new manifest
            manifest = self.read_manifest(root)
            new_manifest = self.create_manifest(root, manifest)

            # compare
            diff_manifest = self.diff_manifest(manifest, new_manifest)

            # notify and write new manifest if there are differences
            self.notify(root, diff_manifest)
            self.write_manifest(root, new_manifest)

def cmdline(args):
    """
    parse commandline

    returns parser instance
    """
    pass

def main(args):
    """init a filenotify instance with command line arguments and run it"""
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.DEBUG)
    fn = FileNotify('.')
    fn.run()

if __name__ == "__main__":
    main(sys.argv)
