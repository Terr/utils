#!/usr/bin/python
'''Script for deleting old files (and empty directories) after X days of not being modified'''

import sys, os, getopt, locale
import datetime

locale.setlocale(locale.LC_ALL, '')

parameters = 'hp:d:'
parameters_long = ['help', 'path=', 'days=', 'delete=', 'delete-empty-dirs=']
parameters_description	= {
  'help': 'This help screen',
  'path': 'Path to the directory to check (required)',
  'days=180': 'Number of days in the past to check files against. Files that aren\'t modified since will be deleted if --delete=yes',
  'delete=no': 'Delete files that are older than --days if value = \'yes\'. Default is to print a list of files that would be deleted',
  'delete-empty-dirs=yes': 'Will delete empty directories in path when --delete=yes'
}

def usage():
  print 'Possible options:'
  for p in parameters_description:
    print '--%s: %s' % (p, parameters_description.get(p, None))

def main():
    try:
        opts, args	= getopt.getopt(sys.argv[1:], parameters, parameters_long)
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)

    path = None
    days = 180
    delete = False
    delete_empty_dirs = True
    bytes_deleted = 0

    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit()
        elif o in ('p', '--path'):
            path = a

        elif o in ('d', '--days'):
            days = int(a)
        elif o == '--delete':
            if a == 'yes':
                delete = True
        elif o == '--delete-empty-dirs':
            if a == 'no':
              delete_empty_dirs = False
        else:
            assert False, 'Invalid option'

    if path == None:
        assert False, '--path parameter is required'

    delete_date_from =  datetime.date.today() - datetime.timedelta(days = days)

    dir_list	= os.walk(path)

    for dirpath, dirnames, filenames in dir_list:
        for file in filenames:
            file_path	= dirpath + os.sep + file
            file_stat	= os.stat(file_path)
            file_date	= datetime.datetime.fromtimestamp(file_stat.st_mtime)

            if file_date.date() <= delete_date_from:
                if delete == False:
                    print 'Would delete: %s' % (file_path)
                else:
                    os.remove(file_path)
                    print 'Deleted: %s' % (file_path)

                bytes_deleted += file_stat.st_size

                dir_handled = os.listdir(dirpath)

                # Manually remove file from directory listing when not deleting
                # the file
                if delete == False:
                    for x in dir_handled:
                        if x == file:
                            dir_handled.remove(x)

                if len(dir_handled) == 0:
                    if delete == False:
                        print 'Would delete empty directory: %s' % (dirpath)
                    else:
                        os.removedirs(dirpath)
                        print 'Deleted empty directory: %s' % (dirpath)

                sBytes_deleted  = locale.format('%(a).2f MB', { 'a': bytes_deleted / 1048576 }, True)

    if delete == False:
        print 'Would free up %s' % (sBytes_deleted)
    else:
        print 'Freed up %s' % (sBytes_deleted)

if __name__ == '__main__':
  main()
