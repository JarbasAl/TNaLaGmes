# Copyright 2017 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import re
import subprocess

from threading import Thread
from time import sleep

import os.path
import psutil
from stat import S_ISREG, ST_MTIME, ST_MODE, ST_SIZE
import signal as sig
from tnalagmes.util.log import LOG
from tnalagmes.util.signal import *


def resolve_resource_file(res_name, lang="en-us"):
    """Convert a resource into an absolute filename.

    Resource names are in the form: 'filename.ext'
    or 'path/filename.ext'

    The system wil look for ~/.mycroft/res_name first, and
    if not found will look at /opt/mycroft/res_name,
    then finally it will look for res_name in the 'mycroft/res'
    folder of the source code package.

    Args:
        res_name (str): a resource path/name
    """
    # First look for fully qualified file (e.g. a user setting)
    if os.path.isfile(res_name):
        return res_name

    # Now look for in user folder
    filename = os.path.expanduser("~/tnalagmes/" + res_name)
    if os.path.isfile(filename):
        return filename

    # Next look for ~/tnalagmes/res/res_name
    filename = os.path.expanduser("~/tnalagmes/res/" + res_name)
    if os.path.isfile(filename):
        return filename

    # Next look for ~/tnalagmes/locale/lang/res_name
    filename = os.path.expanduser("~/tnalagmes/locale/" + lang + "/" + res_name)
    if os.path.isfile(filename):
        return filename

    # next look for it in locale
    filename = os.path.join(os.path.dirname(__file__), '..', 'locale',lang, res_name)
    filename = os.path.abspath(os.path.normpath(filename))
    if os.path.isfile(filename):
        return filename

    # next look for it in data
    filename = os.path.join(os.path.dirname(__file__), '..', 'data', lang, res_name)
    filename = os.path.abspath(os.path.normpath(filename))
    if os.path.isfile(filename):
        return filename

    # Finally look for it in the source package
    filename = os.path.join(os.path.dirname(__file__), '..', 'res', res_name)
    filename = os.path.abspath(os.path.normpath(filename))
    if os.path.isfile(filename):
        return filename

    # Let's check default internal file formats
    if not filename.endswith(".voc") and not filename.endswith(".intent") and not filename.endswith(".rx"):
        vocs = resolve_resource_file(filename+".voc")
        if vocs:
            return vocs
        vocs = resolve_resource_file(filename+".intent")
        if vocs:
            return vocs
        vocs = resolve_resource_file(filename+".rx")
        if vocs:
            return vocs
    return None  # Resource cannot be resolved


def play_wav(uri):
    if not uri.startswith("http"):
        uri = resolve_resource_file(uri)
    play_cmd = "paplay %1 --stream-name=tnalagmes"
    play_wav_cmd = str(play_cmd).split(" ")
    for index, cmd in enumerate(play_wav_cmd):
        if cmd == "%1":
            play_wav_cmd[index] = get_http(uri)
    return subprocess.Popen(play_wav_cmd)


def play_mp3(uri):
    if not uri.startswith("http"):
        uri = resolve_resource_file(uri)
    play_cmd = "mpg123 %1"
    play_mp3_cmd = str(play_cmd).split(" ")
    for index, cmd in enumerate(play_mp3_cmd):
        if cmd == "%1":
            play_mp3_cmd[index] = get_http(uri)
    return subprocess.Popen(play_mp3_cmd)


def play_ogg(uri):
    play_cmd = "ogg123 -q %1"
    play_ogg_cmd = str(play_cmd).split(" ")
    for index, cmd in enumerate(play_ogg_cmd):
        if cmd == "%1":
            play_ogg_cmd[index] = (get_http(uri))
    return subprocess.Popen(play_ogg_cmd)


def record(file_path, duration, rate, channels):
    if duration > 0:
        return subprocess.Popen(
            ["arecord", "-r", str(rate), "-c", str(channels), "-d",
             str(duration), file_path])
    else:
        return subprocess.Popen(
            ["arecord", "-r", str(rate), "-c", str(channels), file_path])


def get_http(uri):
    return uri.replace("https://", "http://")


def remove_last_slash(url):
    if url and url.endswith('/'):
        url = url[:-1]
    return url


def read_stripped_lines(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f]


def read_dict(filename, div='='):
    d = {}
    with open(filename, 'r') as f:
        for line in f:
            (key, val) = line.split(div)
            d[key.strip()] = val.strip()
    return d


def curate_cache(directory, min_free_percent=5.0, min_free_disk=50):
    """Clear out the directory if needed

    This assumes all the files in the directory can be deleted as freely

    Args:
        directory (str): directory path that holds cached files
        min_free_percent (float): percentage (0.0-100.0) of drive to keep free,
                                  default is 5% if not specified.
        min_free_disk (float): minimum allowed disk space in MB, default
                               value is 50 MB if not specified.
    """

    # Simpleminded implementation -- keep a certain percentage of the
    # disk available.
    # TODO: Would be easy to add more options, like whitelisted files, etc.
    space = psutil.disk_usage(directory)

    # convert from MB to bytes
    min_free_disk *= 1024 * 1024
    # space.percent = space.used/space.total*100.0
    percent_free = 100.0 - space.percent
    if percent_free < min_free_percent and space.free < min_free_disk:
        LOG.info('Low diskspace detected, cleaning cache')
        # calculate how many bytes we need to delete
        bytes_needed = (min_free_percent - percent_free) / 100.0 * space.total
        bytes_needed = int(bytes_needed + 1.0)

        # get all entries in the directory w/ stats
        entries = (os.path.join(directory, fn) for fn in os.listdir(directory))
        entries = ((os.stat(path), path) for path in entries)

        # leave only regular files, insert modification date
        entries = ((stat[ST_MTIME], stat[ST_SIZE], path)
                   for stat, path in entries if S_ISREG(stat[ST_MODE]))

        # delete files with oldest modification date until space is freed
        space_freed = 0
        for moddate, fsize, path in sorted(entries):
            try:
                os.remove(path)
                space_freed += fsize
            except:
                pass

            if space_freed > bytes_needed:
                return  # deleted enough!


def get_cache_directory(dir=None, domain=None):
    """Get a directory for caching data

    This directory can be used to hold temporary caches of data to
    speed up performance.  This directory will likely be part of a
    small RAM disk and may be cleared at any time.  So code that
    uses these cached files must be able to fallback and regenerate
    the file.

    Args:
        domain (str): The cache domain.  Basically just a subdirectory.

    Return:
        str: a path to the directory where you can cache data
    """
    if not dir:
        # If not defined, use /tmp/mycroft/cache
        dir = os.path.join(tempfile.gettempdir(), "tnalagmes", "cache")
    return ensure_directory_exists(dir, domain)


def get_arch():
    """ Get architecture string of system. """
    return os.uname()[4]


def reset_sigint_handler():
    """
    Reset the sigint handler to the default. This fixes KeyboardInterrupt
    not getting raised when started via start-mycroft.sh
    """
    sig.signal(sig.SIGINT, sig.default_int_handler)


def create_daemon(target, args=(), kwargs=None):
    """Helper to quickly create and start a thread with daemon = True"""
    t = Thread(target=target, args=args, kwargs=kwargs)
    t.daemon = True
    t.start()
    return t


def wait_for_exit_signal():
    """Blocks until KeyboardInterrupt is received"""
    try:
        while True:
            sleep(100)
    except KeyboardInterrupt:
        pass


def camel_case_split(identifier: str) -> str:
    """Split camel case string"""
    regex = '.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)'
    matches = re.finditer(regex, identifier)
    return ' '.join([m.group(0) for m in matches])
