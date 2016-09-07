#!/usr/bin/python3
# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Python instrument for connecting deeplace Drupal
# modules.
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
#
# Usage:
#   drush_module.py
#   --gitdir=./
#   --archive-dir=/work/www/drupalupdates/archive/mywebform/
#   --release-base-url=http://gitlab.deeplace.md/project/mywebform/tags/{tag}
#   --archive-base-url=http://drupalupdates.deeplace.md/archive/mywebform/mywebform-{tag}
#   --base-xml-dir=/work/www/drupalupdates/release-history/mywebform
#
import subprocess
import xml.etree.ElementTree as ET
import re
import logging
import os
import time
import hashlib
import argparse


def main():
    """ Python instrument for connecting deeplace Drupal
        modules.

    """
    logging.basicConfig(format='%(levelname)s [%(asctime)s]  %(message)s',
                        level=logging.DEBUG,
                        filename='mylog.log')
    logger = logging.getLogger("myLog")
    try:
        args = getArgs(logger)
        if args['tag'] in getTagList():
            createArchive(args['tag'], args['archive_dir'])
            writeInfoToXML(args)
            logger.info("Created xml and archive for {0}-{1}".format(
                args['module'], args['tag']))
        else:
            logger.warning("Invalid tag for this module")
    except Exception as exc:
        logger.error("{0}: {1}".format(type(exc), exc.args))


def getArgs(logger):
    """ Get arguments from command prompt.

        Args for scrypt:
        --gitdir=./
        --archive-dir=/work/www/drupalupdates/archive/mywebform/
        --release-base-url=http://gitlab.deeplace.md/project/mywebform/tags/7.x
        --archive-dase-url=http://drupalupdates.deeplace.md/archive/mywebform/mywebform-7.x
        --base-xml-dir=/work/www/drupalupdates/release-history/mywebform

        Parameters:
        logging     logger

        Returns:
        dict    args from command promt

    """
    parser = argparse.ArgumentParser(
            description='Connect deeplace Drupal modules')
    parser.add_argument(
        '--gitdir', nargs='?',
        help='Path to git repository', default='./')
    parser.add_argument(
        '--archive-dir', nargs='?',
        help='Path to archive storage',
        default="/work/www/drupalupdates/archive/mywebform/")
    parser.add_argument(
        '--release-base-url', nargs='?',
        help='Release url',
        default="http://gitlab.deeplace.md/project/mywebform/tags/7.x")
    parser.add_argument(
        '--archive-base-url', nargs='?',
        help='Url for download archive',
        default="http://drupalupdates.deeplace.md/archive\
/mywebform/mywebform-7.x")
    parser.add_argument(
        '--base-xml-dir', nargs='?',
        help='Path to xml storage',
        default="/work/www/drupalupdates/release-history/mywebform")
    args = vars(parser.parse_args())
    try:
        module = args['archive_base_url'].split("/")
        tag = re.findall(r"\b[6-8]\.x\S*", module[len(module) - 1])
        module = module[len(module) - 2]
        args['tag'] = tag[0]
        args['module'] = module
        if args['archive_dir'][len(args['archive_dir']) - 1] != '/':
            args['archive_dir'] = args['archive_dir'] + '/'
        return args
    except Exception as e:
        logger.error("{0}: {1}".format(type(e), e.args))
        return False


def getTagList():
    """ Get list of versions of module of current repository.

        Using `git branch` gets all branches of repository. Find
        branches looks like 7.x or 6.x, creates a list with them.

        Return:
            list of tags if exist tags like 7.x or 6.x and
            empty list if not.

    """
    tags = subprocess.check_output("git branch", shell=True).decode()
    return re.findall(r"\b[6-8]\.x\S*", tags)


def createArchive(tag, archive_dir):
    """ Create archive with files for tag from parameters.

        Using `git archive` creates archive in format <tag>.tar.gz.

        Parameters:
        dict    args    arguments from command prompt

        Example:
        tag - 7.x
        archive - 7.x.tar.gz

    """
    os.chdir("..")
    subprocess.call("git archive {0} --format=tar.gz\
                     --output={1}{0}.tar.gz".format(tag,
                                                    archive_dir),
                    shell=True)
    os.chdir("drush_module")


def writeInfoToXML(args):
    """ Create .xml file and write information about modules.
        Standart for .xml:
            https://updates.drupal.org/release-history/migrate/7.x

        Parameters:
        dict    args    arguments from command prompt

        Example:
            args['tag'] - 7.x
            project name - mywebform
            xml - muwebform-7.x.xml

    """
    info = getInfo(args['tag'], args['module'])
    filename = "{0}-{1}.xml".format(info['short_name'],
                                    info['core'])
    with open("{0}/{1}".format(args['base_xml_dir'], filename), "w") as file:
        header = '<?xml version="1.0" encoding="UTF-8"?>'
        file.write(header)
        project = ET.Element("project")
        project.set("xmlns:dc", "http://purl.org/dc/elements/1.1/")
        setTitle(project, info, args['release_base_url'])
        setTerms(project)
        setReleases(project, info, args)
        file.write(ET.tostring(project, "utf-8").decode("utf-8"))


def getInfo(tag, module):
    """ Get information about version.

        Read file <module_name>.info and gets all information from
        this file. Create dictionary with these parameters.

        Parameters:
        str     tag     version of module

        Returns:
        dict    info

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
             'version': '7.x-1.0',
             'short_name': 'mywebform',
             'version_major': '1',
             'version_patch': '0'
             }

    """
    subprocess.call("git checkout {0}".format(tag), shell=True)
    with open("../{0}.info".format(module), "r") as file:
        temp = file.read().split("\n")
        temp = list(filter(None, temp))
        info = {tmp.split(" = ")[0].replace("\"", ""):
                tmp.split(" = ")[1].replace("\"", "") for tmp in temp
                }
        info['short_name'] = module
        info['version_major'] = info["version"].split("-")[1].split(".")[0]
        info['version_patch'] = info["version"].split("-")[1].split(".")[1]
    subprocess.call("git checkout master", shell=True)
    return info


def setTitle(project, info, link):
    """ Set title tags to .xml file.

        Creates list of tags and values and generate xml
        format for title tags.

        Parameters:
        xml.etree.ElementTree   project
        dict                    info        information about module
        str                     link        release link

        Example:
            <title>My webform</title>
            <short_name>mywebform</short_name>
            <dc:creator>Deeplace</dc:creator>
            <type>project_module</type>
            <api_version>7.x</api_version>
            <recommended_major>1</recommended_major>
            <supported_major>1</supported_major>
            <default_major>1</default_major>
            <project_status>published</project_status>
            <link>http://gitlab.deeplace.md/project/mywebform/tags/{tag}</link>

    """
    fields = [["title", info['name']],
              ["short_name", info['short_name']],
              ["dc:creator", "Deeplace"],
              ["type", "project_module"],
              ["api_version", info['core']],
              ["recommended_major", info['version_major']],
              ["supported_major", info['version_major']],
              ["default_major", info['version_major']],
              ["project_status", "published"],
              ["link", link]
              ]
    for field in fields:
        block = ET.SubElement(project, field[0])
        block.text = field[1]


def setTerms(project):
    """ Set terms tags to .xml file.

        Parameters:
        xml.etree.ElementTree   project

        Example:
            <terms>
                <term>
                    <name>Project</name>
                    <value>Modules</value>
                </term>
                <term>
                    <name>Maintenance status</name>
                    <value>Seeking new maintaner</value>
                </term>
                <term>
                    <name>Development status</name>
                    <value>No further development</value>
                </term>
                <term>
                    <name>Module categories</name>
                    <value>Content</value>
                </term>
                <term>
                    <name>Module categories</name>
                    <value>Import/export</value>
                </term>
            </terms>

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


def setReleases(project, info, args):
    """ Set releases tags to .xml file.

        Parameters:
            xml.etree.ElementTree   project
            dict                    info        information about module
            dict                    args        arguments from command prompt

        Example:
            <releases>
                <release>
                    <name>mywebform 7.x-1.0</name>
                    <version>7.x-1.0</version>
                    <tag>7.x-1.0</tag>
                    <version_major>1</version_major>
                    <version_patch>0</version_patch>
                    <status>published</status>
                    <release_link>http://gitlab.deeplace.md/project/mywebform/tags/7.x</release_link>
                    <download_link>http://drupalupdates.deeplace.md/archive/mywebform/mywebform-7.x</download_link>
                    <date>1472206272</date>
                    <mdhash>08a78d6c56a6a4daa9c943fe1ef3e270</mdhash>
                    <filesize>39166</filesize>
                    <files>
                        <file>
                            <url>http://gitlab.deeplace.md/project/mywebform/tags/{tag}</url>
                            <archive_type>tar.gz</archive_type>
                            <md5>08a78d6c56a6a4daa9c943fe1ef3e270</md5>
                            <size>39166</size>
                            <filedata>1472206272</filedata>
                        </file>
                    </files>
                    <terms>
                        <term>
                            <name>Release type</name>
                            <value>Security update</value>
                        </term>
                        <term>
                            <name>Release type</name>
                            <value>Bug fixes</value>
                        </term>
                        <term>
                            <name>Release type</name>
                            <value>New features</value>
                        </term>
                    </terms>
                </release>
            </releases>

    """
    releases = ET.SubElement(project, "releases")
    release = ET.SubElement(releases, "release")

    name = ET.SubElement(release, "name")
    name.text = "{0} {1}".format(info['short_name'], info["version"])

    version = ET.SubElement(release, "version")
    version.text = info["version"]

    tag = ET.SubElement(release, "tag")
    tag.text = info["version"]

    version_major = ET.SubElement(release, "version_major")
    version_major.text = info["version_major"]

    version_patch = ET.SubElement(release, "version_patch")
    version_patch.text = info["version_patch"]

    status = ET.SubElement(release, "status")
    status.text = "published"

    release_link = ET.SubElement(release, "release_link")
    release_link.text = args['release_base_url']

    download_link = ET.SubElement(release, "download_link")
    download_link.text = args['archive_base_url']

    date = ET.SubElement(release, "date")
    date.text = str(int(time.time()))

    path = "{0}{1}.tar.gz".format(args['archive_dir'],
                                  info['core'])

    mdhash = ET.SubElement(release, "mdhash")
    mdhash.text = hashlib.md5(open(path, 'rb').read()).hexdigest()

    filesize = ET.SubElement(release, "filesize")
    filesize.text = str(os.path.getsize(path))

    files = ET.SubElement(release, "files")
    file = ET.SubElement(files, "file")
    url = ET.SubElement(file, "url")
    url.text = args['release_base_url']
    archive_type = ET.SubElement(file, "archive_type")
    archive_type.text = "tar.gz"
    md5 = ET.SubElement(file, "md5")
    md5.text = hashlib.md5(open(path, 'rb').read()).hexdigest()
    size = ET.SubElement(file, "size")
    size.text = str(os.path.getsize(path))
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


if __name__ == "__main__":
    main()
