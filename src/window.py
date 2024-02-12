# window.py
#
# Copyright 2021 Hennie
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math
import socket
import getpass
import os
import os.path
import sys
import urllib.parse
import urllib.request
import re
from os.path import expanduser
from gi.repository import Gtk, Gdk, GdkPixbuf, cairo, Pango

mp3_enabled = True
cddb_enabled = True
cdtext_enabled = True

try:
    from eyed3 import id3
except:
    mp3_enabled = False
    print("WARNING: eyed3 not found - disabling MP3/ID3 support")

try:
    import cdio
    import pycdio
except:
    cdtext_enabled = False
    print("WARNING: pycdio not found - disabling CDTEXT support")

try:
    import discid
except:
    cddb_enabled = False
    print("WARNING: discid not found - disabling CDDB support")

mm_to_pt = 72/25.4
factor = 1.015
mt = 121
mt2 = 151
mt3 = 118
mt4 = 124
img = None
img2 = None
wrp = False
dec = False


@Gtk.Template(resource_path='/org/molenkamp/Label/window.ui')
class CdlabelWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'CdlabelWindow'

    header_bar = Gtk.Template.Child()
    artist_entry = Gtk.Template.Child("artist_entry")
    title_entry = Gtk.Template.Child()
    genre_entry = Gtk.Template.Child()
    year_entry = Gtk.Template.Child()
    text1 = Gtk.Template.Child()
    button_bold = Gtk.Template.Child()
    button_italic = Gtk.Template.Child()
    button_underline = Gtk.Template.Child()
    textbuffer = Gtk.Template.Child()
    button_cddb = Gtk.Template.Child()
    button_mp3 = Gtk.Template.Child()
    text_colorbutton = Gtk.Template.Child()
    second_colorbutton = Gtk.Template.Child()
    background_colorbutton = Gtk.Template.Child()
    style_combo = Gtk.Template.Child()
    image_select = Gtk.Template.Child()
    image_back_select = Gtk.Template.Child()
    use_image = Gtk.Template.Child()
    use_back_image = Gtk.Template.Child()
    use_full = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        tag_bold = self.textbuffer.create_tag("bold", weight=Pango.Weight.BOLD)
        tag_italic = self.textbuffer.create_tag(
            "italic", style=Pango.Style.ITALIC)
        tag_underline = self.textbuffer.create_tag(
            "underline", underline=Pango.Underline.SINGLE)

        self.button_bold.connect("clicked", self.on_button_clicked, tag_bold)
        self.button_italic.connect(
            "clicked", self.on_button_clicked, tag_italic)
        self.button_underline.connect(
            "clicked", self.on_button_clicked, tag_underline)

        if not cddb_enabled:
            self.button_cddb.set_sensitive(False)

        if not mp3_enabled:
            self.button_mp3.set_sensitive(False)

        self.image_select.set_sensitive(False)
        self.image_back_select.set_sensitive(False)

    @Gtk.Template.Callback()
    def on_use_image_toggled(self, widget):
        print("widget is;", widget)
        if widget.get_active():
            self.image_select.set_sensitive(True)
            self.background_colorbutton.set_rgba(Gdk.RGBA(1.0, 1.0, 1.0, 1.0))
            #self.background_colorbutton.set_sensitive(False)
        else:
            self.image_select.set_sensitive(False)
            #self.background_colorbutton.set_sensitive(True)

    @Gtk.Template.Callback()
    def on_use_back_image_toggled(self, widget):
        if widget.get_active():
            self.image_back_select.set_sensitive(True)
            self.use_full.set_sensitive(True)
            self.background_colorbutton.set_rgba(Gdk.RGBA(1.0, 1.0, 1.0, 1.0))
            #self.background_colorbutton.set_sensitive(False)
        else:
            self.image_back_select.set_sensitive(False)
            self.use_full.set_active(False)
            self.use_full.set_sensitive(False)
            #self.background_colorbutton.set_sensitive(True)

    @Gtk.Template.Callback()
    def on_use_full_toggled(self, widget):
         if widget.get_active():
             print("raak!")

    def begin_print(self, operation, print_ctx, print_data):
        # operation.set_n_pages(self.doc.get_n_pages())
        operation.set_n_pages(1)

    def draw_page(self, operation, print_ctx, page_num, print_data):
        w = self.style_combo
        model = w.get_model()
        itr = w.get_active_iter()
        case = model.get_value(itr, 1)

        cr = print_ctx.get_cairo_context()
        width = print_ctx.get_width()

        artist = self.artist_entry.get_text()
        (x, y, w, h, dx, dy) = cr.text_extents(artist)
        title = self.title_entry.get_text()
        te = cr.text_extents(title)
        artist_id = Gtk.Buildable.get_name(self.artist_entry)
        text_color = self.text_colorbutton.get_color()
        print(text_color)
        second_color = self.second_colorbutton.get_color()
        print(second_color)
        bg_color = self.background_colorbutton.get_color()

        im = self.use_image.get_active()
        im2 = self.use_back_image.get_active()
        img = self.image_select.get_filename()
        img2 = self.image_back_select.get_filename()
        wrp = self.use_full.get_active()

        pbd = GdkPixbuf.Pixbuf.new_from_file("/home/hennie/Afbeeldingen/2031/IMG_20211229_143456.jpg")


        if img is not None:
            pb = GdkPixbuf.Pixbuf.new_from_file(img)

            pb_width = pb.get_width()
            pb_height = pb.get_height()

            scale1 = mt * mm_to_pt/pb_width
            scale2 = mt * mm_to_pt/pb_height

        if img2 is not None:
            pb2 = GdkPixbuf.Pixbuf.new_from_file(img2)

            pb_width = pb2.get_width()
            pb_height = pb2.get_height()

            wrp = self.use_full.get_active()
            if wrp == False:
                scale3 = (mt2 - 6 - 7) * mm_to_pt/pb_width
                scale4 = mt3 * mm_to_pt/pb_height
            elif wrp == True:
                scale3 = mt2 * mm_to_pt/pb_width
                scale4 = mt3 * mm_to_pt/pb_height



        if case == 1:
            cr.set_line_width(0.5)
            cr.set_tolerance(0.1)

            if im == True and img is not None:
                cr.save()
                cr.translate(40, mt * mm_to_pt + 40)
                cr.scale(scale1, scale2)
                cr.rotate(-90*math.pi/180)
                Gdk.cairo_set_source_pixbuf(cr, pb, 0, 0)
                cr.paint()
                cr.restore()

            cr.rectangle(40, 40, mt * mm_to_pt, mt * mm_to_pt)
            cr.rectangle(40, mt * mm_to_pt + 40, mt * mm_to_pt, mt * mm_to_pt)
            if im == False:
                cr.stroke_preserve()
                cr.set_source_rgba(
                     bg_color.red / 65535, bg_color.green / 65535, bg_color.blue / 65535, 0.5)
                cr.fill()
            elif im == True:
                cr.set_source_rgba(0.0 ,0.0 ,0.0 ,1.0)
                cr.stroke()

            if im == False:
                cr.select_font_face("Purisa", cairo.FontSlant.NORMAL,
                                    cairo.FontWeight.BOLD)
                cr.set_font_size(20)
                cr.set_source_rgba(
                    text_color.red / 65535, text_color.green / 65535, text_color.blue / 65535, 0.8)

                (x, y, w, h, dx, dy) = cr.text_extents(artist)

                cr.save()
                cr.translate(70, mt * mm_to_pt/2 + 40 + w/2)
                cr.rotate(-90*math.pi/180)
                cr.show_text(artist)
                cr.restore()
                cr.stroke()

                cr.select_font_face("Purisa", cairo.FontSlant.NORMAL,
                                    cairo.FontWeight.NORMAL)
                cr.set_source_rgba(
                    second_color.red / 65535, second_color.green / 65535, second_color.blue / 65535, 0.8)

                te = cr.text_extents(title)

                cr.save()
                cr.translate(90, mt * mm_to_pt/2 + 40 + te.width/2)
                cr.rotate(-90*math.pi/180)
                cr.show_text(title)
                cr.restore()

                cr.stroke()

            text = self.textbuffer.get_text(
                self.textbuffer.get_start_iter(), self.textbuffer.get_end_iter(), False)

            cr.set_font_size(12)
            cr.move_to(100, 700)
            tx = 100
            for line in text.splitlines():
                cr.save()
                cr.translate(tx, 700)
                cr.rotate(-90*math.pi/180)
                cr.show_text(line)
                cr.stroke()
                cr.restore()
                tx = tx + 12
            #cr.stroke()

        elif case == 0:
            cr.set_line_width(0.5)
            cr.set_tolerance(0.1)
            #cr.set_source_rgb(0.0, 0.0, 0.0)
            start = 40 - 6 * mm_to_pt

            # rectangles
            cr.rectangle(40, 40, mt * mm_to_pt, mt * mm_to_pt)
            cr.rectangle(start, mt * mm_to_pt + 40,
                         6 * mm_to_pt, mt3 * mm_to_pt)
            cr.rectangle(40, mt * mm_to_pt + 40, (mt2 - 13)
                         * mm_to_pt, mt3 * mm_to_pt)
            cr.rectangle(mt2 * mm_to_pt + start - 7 * mm_to_pt,
                         mt * mm_to_pt + 40, 7 * mm_to_pt, mt3 * mm_to_pt)
            cr.rectangle(mt2 * mm_to_pt + start, mt * mm_to_pt + 1.5 *
                         mm_to_pt + 40, 9 * mm_to_pt, (mt3 * mm_to_pt) - (3 * mm_to_pt))

            if im == False:
                cr.set_source_rgba(
                     bg_color.red / 65535, bg_color.green / 65535, bg_color.blue / 65535, 0.5)
                cr.fill_preserve()
                cr.set_source_rgba(0.0, 0.0, 0.0, 1.0)
                cr.stroke()
            elif im == True:
                cr.set_source_rgba(0.0, 0.0, 0.0, 1.0)
                cr.stroke()

            if im == True and img is not None:
                cr.save()
                cr.translate(40, 40)
                cr.scale(scale1, scale2)
                Gdk.cairo_set_source_pixbuf(cr, pb, 0, 0)
                cr.paint()
                cr.restore()

            if im2 == True and img2 is not None:
                cr.save()
                if wrp == True:
                    cr.translate(start, 40 + mt * mm_to_pt)
                elif wrp == False:
                    cr.translate(40, 40 + mt * mm_to_pt)
                cr.scale(scale3, scale4)
                Gdk.cairo_set_source_pixbuf(cr, pb2, 0, -2)
                cr.paint()
                cr.restore()

            if im == False and dec == True:
                print("deco is", dec)
                cr.save()
                cr.translate(100, 100)
                cr.scale(0.2, 0.2)
                Gdk.cairo_set_source_pixbuf(cr, pbd, 0, 0)
                cr.paint()
                cr.restore()


            cr.select_font_face("Purisa", cairo.FontSlant.NORMAL,
                                        cairo.FontWeight.BOLD)
            cr.set_font_size(20)
            cr.set_source_rgba(
                    text_color.red / 65535, text_color.green / 65535, text_color.blue / 65535, 0.8)
            (x, y, w, h, dx, dy) = cr.text_extents(artist)

            if im == False:
                cr.move_to(40 + mt/2 * mm_to_pt - w/2, 70)
                cr.show_text(artist)
                cr.stroke()


            cr.set_font_size(10)
            cr.move_to(35, 710)
            cr.save()
            cr.translate(35, 710)
            cr.rotate(-90*math.pi/180)
            cr.show_text(artist)
            cr.restore()
            cr.stroke()

            cr.save()
            cr.translate(437, 390)
            cr.rotate(90*math.pi/180)
            cr.show_text(artist)
            cr.restore()
            cr.stroke()

            cr.save()
            cr.translate(465, 700)
            cr.rotate(-90*math.pi/180)
            cr.show_text(artist)
            cr.restore()
            cr.stroke()

            cr.select_font_face("Purisa", cairo.FontSlant.NORMAL,
                                cairo.FontWeight.NORMAL)
            cr.set_font_size(20)
            cr.set_source_rgba(
                second_color.red / 65535, second_color.green / 65535, second_color.blue / 65535, 0.8)

            te = cr.text_extents(title)
            if im == False:
                cr.move_to(40 + mt/2 * mm_to_pt - te.width/2, 90)
                cr.show_text(title)
                cr.stroke()

            cr.set_font_size(10)
            cr.save()
            cr.translate(35, 515)
            cr.rotate(-90*math.pi/180)
            cr.show_text(title)
            cr.restore()
            cr.stroke()

            cr.save()
            cr.translate(437, 590)
            cr.rotate(90*math.pi/180)
            cr.show_text(title)
            cr.restore()
            cr.stroke()

            cr.save()
            cr.translate(465, 515)
            cr.rotate(-90*math.pi/180)
            cr.show_text(title)
            cr.restore()
            cr.stroke()

            text = self.textbuffer.get_text(
                self.textbuffer.get_start_iter(), self.textbuffer.get_end_iter(), False)

            cr.set_font_size(12)
            ty = 420
            tx = 60
            for line in text.splitlines():
                cr.move_to(tx, ty)
                cr.show_text(line)
                cr.stroke()
                ty = ty + 12
            #cr.stroke()


        elif case == 2:
            cr.set_line_width(0.5)
            cr.set_tolerance(0.1)

            cr.move_to(60, 80)
            cr.line_to(60 + 5 * mm_to_pt, 5)
            cr.line_to(60 + (114 + 5) * mm_to_pt, 5)
            cr.line_to(60 + mt4 * mm_to_pt, 80)

            cr.line_to(60 + (mt4 + 15) * mm_to_pt, 80 + 8 * mm_to_pt)
            cr.line_to(60 + (mt4 + 15) * mm_to_pt, 80 + (mt4 - 8) * mm_to_pt)
            cr.line_to(60 + mt4 * mm_to_pt, 80 + mt4 * mm_to_pt)

            cr.move_to(60, 80)
            cr.line_to(60 - 15 * mm_to_pt, 80 + (8 * mm_to_pt))
            cr.line_to(60 - 15 * mm_to_pt, 80 + (mt4 - 8) * mm_to_pt)
            cr.line_to(60, 80 + mt4 * mm_to_pt)

            #cr.rectangle(75, 10, 114 * mm_to_pt, 50)
            cr.rectangle(60, 80, mt4 * mm_to_pt, mt4 * mm_to_pt)
            #cr.rectangle(60 + 2 * mm_to_pt, mt4 * mm_to_pt + 80, mt * mm_to_pt - 2 * mm_to_pt, mt * mm_to_pt)
            cr.rectangle(60, mt4 * mm_to_pt + 80,
                         mt4 * mm_to_pt, mt * mm_to_pt)
            if im == False:
                cr.stroke_preserve()
                cr.set_source_rgba(
                     bg_color.red / 65535, bg_color.green / 65535, bg_color.blue / 65535, 0.5)
                cr.fill()
            elif im == True:
                cr.stroke

            text = self.textbuffer.get_text(
                        self.textbuffer.get_start_iter(), self.textbuffer.get_end_iter(), False)

            if im == True and img is not None:
                scale5 = mt4 * mm_to_pt/pb.get_width()
                scale6 = mt4 * mm_to_pt/pb.get_height()
                cr.save()
                cr.translate(60, 80)
                cr.scale(scale5, scale6)
                Gdk.cairo_set_source_pixbuf(cr, pb, 0, 0)
                cr.paint()
                cr.restore()
            else:
                cr.select_font_face("Purisa", cairo.FontSlant.NORMAL,
                                        cairo.FontWeight.BOLD)
                cr.set_font_size(20)
                cr.set_source_rgba(
                    text_color.red / 65535, text_color.green / 65535, text_color.blue / 65535, 0.8)

                (x, y, w, h, dx, dy) = cr.text_extents(artist)

                cr.move_to(60 + mt4/2 * mm_to_pt - w/2, 110)
                cr.show_text(artist)
                cr.stroke()

                cr.select_font_face("Purisa", cairo.FontSlant.NORMAL,
                                    cairo.FontWeight.NORMAL)
                cr.set_font_size(20)
                cr.set_source_rgba(
                    second_color.red / 65535, second_color.green / 65535, second_color.blue / 65535, 0.8)

                te = cr.text_extents(title)
                cr.move_to(60 + mt4/2 * mm_to_pt - te.width/2, 130)
                cr.show_text(title)
                cr.stroke()

            cr.set_font_size(12)
            cr.move_to(360,720)
            ty = 720
            for line in text.splitlines():
                cr.save()
                cr.translate(360, ty)
                cr.rotate(-180*math.pi/180)
                cr.show_text(line)
                cr.stroke()
                cr.restore()
                ty = ty - 12
            cr.stroke()


    @Gtk.Template.Callback()
    def get_file(self, widget):
        file = widget.get_filename()
        dmap = widget.get_current_folder()
        print("map is:", dmap)
        print(file)

    @Gtk.Template.Callback()
    def on_print_button_clicked(self, widget):
        operation = Gtk.PrintOperation()
        # operation.set_n_pages(1)
        page_setup = Gtk.PageSetup()
        page_setup.set_orientation(Gtk.PageOrientation.PORTRAIT)

        operation.set_default_page_setup(page_setup)
        operation.connect("begin_print", self.begin_print, None)
        operation.connect("draw_page", self.draw_page, None)
        result = operation.run(Gtk.PrintOperationAction.PRINT_DIALOG,
                               None)

        if result == Gtk.PrintOperationResult.ERROR:
            message = self.operation.get_error()

            dialog = Gtk.MessageDialog(parent,
                                       0,
                                       Gtk.MessageType.ERROR,
                                       Gtk.ButtonsType.CLOSE,
                                       message)

            dialog.run()
            dialog.destroy()

        Gtk.main_quit()

    @Gtk.Template.Callback()
    def on_clear_clicked(self, widget):
        textbuffer = self.text1.get_buffer()
        start = textbuffer.get_start_iter()
        end = textbuffer.get_end_iter()
        textbuffer.remove_all_tags(start, end)
        textbuffer.set_text("")

    # @Gtk.Template.Callback()
    def on_button_clicked(self, widget, tag):
        bounds = self.textbuffer.get_selection_bounds()
        if len(bounds) != 0:
            start, end = bounds
            self.textbuffer.apply_tag(tag, start, end)

    @Gtk.Template.Callback()
    def on_button_cddb_clicked(self, widget):

        device_name = discid.get_default_device()
        #disc = discid.read(device='/dev/cdrom', features=["mcn", "isrc"])
        disc = discid.read(device_name, ["mcn", "isrc"])

        offsets = []
        checksum = 0

        for track in disc.tracks:
            checksum += self.cddb_sum(track.offset // 75)
            offsets.append(track.offset)

        offsets.append(disc.sectors)

        total_time = (offsets[-1] // 75) - (offsets[0] // 75)
        last = len(offsets) - 1

        disc_id = ((checksum % 0xff) << 24 | total_time << 8 | last)
        cdinfo = [last] + offsets[:-1] + [offsets[-1] // 75]

        proto = 5
        server = 'http://gnudb.gnudb.org/~cddb/cddb.cgi'
        host = socket.gethostname() or 'host'
        user = getpass.getuser()
        version = 0
        app = "gtkcdlabel"

        did = '%08lx' % disc_id
        info = cdinfo[0:]

        string = [str(int) for int in info]
        query = "+".join(string)

        url = "%s?cmd=cddb+query+%s+%s&hello=%s+%s+%s+%s&proto=%d" % \
            (server, did, query, user, host, app, version, proto)
        res = urllib.request.urlopen(url)
        header = res.readline().decode('latin-1').rstrip()
        arr = header.split(' ', 3)
        rc = int(arr[0])

        if rc == 200:
            result = {'category': arr[1], 'disc_id': arr[2], 'title':
                      arr[3]}
            cat = arr[1]
            did = arr[2]
        elif rc in (210, 211):
            result = []
            line = res.readline().decode('latin-1').rstrip()
            while line != ".":
                info = line.split(' ', 2)
                result.append(
                    {'category': info[0], 'disc_id': info[1], 'title': info[2]})
                line = res.readline().decode('latin-1').rstrip()
            cat = (result[1]['category'])

        elif rc == 202:
            self.error_dialog(
                "CDDB Error", "Did cddb query, but this CD is not listed.")
        else:
            self.error_dialog(
                "CDDB Error", "Did cddb query, but it got an error. The return code is %s" % rc)

        url = "%s?cmd=cddb+read+%s+%s&hello=%s+%s+%s+%s&proto=%d" % \
            (server, cat, did, user, host, app, version, proto)
        res = urllib.request.urlopen(url)
        header = res.readline().decode('latin-1').rstrip()
        rc = int(header.split(' ', 1)[0])
        if not rc == 210:
            self.error_dialog(
                "CDDB Error", "CD database had an error when I tried to read track info (return code=%d)" % rc)

        reply = []
        tracks = []

        for line in res.readlines():
            line = line.decode('latin-1').rstrip()
            m = re.match("DTITLE=(?P<dtitle>.*)", line)
            if m:
                m = re.match(
                    '(?P<artist>[^\/]*)\/(?P<album>[^\/]*)', m.group("dtitle"))
                if m:
                    album_field = self.artist_entry
                    album_field2 = self.title_entry
                    album_field.set_text(m.group('artist').rstrip())
                    album_field2.set_text(m.group('album').lstrip())
            m = re.match("DYEAR=(?P<year>.*)", line)
            if m:
                album_field = self.year_entry
                album_field.set_text(m.group("year"))
            m = re.match("DGENRE=(?P<genre>.*)", line)
            if m:
                album_field = self.genre_entry
                album_field.set_text(m.group("genre"))
            m = re.match("TTITLE(?P<num>[^=]*)=(?P<title>.*)", line)
            if m:
                if not tracks:
                    tracks = []
                textbuffer = self.text1.get_buffer()
                iter = textbuffer.get_end_iter()
                textbuffer.insert(iter, ("%s. %s\n") %
                                  (int(m.group("num")) + 1, m.group("title")))
                tracks.append(m.group("title"))

    @Gtk.Template.Callback()
    def on_cdtextbutton_clicked(self, widget):
        try:
            d = cdio.Device(driver_id=pycdio.DRIVER_UNKNOWN)
            drive_name = d.get_device()
        except IOError:
            sys.exit(1)

        cdt = d.get_cdtext()
        i_tracks = d.get_num_tracks()
        i_first_track = pycdio.get_first_track_num(d.cd)

        performer = cdt.get(pycdio.CDTEXT_FIELD_PERFORMER, 0)
        title = cdt.get(pycdio.CDTEXT_FIELD_TITLE, 0)

        if performer is not None:
            self.artist_entry.set_text(performer)
        if title is not None:
            self.title_entry.set_text(title)

        for t in range(i_first_track, i_tracks + i_first_track):
            performer = cdt.get(pycdio.CDTEXT_FIELD_PERFORMER, t)
            if performer is None:
                performer = ""
            title = cdt.get(pycdio.CDTEXT_FIELD_TITLE, t)
            textbuffer = self.text1.get_buffer()
            iter = textbuffer.get_end_iter()
            textbuffer.insert(iter, ("%d. %s - %s\n") % (t, title, performer))
            pass
        return
        d.close()

    @Gtk.Template.Callback()
    def on_button_mp3_clicked(self, widget):
        home = expanduser("~")
        dialog = Gtk.FileChooserDialog(
            title="Selecteer een map",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Selecteer", Gtk.ResponseType.OK
        )
        #dialog.set_default_size(800, 400)

        dialog.set_current_folder(home)

        if dialog.run() == Gtk.ResponseType.OK:
            result = dialog.get_filename()
        dialog.destroy()

        print("path",result)
        firstmp3 = 0
        for root, dirs, files in os.walk(result):
            for name in sorted(files):
                p = os.path.join(root, name)
                print(p)
                if name.endswith(".mp3") or name.endswith(".MP3"):
                    if firstmp3 == 0:
                        textbuffer = self.text1.get_buffer()
                        iter = textbuffer.get_end_iter()
                        textbuffer.insert(iter, '\n %s\n' % root)
                    print(name)
                    tag = id3.Tag()
                    tag.parse(p)
                    artist = tag.artist
                    print(artist)
                    title = tag.title
                    print(title)
                    track_path = tag.file_info.name
                    textbuffer = self.text1.get_buffer()
                    iter = textbuffer.get_end_iter()
                    textbuffer.insert(
                        iter, '%d. %s - %s\n' % (firstmp3+1, artist, title))
                    firstmp3 += 1

    @Gtk.Template.Callback()
    def on_gtk_about_clicked(self, widget):
        dialog = Gtk.AboutDialog(transient_for=self)
        dialog.set_logo_icon_name('org.molenkamp.label')
        dialog.set_program_name('Gtkcdlabel')
        dialog.set_version("1.0")
        dialog.set_website('https://imeditor.github.io')
        dialog.set_authors(['Henny van Gameren'])
        gtk_version = '{}.{}.{}'.format(Gtk.get_major_version(),
            Gtk.get_minor_version(), Gtk.get_micro_version())
        comment = '{}\n\n'.format(_("Cdlabel creator"))
        comment += 'Gtk: {} Python: {}'.format(gtk_version, str(sys.version_info.major) + "." + str(sys.version_info.major) + "." + str(sys.version_info.micro))
        dialog.set_comments(comment)
        text = _("Distributed under the GNU GPL(v3) license.\n")
        text += 'https://www.gnu.org/licenses/gpl-3.0.html\n'
        dialog.set_license(text)
        dialog.run()
        dialog.destroy()


    def cddb_sum(self, n):
        ret = 0

        while n > 0:
            ret = ret + (n % 10)
            n = n // 10

        return ret
