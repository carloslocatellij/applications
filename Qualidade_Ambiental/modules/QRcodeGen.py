#!/usr/bin/python
# -*- coding: utf-8 -*-

#============================================#
#--- UM GERADOR DE QRCODEs PERSONALIZADOS ---#
#============================================#

# %%
'''
    "(C)" Carlos Augusto Locatelli Júnior 2023
    Este programa é um software livre: você pode redistribuí-lo e/ou modificá-lo sob os termos da
    GNU General Public License conforme publicada pela Free Software Foundation.
    Este programa é distribuído na esperança de que seja útil, mas SEM QUALQUER GARANTIA;
    Consulte <https://www.gnu.org/licenses/>.
'''
#UM GERADOR DE QRCODEs PERSONALIZADOS UTILIZANDO A LIB QRCODE DO PYTHON

# import modules
import qrcode
from PIL import Image


def adjust_logo(logo):
    logo = Image.open(logo)
    basewidth = 100
    wpercent = (basewidth/float(logo.size[0]))
    hsize = int((float(logo.size[1])*float(wpercent)))
    logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)
    return logo





def add_qrdata(data, color, logo=None):
    QRcode = qrcode.QRCode( version= 3,
	error_correction=qrcode.constants.ERROR_CORRECT_H)
    QRcode.add_data(data)
    QRcode.make(fit=True)
    QRimg = QRcode.make_image( fill_color=color, back_color="white").convert('RGB')
    if logo is not None:
        pos = ((QRimg.size[0] - logo.size[0]) // 2,
              (QRimg.size[1] - logo.size[1]) // 2)
        QRimg.paste(logo, pos)
    return QRimg

# save the QR code generated
def save_qrcode(QRimg, pathname):
    QRimg.save(pathname)
    print('QR code generated!')
