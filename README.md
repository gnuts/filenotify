# filenotify


Filenotify watches a directory structure and sends mail to users about changes in each directory.

- Each directory has its own configuration file that contains the mailaddresses that will be notified.
- Each directory also contains a manifest file that contains information about known files
- When run, the contents of the manifest file are compared to the actual files in the directory. 
  new files and files with changed modification time are notified and the manifest is then updated
- removed files will NOT be notified

The directory config file format is:

   # comment
   mail@address
   another@address
   ...
