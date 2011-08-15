# -*- coding: utf-8 -*-
# See LICENSE.txt for licensing terms

import os
import xml

from reportlab.platypus import Flowable, Paragraph
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from svglib import svglib

class SVGImage(Flowable):

    def __init__(self, svg_string, width=None, height=None, kind='direct'):
        Flowable.__init__(self)
        self._kind = kind
        s = svglib.SvgRenderer()
        doc = xml.dom.minidom.parseString(svg_string)
        svg_dom = doc.documentElement
        s.render(svg_dom)
        self.doc = s.finish()
        #self.doc = svglib.svg2rlg(filename)
        self.imageWidth = width
        self.imageHeight = height
        x1, y1, x2, y2 = self.doc.getBounds()
        self._w, self._h = x2, y2
        if not self.imageWidth:
            self.imageWidth = self._w
        if not self.imageHeight:
            self.imageHeight = self._h
        self.__ratio = float(self.imageWidth)/self.imageHeight
        if kind in ['direct','absolute']:
            self.drawWidth = width or self.imageWidth
            self.drawHeight = height or self.imageHeight
        elif kind in ['bound','proportional']:
            factor = min(float(width)/self.imageWidth,float(height)/self.imageHeight)
            self.drawWidth = self.imageWidth*factor
            self.drawHeight = self.imageHeight*factor

    def wrap(self, aW, aH):
        return self.drawWidth, self.drawHeight

    def drawOn(self, canv, x, y, _sW=0):
        if _sW and hasattr(self, 'hAlign'):
            a = self.hAlign
            if a in ('CENTER', 'CENTRE', TA_CENTER):
                x += 0.5*_sW
            elif a in ('RIGHT', TA_RIGHT):
                x += _sW
            elif a not in ('LEFT', TA_LEFT):
                raise ValueError("Bad hAlign value " + str(a))
        canv.saveState()
        canv.translate(x, y)
        canv.scale(self.drawWidth/self._w, self.drawHeight/self._h)
        self.doc._drawOn(canv)
        canv.restoreState()


if __name__ == "__main__":
    import sys
    from reportlab.platypus import SimpleDocTemplate
    from reportlab.lib.styles import getSampleStyleSheet
    doc = SimpleDocTemplate('svgtest.pdf')
    styles = getSampleStyleSheet()
    style = styles['Normal']
    svg_data = open(sys.argv[1]).read()
    Story = [Paragraph("Before the image", style),
             SVGImage(svg_data),
             Paragraph("After the image", style)]
    doc.build(Story)
