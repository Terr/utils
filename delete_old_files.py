#!/usr/bin/python
'''Script for deleting old files (and empty directories) after X days of not being modified'''

import sys, os, getopt
import datetime

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
  sDirs_with_deleted_files = set()

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

        dir_handled = os.listdir(dirpath)

        if delete == False:
          for x in dir_handled:
            if x == file:
              dir_handled.remove(x)

        if len(dir_handled) == 0:
          if delete == False:
            print 'Would delete directory: %s' % (dirpath)
          else:
            os.removedirs(dirpath)
            print 'Deleted directory: %s' % (dirpath)

if __name__ == '__main__':
  main()
