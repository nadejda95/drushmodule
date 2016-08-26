import xml.etree.ElementTree as ET
import time
import hashlib
import os
import logging


def setTitle(project, info):
    """ Set title tags to .xml file.

        Parameters:
            xml.etree.ElementTree(project)

    """
    fields = [["title", info['name']],
              ["short_name", info['name'].replace(" ", "").lower()],
              ["dc:creator", "Deeplace"],
              ["type", "project_module"],
              ["api_version", info['core']],
              ["recommended_major", info["version"].split("-")[1]
                                                   .split(".")[0]],
              ["supported_major", info["version"].split("-")[1].split(".")[0]],
              ["default_major", info["version"].split("-")[1].split(".")[0]],
              ["project_status", "published"],
              ["link", "http://deeplace.md/"]  #
              ]
    for field in fields:
        block = ET.SubElement(project, field[0])
        block.text = field[1]


def setTerms(project, info):
    """ Set terms tags to .xml file.

        Parameters:
            xml.etree.ElementTree(project)

    """
    terms = ET.SubElement(project, "terms")
    terms_content = [["Project", "Modules"],
                     ["Maintenance status", "Seeking new maintaner"],
                     ["Development status", "No further development"],
                     ["Module categories", "Content"],
                     ["Module categories", "Import/export"],
                     ]
    for content in terms_content:
        term = ET.SubElement(terms, "term")
        name = ET.SubElement(term, "name")
        name.text = content[0]
        value = ET.SubElement(term, "value")
        value.text = content[1]


def setReleases(project, info):
    """ Set releases tags to .xml file.

        Parameters:
            xml.etree.ElementTree(project)

    """
    releases = ET.SubElement(project, "releases")
    release = ET.SubElement(releases, "release")
    name = ET.SubElement(release, "name")
    name.text = info['name'].replace(" ", "").lower() + " " + info["version"]
    version = ET.SubElement(release, "version")
    version.text = info["version"]
    tag = ET.SubElement(release, "tag")
    tag.text = info["version"]
    version_major = ET.SubElement(release, "version_major")
    version_major.text = info["version"].split("-")[1].split(".")[0]
    version_patch = ET.SubElement(release, "version_patch")
    version_patch.text = info["version"].split("-")[1].split(".")[1]
    status = ET.SubElement(release, "status")
    status.text = "published"
    release_link = ET.SubElement(release, "release_link")
    release_link.text = "http://drupalupdates.deeplace.md/release-history"
    download_link = ET.SubElement(release, "download_link")
    download_link.text = "http://drupalupdates.deeplace.md/7.x-2.8.tar.gz"
    date = ET.SubElement(release, "date")
    date.text = str(int(time.time()))
    mdhash = ET.SubElement(release, "mdhash")
    mdhash.text = hashlib.md5(open("../{0}.tar.gz".format(info['core']),
                              'rb').read()
                              ).hexdigest()
    filesize = ET.SubElement(release, "filesize")
    filesize.text = str(os.path.getsize("../{0}.tar.gz".format(info['core'])))
    files = ET.SubElement(release, "files")
    file = ET.SubElement(files, "file")
    url = ET.SubElement(file, "url")
    url.text = "http://drupalupdates.deeplace.md/release-history"
    archive_type = ET.SubElement(file, "archive_type")
    archive_type.text = "tar.gz"
    md5 = ET.SubElement(file, "md5")
    md5.text = hashlib.md5(open("../{0}.tar.gz".format(info['core']),
                                'rb').read()).hexdigest()
    size = ET.SubElement(file, "size")
    size.text = str(os.path.getsize("../{0}.tar.gz".format(info['core'])))
    filedata = ET.SubElement(file, "filedata")
    filedata.text = str(int(time.time()))
    terms = ET.SubElement(release, "terms")
    terms_content = [["Release type", "Security update"],
                     ["Release type", "Bug fixes"],
                     ["Release type", "New features"]
                     ]
    for content in terms_content:
        term = ET.SubElement(terms, "term")
        name = ET.SubElement(term, "name")
        name.text = content[0]
        value = ET.SubElement(term, "value")
        value.text = content[1]
