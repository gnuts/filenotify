#!python

"""
https://github.com/gnuts/filenotify

Filenotify watches a directory structure and notifies users about changes in each directoryself.

- Each directory has its own configuration file that contains the mailaddresses that will be notifiedself.
- Each directory also contains a manifest file that contains information about known files
- When run, the contents of the manifest file are compared to the actual files in the directory. Any differences are notified and the manifest is then updated
"""

# 17:10 - 18:10 = 1h
# 15:00 - 16:30 = 1.5h
# 13:30 - 15:00 = 1.5h
# 15:00 - 16:30 = 1.5h
# = 5.5h
# 15:30 - 16:00 = 0.5h
# = 6h

import os
import sys
import time
import argparse
import logging
import configparser
from smtplib import SMTP_SSL, SMTP
from email.mime.text import MIMEText

logger = logging.getLogger("filenotify")

class FileNotify:
    dryrun = False
    manifest_file = ".MANIFEST"
    config_file = "mailaddresses.txt"
    sys_config_file = None
    smtp_host = "localhost"
    smtp_port = 25
    smtp_starttls = False
    smtp_ssl = False
    smtp_user = None
    smtp_from = "filenotify"
    smtp_cc = None
    smtp_subject = "there are new or changed files"
    smtp_template = """Hello,

there are new or changed files in directory {base_dir}:

the following files are new or have changed:

{changed_files}

regards,
your filenotify bot
"""

    def __init__(self, base_dir, manifest_file=None, config_file=None, sys_config_file=None,
                 smtp_host=None, smtp_port=None, smtp_starttls=None, smtp_ssl=None, smtp_user=None,
                 smtp_password=None, smtp_from=None, smtp_cc=None, smtp_subject=None, smtp_template=None,
                 dryrun=False):
        self.base_dir = os.path.realpath(base_dir)


        self.dryrun = dryrun
        if manifest_file: self.manifest_file = manifest_file
        if config_file: self.config_file = config_file

        # setup smtp parameters
        if sys_config_file: self.sys_config_file = sys_config_file
        if sys_config_file:
            self.read_sys_config(sys_config_file)
        # smtp arguments from constructor/command line override config file!
        if smtp_host: self.smtp_host = smtp_host
        if smtp_port: self.smtp_port = smtp_port
        if smtp_starttls: self.smtp_starttls = smtp_starttls
        if smtp_ssl: self.smtp_ssl = smtp_ssl
        if smtp_user: self.smtp_user = smtp_user
        if smtp_password: self.smtp_password = smtp_password
        if smtp_from: self.smtp_from = smtp_from
        if smtp_cc: self.smtp_cc = smtp_cc

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
            line = line.strip()
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
                f.write("{};{}\n".format(file,date))
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

    def read_sys_config(self, sys_config_file):
        """
        read filenotify system configuration

        thats an ini style config file containing:

        [mail]
        host = your.mail.server
        user = smtp_user
        port = 25
        starttls = False
        ssl = False
        password = yourfancypassword
        from = sending@address
        cc = optional@receipients, if@you.like
        subject = files have changed
        template = hi receipient,
            this is the message body.
            valid placeholders are:
            {base_name} is the directory containing the changes
            {changed_files} is a comma separated list of files that have changed
        """

        config = configparser.ConfigParser()
        config.read([sys_config_file])
        logger.debug("configuration read from {}".format(sys_config_file))
        self.smtp_host = config.get("mail","host")
        self.smtp_port = config.get("mail","port")
        self.smtp_starttls = config.getboolean("mail","starttls")
        self.smtp_ssl = config.getboolean("mail","ssl")
        self.smtp_user = config.get("mail","user")
        self.smtp_password = config.get("mail","password")
        self.smtp_from = config.get("mail","from")
        self.smtp_cc = config.get("mail","cc")
        self.smtp_subject = config.get("mail","subject")
        self.smtp_template = config.get("mail","template")

    def notify(self, root, diff_manifest):
        """
        send mail about changed files
        """

        if not diff_manifest:
            logger.error("no changes, should not be here")
            return

        base_dir = os.path.basename(root)
        mailaddresses = self.read_config(root)
        logger.info("send notifications about {} to {}".format(base_dir, mailaddresses))
        # fill in template
        changed_files = ", ".join(diff_manifest.keys())
        logger.debug("changed_files: {}".format(changed_files))

        # create mail
        mailtext = self.smtp_template.format(base_dir=self.base_dir, changed_files=changed_files)
        message = MIMEText(mailtext)
        message['Subject'] = self.smtp_subject
        message['To'] = ", ".join(mailaddresses)
        message["From"] = self.smtp_from
        message["Cc"] = self.smtp_cc
        logger.debug("text to send: {}".format(mailtext))
        # send mail
        try:
            logger.debug("opening connection to {}:{}".format(self.smtp_host, self.smtp_port))

            if self.smtp_ssl:
                logger.debug("connecting using SSL")
                conn = SMTP_SSL(host=self.smtp_host, port=self.smtp_port)
            else:
                conn = SMTP(host=self.smtp_host, port=self.smtp_port)

            if logger.level == logging.DEBUG:
                conn.set_debuglevel(True)
            if self.smtp_starttls:
                logger.debug("sending starttls")
                conn.starttls()

            # login in if needed
            if self.smtp_user:
                logger.debug("logging in as {}".format(self.smtp_user))
                conn.login(self.smtp_user, self.smtp_password)

            try:
                logger.debug("sending mail from {} to {}".format(self.smtp_from, mailaddresses))
                conn.sendmail(self.smtp_from, mailaddresses, message.as_string())
            finally:
                conn.close()

        except Exception as exc:
            logger.error("Error sending mail")
            logger.critical(exc)
            sys.exit("Mail failed: {}".format(exc))


    def run(self):
        """
        run filenotify and scoop directories

        - directories that do not contain a config file are ignored
        - directories and files starting with '.' are ignored
        """
        logger.info("scanning {}".format(self.base_dir))
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
                logger.warn("no '{}' in '{}', ignoring directory".format(self.config_file, base_name))
                continue

            # read manifest and create new manifest
            manifest = self.read_manifest(root)
            new_manifest = self.create_manifest(root, files)

            # compare
            diff_manifest = self.diff_manifest(manifest, new_manifest)

            # notify and write new manifest if there are differences
            if diff_manifest:
                logger.info("there are changes in {}".format(base_name))
                logger.debug("changes: {}".format(diff_manifest))
                if self.dryrun:
                    logger.warn("dryrun: doing nothing")
                else:
                    self.notify(root, diff_manifest)
                    self.write_manifest(root, new_manifest)
            else:
                logger.info("nothing changed in {}".format(base_name))

def cmdline(args):
    """
    parse commandline

    returns parser namespace
    """
    parser = argparse.ArgumentParser(description = "detect and notify changes in directories")
    parser.add_argument("path", help="root directory where parsing starts")
    parser.add_argument("-v", "--verbose", help="enable verbose logging", action="store_true")
    parser.add_argument("-C", "--config", help="configuration file")
    parser.add_argument("--host", help="smtp host")
    parser.add_argument("--port", help="smtp port (default:%(default)s)", default=25, type=int)
    parser.add_argument("--user", help="smtp user")
    parser.add_argument("--password", help="smtp password")
    parser.add_argument("--starttls", help="send starttls in smtp connection", action="store_true")
    parser.add_argument("--ssl", help="use ssl connection for smtp connection", action="store_true")
    parser.add_argument("--from", help="sender address", dest="smtp_from")
    parser.add_argument("--cc", help="carbon copies for all mails")
    parser.add_argument("--subject", help="mail subject")
    parser.add_argument("--manifest", help="name of manifest file (default:%(default)s)",
                        default=FileNotify.manifest_file)
    parser.add_argument("--mailfile", help="name of directory config file (default:%(default)s)",
                        default=FileNotify.config_file)
    parser.add_argument("--dryrun", help="do not send mail and do not update manifest file",
                        action="store_true")
    #parser.add_argument("--", help="smtp")
    result = parser.parse_args(args)
    if result.verbose:
        logger.setLevel(logging.DEBUG)
    return result

def main(args):
    """init a filenotify instance with command line arguments and run it"""
    logging.basicConfig(format='%(message)s',level=logging.INFO)
    argp = cmdline(args)
    fn = FileNotify(argp.path, sys_config_file=argp.config, manifest_file=argp.manifest,
                    config_file=argp.mailfile, dryrun=argp.dryrun,
                    smtp_host=argp.host, smtp_port=argp.port, smtp_starttls=argp.starttls,
                    smtp_ssl=argp.ssl, smtp_user=argp.user, smtp_password=argp.password,
                    smtp_from=argp.smtp_from, smtp_cc=argp.cc, smtp_subject=argp.subject
                    )
    fn.run()

if __name__ == "__main__":
    main(sys.argv[1:])
