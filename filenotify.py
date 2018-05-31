#!python

"""
Filenotify watches a directory structure and notifies users about changes in each directoryself.

- Each directory has its own configuration file that contains the mailaddresses that will be notifiedself.
- Each directory also contains a manifest file that contains information about known files
- When run, the contents of the manifest file are compared to the actual files in the directory. Any differences are notified and the manifest is then updated
"""

# 17:10 - 18:10 = 1h
# 15:00 - 16:30 = 1.5h

import os
import sys
import time
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
        if no manifest file in dir, returns {}

        manifest file format:
        <file_base_name>;<file_date_time_string>
        """

        manifest_file = os.path.join(manifest_dir, self.manifest_file)
        if not os.path.exists(manifest_file):
            logger.debug("no manifest file: {}".format(manifest_file))
            return {}
        with open(manifest_file) as f:
            lines = f.readlines()

        manifest = {}
        for line in lines:
            if not line:
                continue
            (base, date) = line.split(';',1)
            manifest[base]=date
        logger.debug("read manifest from {}: {}".format(manifest_file,manifest))
        return manifest

    def write_manifest(self, manifest_dir, manifest_dict):
        """
        write manifest of directory
        """
        # do not write if no files
        manifest_file = os.path.join(manifest_dir, self.manifest_file)
        if not manifest_dict:
            return

        with open(manifest_file, "w") as f:
            for file, date in manifest_dict.items():
                f.write("{};{}".format(file,date))
        logger.debug("wrote manifest {}".format(manifest_file))

    def diff_manifest(self, old_manifest, new_manifest):
        """
        compare two manifest structures

        return new structure only containing new or changed files from old to new
        files with changed modification time are mentioned
        removed files are NOT mentioned
        returns {} if no changes.
        """
        diff = {}
        for base_name, date in new_manifest.items():
            if not base_name in old_manifest.keys():
                diff[base_name]=new_manifest[base_name]
            elif old_manifest[base_name] != new_manifest[base_name]:
                diff[base_name]=new_manifest[base_name]
        logger.debug("differences:{}".format(diff))
        return diff


    def create_manifest(self, manifest_dir, manifest_files):
        """
        create manifest from directoryself

        returns manifest structure

        manifest structure is

           dict = {
            file_base_name: change_datetime
           }


        """
        manifest = {}
        manifest_file = os.path.join(manifest_dir, self.manifest_file)
        logger.debug("files for new manifest: {}".format(manifest_files))
        for file_base_name in manifest_files:
            # ignore config and manifest
            if file_base_name in [self.manifest_file, self.config_file]:
                continue
            file_name = os.path.join(manifest_dir, file_base_name)
            timestamp = os.path.getmtime(file_name)
            manifest[file_base_name] = time.ctime(timestamp)

        logger.debug("manifest for {}: {}".format(manifest_dir, manifest))
        return manifest


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
            line = line.strip()
            if "#" in line:
                continue
            if not "@" in line:
                continue
            mailaddresses.append(line)

        logger.debug("read {} addresses from {}".format(len(mailaddresses), file))
        return mailaddresses

    def notify(self, root, diff_manifest):
        """
        send mail about changed files
        """

        if not diff_manifest:
            logger.warn("no changes, should not be here")
            return

        base_dir = os.path.basename(root)
        mailaddresses = self.read_config(root)
        logger.info("send notifications about {} to {}".format(base_dir, mailaddresses))

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
            for dir in subdirs:
                sub_base_name = os.path.basename(dir)
                if sub_base_name.startswith('.'):
                    logger.info("ignoring subdirectory {}".format(sub_base_name))
                    subdirs.remove(dir)

            # look for configfile, else bail out
            if not self.config_file in files:
                logger.info("no '{}' in '{}', ignoring directory".format(self.config_file, base_name))
                continue

            # read manifest and create new manifest
            manifest = self.read_manifest(root)
            new_manifest = self.create_manifest(root, files)

            # compare
            diff_manifest = self.diff_manifest(manifest, new_manifest)

            # notify and write new manifest if there are differences
            if diff_manifest:
                self.notify(root, diff_manifest)
                self.write_manifest(root, new_manifest)
            else:
                logger.info("nothing changed in {}".format(base_name))

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
