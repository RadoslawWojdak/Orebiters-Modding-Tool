# Resource object code (Python 3)
# Created by: object code
# Created by: The Resource Compiler for Qt version 6.11.2
# WARNING! All changes made in this file will be lost!

from PySide6 import QtCore

qt_resource_data = b"\
\x00\x00\x01\x01\
<\
svg xmlns=\x22http:\
//www.w3.org/200\
0/svg\x22 viewBox=\x22\
0 0 24 24\x22>\x0d\x0a   \
 <path\x0d\x0a        \
d=\x22M12 5V19M5 12\
H19\x22\x0d\x0a        fi\
ll=\x22none\x22\x0d\x0a     \
   stroke=\x22#0000\
00\x22\x0d\x0a        str\
oke-linecap=\x22rou\
nd\x22\x0d\x0a        str\
oke-linejoin=\x22ro\
und\x22\x0d\x0a        st\
roke-width=\x222\x22\x0d\x0a\
    />\x0d\x0a</svg>\x0d\x0a\
\
"

qt_resource_name = b"\
\x00\x05\
\x00o\xa6S\
\x00i\
\x00c\x00o\x00n\x00s\
\x00\x07\
\x07\xa7Z\x07\
\x00a\
\x00d\x00d\x00.\x00s\x00v\x00g\
"

qt_resource_struct = b"\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x01\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x02\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x10\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\
\x00\x00\x01\xa0XY!+\
"


def qInitResources() -> None:
    QtCore.qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)


def qCleanupResources() -> None:
    QtCore.qUnregisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)


qInitResources()
