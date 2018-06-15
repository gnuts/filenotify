# filenotify


Filenotify watches a directory structure and sends mail to users about changes in each directory.

Its intended use is for embedded NAS systems, therefore it has no requirements besides python 3 and its standard libs.

- Each directory has its own configuration file that contains the mailaddresses that will be notified.
- Each directory also contains a manifest file that contains information about known files
- When run, the contents of the manifest file are compared to the actual files in the directory.
  new files and files with changed modification time are notified and the manifest is then updated
- removed files will NOT be notified
- if a mailaddresses file is found, it will be used for subdirectories, too

# Usage

```
usage: filenotify.py [-h] [-v] [-C CONFIG] [--host HOST] [--port PORT]
                     [--user USER] [--password PASSWORD] [--starttls] [--ssl]
                     [--from SMTP_FROM] [--cc CC] [--subject SUBJECT]
                     [--manifest MANIFEST] [--mailfile MAILFILE] [--dryrun]
                     path

detect and notify changes in directories

positional arguments:
  path                  root directory where parsing starts

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         enable verbose logging
  -C CONFIG, --config CONFIG
                        configuration file
  --host HOST           smtp host
  --port PORT           smtp port (default:25)
  --user USER           smtp user
  --password PASSWORD   smtp password
  --starttls            send starttls in smtp connection
  --ssl                 use ssl connection for smtp connection
  --from SMTP_FROM      sender address
  --cc CC               carbon copies for all mails
  --subject SUBJECT     mail subject
  --manifest MANIFEST   name of manifest file (default:.MANIFEST)
  --mailfile MAILFILE   name of directory config file
                        (default:mailaddresses.txt)
  --dryrun              do not send mail and do not update manifest file

```

# Directory config file

The directory config file is `mailaddresses.txt` in each directory. If none is found, the one in a lower directory of the same branch is used. If there isn't any config file found, the directory is ignored.

The format is:

```
# comment
mail@address
another@address
```

# Filenotify Configuration file

For the mail configuration a ini style config file is used.

Format:

```ini
[mail]
host = your.mail.server
port = 25
user = smtp_user
starttls = False
ssl = False
password = yourfancypassword
from = sending@address
cc = optional@receipients, if@you.like
subject = files have changed
template = hi receipient,
    this is the message body.
    valid placeholders are:
    {base_dir} is the directory containing the changes
    {changed_files} is a comma separated list of files that have changed
```
