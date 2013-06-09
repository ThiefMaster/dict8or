import requests
import tempfile
import tarfile
import os
import shutil


def _fetch_and_extract(pkg_name, fname, url):
    print("Fetching {}".format(url))

    r = requests.get(url)
    dir_path = tempfile.mkdtemp(prefix='dict8or-')
    fpath = os.path.join(dir_path, fname)

    try:
        if r.status_code == 200:
            with open(fpath, 'wb') as f:
                for chunk in r.iter_content():
                    f.write(chunk)

            print("Extracting {}".format(fpath))

            tar = tarfile.open(fpath)
            tar.extractall(dir_path)
            tar.close()

            print("Done.")

            return dir_path
        else:
            print("Error {} downloading tarball for {} ({})".format(
                r.status_code, pkg_name, url))
    except:
        shutil.rmtree(dir_path)
        raise
