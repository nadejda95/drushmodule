#!/usr/bin/python3
# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Python instrument for connecting deeplace Drupal
# modules.
#
# 1) Is executing in git repository hook post-receive
# of our modules:
#     git@git.work.deeplace.md/deeplace/infrastructure/drupal/<module>
# 2) Gets list of git repository tags looks like 6.x-1.12
# 3) For each tag creates archive <tag>.tar.gz with module cod
# 4) Write all versions of modules into <tag>.xml file with such format
# compatible with drush dl --source <url>:
#     https://updates.drupal.org/release-history/migrate/7.x
#
# For install module developer should use command:
#     drush dl --source http://drupalupdates.deeplace.md/
#                              release-history <module>
# or alias:
#     drush ddl <module>
import subprocess
import xml.etree.ElementTree as ET
import re
import logging
import os

import create_xml


def main():
    """ Python instrument for connecting deeplace Drupal
        modules.

    """
    logging.basicConfig(format='%(levelname)s [%(asctime)s]  %(message)s',
                        level=logging.DEBUG,
                        filename='mylog.log')
    logger = logging.getLogger("myLog")
    try:
        tags = getTagList()
        if tags:
            for tag in tags:
                createArchive(tag)
                writeInfoToXML(tag)
        else:
            logger.warning("No tags in this repository")
    except Exception as exc:
        logger.error("{0} - {1}".format(type(exc), exc.args))


def getTagList():
    """ Get list of versions of module of current repository.

        Using `git branch` gets all branches of repository. Find
        branches looks like 7.x or 6.x, creates a list with them.

        Return:
            list of tags if exist tags like 7.x or 6.x and
            empty list if not.

    """
    tags = subprocess.check_output("git branch",
                                   shell=True
                                   ).decode("utf-8").strip()
    if tags not in [" ", "\n"]:
        tags = re.findall(r"\b[6-8]\.x\S*", tags)
        return tags
    return []


def createArchive(tag):
    """ Create archive with files for tag fom parameters.

        Using `git archive` creates archive in format <tag>.tar.gz.

        Parameters:
            str(tag) - tag from repository.

        Example:
            tag - 7.x
            archive - 7.x.tar.gz

    """
    os.chdir("..")
    subprocess.call("git archive {0} --format=tar.gz\
                     --output={0}.tar.gz".format(tag), shell=True)
    os.chdir("drush_module")


def writeInfoToXML(tag):
    """ Create .xml file and write information about modules.
        Standart for .xml:
            https://updates.drupal.org/release-history/migrate/7.x

        Parameters:
             str(tag) - tag which xml file is creating

        Example:
            tag - 7.x
            xml - 7.x.xml

    """
    info = getInfo(tag)
    filename = info['core'] + '.xml'
    with open(filename, "w") as file:
        header = '<?xml version="1.0" encoding="UTF-8"?>'
        file.write(header)
        project = ET.Element("project")
        project.set("xmlns:dc", "http://purl.org/dc/elements/1.1/")
        create_xml.setTitle(project, info)
        create_xml.setTerms(project, info)
        create_xml.setReleases(project, info)
        file.write(ET.tostring(project, "utf-8").decode("utf-8"))


def getInfo(tag):
    """ Get information about version.

        Read file <module_name>.info and gets all information from
        this file. Create dictionary with these parameters.

        Parameters:
            str(tag) - version of module

        Returns:
            dict(info)

        Example:
            mywebform.info:
                name = My webform
                description = Defines a custom webform.
                package = Deeplace
                core = 7.x
                version = 7.x-1.0
            info:
                {'package': 'Deeplace',
                 'description': 'Defines a custom webform.',
                 'core': '7.x',
                 'name': 'My webform',
                 'version': '7.x-1.0'
                 }

    """
    subprocess.call("git checkout {0}".format(tag), shell=True)
    with open("../mywebform.info") as file:
        temp = file.read().split("\n")
        temp = list(filter(None, temp))
        info = {tmp.split(" = ")[0].replace("\"", ""):
                tmp.split(" = ")[1].replace("\"", "") for tmp in temp
                }
    subprocess.call("git checkout master", shell=True)
    return info


if __name__ == "__main__":
    main()
