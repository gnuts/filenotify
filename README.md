# filenotify


Filenotify watches a directory structure and sends mail to users about changes in each directory.

- Each directory has its own configuration file that contains the mailaddresses that will be notified.
- Each directory also contains a manifest file that contains information about known files
- When run, the contents of the manifest file are compared to the actual files in the directory.
  new files and files with changed modification time are notified and the manifest is then updated
- removed files will NOT be notified


# Directory config file

The directory config file is `mailaddresses.txt` in each directory.

The format is:

```
# comment
mail@address
another@address
...
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
