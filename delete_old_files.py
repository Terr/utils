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
  'delete-empty-dirs=yes': 'Delete empty directories in path when deleting the last file in it via --delete=yes'
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

    sPath   = None
    iDays   = 180
    bDeleteFiles    = False
    bDeleteEmptyDirs    = True
    iBytesDeleted   = 0
    sBytesDeleted   = ''

    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit()
        elif o in ('-p', '--path'):
            sPath = a

        elif o in ('-d', '--days'):
            iDays = int(a)
        elif o == '--delete':
            if a == 'yes':
                bDeleteFiles = True
        elif o == '--delete-empty-dirs':
            if a == 'no':
              bDeleteEmptyDirs = False
        else:
            assert False, 'Invalid option'

    if sPath == None:
        assert False, '--path parameter is required'

    dateDeleteFrom =  datetime.date.today() - datetime.timedelta(days = iDays)

    lDirList	= os.walk(sPath)

    for sDirPath, lDirNames, lFilenames in lDirList:
        for file in lFilenames:
            sFilePath	= sDirPath + os.sep + file
            statFile	= os.stat(sFilePath)
            dateFile	= datetime.datetime.fromtimestamp(statFile.st_mtime)

            if dateFile.date() <= dateDeleteFrom:
                if bDeleteFiles == False:
                    print 'Would delete: %s' % (sFilePath)
                else:
                    os.remove(sFilePath)
                    print 'Deleted: %s' % (sFilePath)

                iBytesDeleted += statFile.st_size

                dirHandled = os.listdir(sDirPath)

                # Manually remove file from directory listing when not deleting
                # the file
                if bDeleteFiles == False:
                    for x in dirHandled:
                        if x == file:
                            dirHandled.remove(x)

                if len(dirHandled) == 0:
                    if bDeleteFiles == False:
                        print 'Would delete empty directory: %s' % (sDirPath)
                    else:
                        os.removedirs(sDirPath)
                        print 'Deleted empty directory: %s' % (sDirPath)

                sBytesDeleted  = locale.format('%(a).2f MB', { 'a': iBytesDeleted / 1048576 }, True)

    if sBytesDeleted:
        if bDeleteFiles == False:
            print 'Would free up %s' % (sBytesDeleted)
        else:
            print 'Freed up %s' % (sBytesDeleted)
    else:
        print 'Nothing to delete'

if __name__ == '__main__':
  main()
