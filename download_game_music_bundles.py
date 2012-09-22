#!/usr/bin/python
"""Downloads (and optionally extracts) one or more music bundles that
you've bought from http://www.gamemusicbundle.com/

TODO:
    * Option to download MP3, FLAC or torrent
"""
import os
import sys
import re
import logging
import urllib2

from time import sleep

from zipfile import ZipFile

from pprint import pprint

from urlgrabber import urlopen
from urlgrabber.grabber import URLGrabber, URLGrabError

from urllib import quote

from urlparse import urlparse, parse_qs, urljoin

from bs4 import BeautifulSoup

from optparse import OptionParser


""""""

def merge_album_links(iter_links):
    """Merges different URLs to the same album (e.g. MP3, FLAC and torrents)
    into a single entry.
    """

    dict_output = {}

    # For testing
    #iter_links = iter_links[:1]

    for link in iter_links:
        up = urlparse(link)
        qs = parse_qs(up.query)
        album_id = ''.join(qs.get('album', []))

        if not album_id in dict_output:
            # Remove optional query parameters to create a base URL to work
            # with
            for param in OPT_QUERY_PARAMS:
                if param in qs:
                    del qs[param]

            dict_output[album_id] = '%s?%s' % (
                up.path,
                '&'.join(['%s=%s' % (k, quote(v[0])) for k,v in qs.iteritems()])
            )

    return dict_output

class ProgressPrint(object):
    def __init__(self, *args, **kwargs):
        self.size = 0
        self.last_prog_print = 0

    def start(self, filename, url, basename, size, text):
        self.last_prog_print = 0 # Enables re-use of this instance
        self.size = size

        if not text:
            print 'Downloading %s...' % filename,
        else:
            print text,

        self.flush()

    def update(self, bytes_read):
        if self.size:
            # Print percentage done at >=10%, >=20%, etc.
            prog_percent = (float(bytes_read) / float(self.size)) * 100
            prog_step = int(prog_percent / 10)

            if prog_step > self.last_prog_print:
                self.last_prog_print = prog_step
                print ' %d%%' % (prog_step * 10),
                self.flush()

    def end(self, amount_read):
        print ' done'

    def flush(self):
        sys.stdout.flush()

# Optional query parameters that can be safely removed from a download link
OPT_QUERY_PARAMS = ('flac', 'torrent', 'mp3',)

usage = 'usage: %prog [options] bundle_key bundle_key...'
parser = OptionParser(usage=usage)
parser.add_option(
    '-o', '--output-dir', action='store', dest='output_dir',
    help='Directory to download albums to [default: %default]',
    default=os.getcwd()
)
parser.add_option(
    '-u', '--url', action='store', dest='gmb_url',
    help='Game Music Bundle domain [default: %default]',
    default='http://www.gamemusicbundle.com/'
)
parser.add_option(
    '-x', '--extract', action='store_true', dest='extract',
    help='Extract files after downloading (to subdirectories) [default: no]',
    default=False
)
parser.add_option(
    '-k', '--keep-after-extract', action='store_true', dest='keep_after_extract',
    help='Keep files after extracting [default: no]',
    default=False
)

(options, args) = parser.parse_args()

if len(args) == 0:
    parser.error('One or more bundle keys are required')

progress_printer = ProgressPrint()
grabber = URLGrabber(prefix=options.gmb_url,
                     progress_obj=progress_printer)

# Download the albums for each key
for key in args:
    # Get download page and grab all download URLs
    download_page_url = urljoin(options.gmb_url, '/download?key=%s' % key)
    download_page = urlopen(download_page_url)
    html = download_page.read()
    soup = BeautifulSoup(html, 'lxml')
    download_page.close()

    # Find all download links
    regex_download_link = re.compile('/download\?.*')
    download_links = [x['href'] for x in soup.find_all('a', href=regex_download_link)]
    album_urls = merge_album_links(download_links)

    print 'Going to download %d album(s)' % len(album_urls)

    for url in album_urls.values():
        # Switch to output directory as urlgrabber downloads to the current dir
        os.chdir(options.output_dir)

        if url[0] == '/':
            url = url[1:]

        # First, use urllib2 to check the filename of the album after the
        # redirect from '/download' to Amazon and supply it to urlgrabber
        #print urljoin(options.gmb_url, url)
        try:
            url_redirect = urllib2.urlopen(urljoin(options.gmb_url, url))
            url_redirect_parsed = urlparse(url_redirect.geturl())
            filename = url_redirect_parsed.path[1:] # Strip /
        except urllib2.HTTPError, e:
            if e.code == 403:
                print 'A 403 Forbidden error was raised when accessing the download. Is your bundle key correct?'
            else:
                print e

            sys.exit(1)
        finally:
            url_redirect.close()

        try:
            grabber.urlgrab(url, filename=filename)
        except URLGrabError, e:
            if e.errno == 14:
                print 'Encountered HTTP error: %s' % (e.strerror)
            else:
                print 'Encountered error %d: %s' % (e.errno, e.strerror)
        else:
            if options.extract:
                print 'Extracting %s...' % filename,

                # Create directory
                dir_name = filename[:filename.rfind('.')]
                dir_name = dir_name.replace('+', ' ')
                try:
                    os.mkdir(dir_name)
                except OSError, e:
                    # Directory already exists -- ignore
                    pass

                # Switch to subdirectory to extract to
                os.chdir(dir_name)

                # Extract files
                zip = ZipFile(os.path.join(options.output_dir, filename))
                for file in zip.namelist():
                    if not file.endswith('/'):
                        zip.extract(file)

                if not options.keep_after_extract:
                    print ' done. Deleting zip...'
                    try:
                        os.remove(os.path.join(options.output_dir, filename))
                    except OSError, e:
                        print 'An error occured when trying to delete zip: %s' % e
                else:
                    print ' done'
