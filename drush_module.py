#!/usr/bin/python3
# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
import subprocess
import xml.etree.ElementTree as ET
import re
import logging
import os

import create_xml


def main():
    tags = getTagList()
    if tags:
        for tag in tags:
            createArchive(tag)
            writeInfoToXML(tag)


def getTagList():
    """ Get list of tags of current repository.

        Return:
            list of tags if exist tags like 7.x and
            empty list if not.

    """
    tags = subprocess.check_output("git branch",
                                   shell=True
                                   ).decode("utf-8").strip()
    if tags not in [" ", "\n"]:
        tags = re.findall(r"\b[6-8]\.x\S*", tags)
        # print(tags)
        return tags
    return []


def createArchive(tags):
    """ Create archive with files from each tag from tags.
        Collect all information about module and create dict
        params for writing to .xml.

        Parameters:
            list(tags) - all available tags in needed format.

        Return:
            dict(param) - all parameters for future writing to .xml.

    """
    os.chdir("..")
    subprocess.call("git archive {0} --format=tar.gz\
                     --output={0}.tar.gz".format(tags), shell=True)
    os.chdir("drush_module")


def writeInfoToXML(tag):
    """ Create .xml file and write information about modules.
        Standart for .xml:
            https://updates.drupal.org/release-history/migrate/7.x

        Parameters:
             dict(param) - all parameters for future writing to .xml.

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
