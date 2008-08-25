#-*- coding: utf8 -*
#
# Max E. Kuznecov 2008
#

from libxyz.core.plugins import BasePlugin

class XYZPlugin(BasePlugin):
    "Plugin fileinfo"

    # Plugin name
    NAME = u"fileinfo"

    # AUTHOR: Author name
    AUTHOR = u"Max E. Kuznecov"

    # VERSION: Plugin version
    VERSION = u"0.1"

    # Brief one line description
    BRIEF_DESCRIPTION = u""

    # Full plugin description
    FULL_DESCRIPTION = u""

    # NAMESPACE: Plugin namespace. For detailed information about
    #            namespaces see Plugins chapter of XYZCommander user manual.
    #            Full namespace path to method is:
    #            xyz:plugins:misc:hello:SayHello

    NAMESPACE = u"vfs"

    # MIN_XYZ_VERSION: Minimal XYZCommander version
    #                  the plugin is compatible with
    MIN_XYZ_VERSION = None

    # Plugin documentation
    DOC = None

    # Plugin home-page
    HOMEPAGE = None

    def __init__(self, xyz):
        super(XYZPlugin, self).__init__(xyz)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def prepare(self):
        pass

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def finalize(self):
        pass
