"""

This script definitively identifies the gruft scattered throughout CMFPlone.
Usage:

% python seeWhatsOutThere.py foo/bar.py baz.pt

If you pass in paths relative to CMFPlone, only those will be checked, and a
list of GRUFisms will be returned. If no arguments are given, the script will
walk all of CMFPlone and will return a summary count of GRUFisms per file
(.pyc's and .svn dirs are always skipped).

GRUFisms are API in GRUF that aren't in our implementation of PAS.

$Id: seeWhatsOutThere.py,v 1.2 2005/02/04 10:43:51 whit537 Exp $
"""
from pprint import pprint
from sets import Set
from os.path import join


# framework is copied over from CMFPlone/tests
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))


# Set up a Plone site. I couldn't get this to work with PloneTestCase but I
#  imagine that would be the first optimization. Another option would be to
#  cache the diff in a file, and only refresh the diff if explicitly asked to.
print 'installing Zope ...'
import Zope
from AccessControl.SecurityManagement import newSecurityManager
app = Zope.app()
app.acl_users._doAddUser('fooUser', '', ['Manager'], [])
user = app.acl_users.getUserById('fooUser').__of__(app.acl_users)
newSecurityManager(None, user)
app.manage_addProduct['CMFPlone'].manage_addSite('portal')


# get all the methods from GRUF
print 'inspecting GRUF ...'
gruf = Set(dir(app.portal.acl_users))


# get the API available in the new PAS-based acl_users
print 'inspecting PAS ...'
app.portal.manage_delObjects(['acl_users'])
app.portal.portal_quickinstaller.installProduct('PlonePAS')
pas = Set(dir(app.portal.acl_users))


# get the elements which are in GRUF but not PAS
diff = gruf - pas
del(app)


# tell someone about it
print """\
results of our inspections:
  GRUF: %s
  PAS:  %s
  diff: %s"""\
% (len(gruf), len(pas), len(diff))


# get ready to search through some files
INSTANCE_HOME = os.environ['INSTANCE_HOME']
CMFPLOME = join(INSTANCE_HOME, 'Products', 'CMFPlone')

def sniffFile(abspath):
    """ given an abspath, return a list of GRUFisms """
    text = file(abspath).read()
    attrs = []
    for attr in diff:
        if text.count(attr) > 0:
            if attr not in attrs:
                attrs.append(attr)
    return attrs


tests = sys.argv[1:]
if tests:
    # if we have args then only sniff those files; give verbose output
    print "only checking %s ..." % ', '.join(tests)
    print

    for test in tests:
        abspath = join(CMFPLOME, test)
        attrs = sniffFile(abspath)
        if attrs:
            print test
            print "="*40
            for attr in attrs:
                print attr
        print

else:
    # if we don't have args then walk the entire CMFPlone tree; output a summary
    totalGRUFiles = totalattrs = 0

    # print the header
    print "no args given, walking all of %s ..." % CMFPLOME
    print
    print "%s  GRUFisms" % ("File".ljust(59))
    print "=" * 79

    # walk the tree
    for p, d, f in os.walk(CMFPLOME):
        for filename in f:

            if not filename.endswith('.pyc') and not p.count('.svn'):

                abspath = join(p, filename)
                plonepath = abspath[len(CMFPLOME)+1:]

                attrs = sniffFile(abspath)

                if attrs:
                    totalGRUFiles += 1
                    numattrs = len(attrs)
                    totalattrs += numattrs
                    print "%s  %s" %\
                        (plonepath[:60].ljust(60), str(numattrs).rjust(4))


    # print the footer
    foo = "TOTAL: %s files" % totalGRUFiles
    bar = str(totalattrs)
    print "-" * 79
    print "%s  %s" % (foo.ljust(60), bar.rjust(4))