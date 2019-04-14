#!/usr/bin/env python
# coding: utf8

import os, sys, shutil, tempfile, subprocess, multiprocessing
from os.path import dirname, abspath, join

try:
    import configparser
except:
    import ConfigParser as configparser

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, Notify, Gdk, GdkPixbuf

gi.require_version('Gst', '1.0')
from gi.repository import Gst
Gst.init("")

APPNAME = "gSpeech"
SCRIPT_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))

import gettext
localdir = os.path.abspath(SCRIPT_DIR) + "/locale"
gettext.install(APPNAME, localdir)


root = dirname(dirname(abspath(__file__)))
sys.path.insert(0, join(root, 'wrappers/python'))
import speechtux

#########################
# Application info
ICON = os.path.join(SCRIPT_DIR, 'icons', APPNAME + '.svg')
VERSION = "0.7.0.0"
AUTHORNAME = "Lahire Biette,Sardi Carlo"
AUTHOREMAIL = "<tuxmouraille@gmail.com>,<lusumdev@zoho.eu>"
AUTHOR = AUTHORNAME + ' ' + AUTHOREMAIL
COMMENT = _("A little script to read SVOX 5 texts selected with the mouse.")
COPYRIGHT_YEAR = '2011,2014,2018'
COPYRIGHTS = u"Copyright © %s %s" % (COPYRIGHT_YEAR, AUTHORNAME)
AUTHORS = [
    _(u"Developers :"),
    u"%s" % (AUTHOR),
    #~ "",
    #~ _(u"Contributors:"),
]

TRANSLATORS = u"pt-PT, pt-BR, es-ES &amp; it-IT :\n\
Dupouy Paul"

#~ ARTISTS = []
WEBSITE = 'https://github.com/tuxmouraille/gSpeech'

LICENSE = """Copyright © %s - %s.

%s is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

%s is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with %s.  If not, see <http://www.gnu.org/licenses/>.
""" % (COPYRIGHT_YEAR, AUTHOR, APPNAME, APPNAME, APPNAME)

# Supported SVOX Pico's languages
LISTLANG = ["de-DE", "en-GB", "en-US", "es-ES", "fr-FR", "it-IT"]


# Temporaries files
CACHEFOLDER = os.getenv('HOME') + '/.cache/' + APPNAME + '/'

if not os.path.exists(CACHEFOLDER):
    os.makedirs(CACHEFOLDER)

# Main Class
class MainApp:
    """ the main class of the software """
    def __init__(self, config):
        # init app name in notification
        Notify.init('gSpeech')
        # define speech language
        self.lang = DefaultLang
        # select related icon
        #~ self.icon = APPNAME + '-' + self.lang
        self.icon = ICON

        self.config = config

        if IsAppIndicator == True :
            self.ind =appindicator.Indicator.new(APPNAME, self.icon, appindicator.IndicatorCategory.APPLICATION_STATUS)
            self.ind.set_status (appindicator.IndicatorStatus.ACTIVE)
            self.onRightClick(self)

        elif IsAppIndicator == False :
            # create GTK status icon
            self.tray = Gtk.StatusIcon()
            self.tray.set_from_file(self.icon) # select icon
            self.tray.connect('popup-menu', self.onRightClick) # right click
            self.tray.connect('activate', self.onLeftClick) # left click
            self.tray.set_tooltip_text((_(u"SVOX Pico simple GUI")))

        self.window = Gtk.Dialog(APPNAME,
                           None,
                           Gtk.DialogFlags.MODAL| Gtk.DialogFlags.DESTROY_WITH_PARENT)
        self.window.set_border_width(10)
        self.window.set_keep_above(True)
        self.window.set_icon_from_file(ICON)
        self.window.connect('delete-event', lambda w, e: w.hide() or True)

        hbox = Gtk.HBox()

        # Create an accelerator group
        self.accelgroup = Gtk.AccelGroup()
        # Add the accelerator group to the toplevel window
        self.window.add_accel_group(self.accelgroup)

        button = Gtk.Button()
        button.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_EXECUTE,Gtk.IconSize.MENU))
        button.set_label(_("Read clipboard content"))
        button.connect("clicked", self.onExecute)
        button.add_accelerator("clicked",self.accelgroup , ord('c'), Gdk.ModifierType.SHIFT_MASK, Gtk.AccelFlags.VISIBLE)
        hbox.pack_start(button, False, False,0)

        button = Gtk.Button()
        button.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_EXECUTE, Gtk.IconSize.MENU))
        button.set_label(_("Read selected text"))
        button.connect("clicked", self.onExecute)
        button.add_accelerator("clicked",self.accelgroup , ord('x'),Gdk.ModifierType.SHIFT_MASK, Gtk.AccelFlags.VISIBLE)
        hbox.pack_start(button, False, False,0)

        self.window.vbox.pack_start(hbox, False, False,0)

        hbox = Gtk.HBox()

        self.WinPlayPause = Gtk.Button(stock = Gtk.STOCK_MEDIA_PAUSE)
        self.WinPlayPause.connect("clicked", self.onPlayPause)
        button.add_accelerator("clicked",self.accelgroup , ord('p'),Gdk.ModifierType.SHIFT_MASK, Gtk.AccelFlags.VISIBLE)
        hbox.pack_start(self.WinPlayPause, False, False,0)

        button = Gtk.Button(stock = Gtk.STOCK_MEDIA_STOP)
        button.connect("clicked", self.onStop)
        button.add_accelerator("clicked",self.accelgroup , ord('q'), Gdk.ModifierType.SHIFT_MASK, Gtk.AccelFlags.VISIBLE)
        hbox.pack_start(button, False, False,0)

        button = Gtk.Button(stock = Gtk.STOCK_SAVE)
        button.connect("clicked", self.onSave)
        button.add_accelerator("clicked",self.accelgroup , ord('s'), Gdk.ModifierType.SHIFT_MASK, Gtk.AccelFlags.VISIBLE)
        hbox.pack_end(button, False, False,0)

        self.window.vbox.pack_start(hbox, False, False,0)

        hbox = Gtk.HBox()

        combobox = Gtk.ComboBoxText.new()
        hbox.pack_start(combobox, False, False,0)
        count = 0
        for i in LISTLANG:
            combobox.append_text(i)
            if i == self.lang:
                combobox.set_active(count)
            count += 1
        combobox.connect('changed', self.changed_cb)

        button = Gtk.Button(stock = Gtk.STOCK_CLOSE)
        #~ button.connect_object("clicked", Gtk.Widget.destroy, self.window)
        button.connect_object("clicked", Gtk.Widget.hide, self.window)
        hbox.pack_end(button, False, False,0)

        self.window.vbox.pack_start(hbox, False, False,0)

    def changed_cb(self, combobox):
        model = combobox.get_model()
        index = combobox.get_active()
        if index:
            self.onLang(self, model[index][0])
        return

    # action on right click
    def onRightClick(self, icon=None, event_button=None, event_time=None):
        # create menu
        menu = Gtk.Menu()

        # Execute menu item : execute speeching from Desktop clipboard
        rmItem = Gtk.MenuItem.new_with_label(_("Read clipboard content"))
        rmItem.connect('activate', self.onExecute)
        rmItem.show()
        menu.append(rmItem)

        # Execute menu item : execute speeching from X.org clipboard
        rmItem = Gtk.MenuItem.new_with_label(_("Read selected text"))
        rmItem.connect('activate', self.onExecute)
        rmItem.show()
        menu.append(rmItem)

        # Play item menu
        self.MenuPlayPause = Gtk.CheckMenuItem.new_with_label(_("Pause"))
        self.MenuPlayPause.set_active(False)
        self.MenuPlayPause.connect('toggled', self.onPlayPause)
        self.MenuPlayPause.show()
        menu.append(self.MenuPlayPause)

        # Stop  item menu
        rmItem = Gtk.MenuItem.new_with_label(_("Stop"))
        rmItem.connect('activate', self.onStop)
        rmItem.show()
        menu.append(rmItem)

        # Save item menu
        rmItem = Gtk.MenuItem.new_with_label(_("Save"))
        rmItem.connect('activate', self.onSave)
        rmItem.show()
        menu.append(rmItem)

        # Separator
        rmItem =  Gtk.SeparatorMenuItem()
        rmItem.show()
        menu.append(rmItem)

        mediawin =  Gtk.MenuItem.new_with_label(_("Multimedia window"))
        mediawin.connect('activate', self.onMediaDialog)
        mediawin.show()
        menu.append(mediawin)

        # Separator
        rmItem =  Gtk.SeparatorMenuItem()
        rmItem.show()
        menu.append(rmItem)

        # Open the dictionnary in default editor
        rmItem = Gtk.MenuItem.new_with_label(_(u"Open dictionary"))
        rmItem.connect('activate', self.onDictionnary)
        rmItem.show()
        menu.append(rmItem)

        # Preference item menu
        rmItem = Gtk.MenuItem.new_with_label(_(u"Languages"))
        rmItem.show()
        # Creating and linking langues submenu
        menulngs = Gtk.Menu()
        rmItem.set_submenu(menulngs)

        # Creating languages items in submenu
        # one empty item to initiate radioitem group
        smItem = Gtk.RadioMenuItem(None, None)
        for i in LISTLANG:
            # Creating new item
            #smItem = Gtk.RadioMenuItem(smItem, i, True)
            smItem = Gtk.RadioMenuItem.new_with_label_from_widget(smItem, i)
            # ... adding item in submenu
            menulngs.append(smItem)
            # linking it with onLang fonction
            smItem.connect("toggled", self.onLang, i)
            # i is defaut language activating radio button
            if i == self.lang :
                smItem.set_active(True)
            # show item
            smItem.show()

        menu.append(rmItem)

        ## Reload item menu
        item = Gtk.MenuItem.new_with_label(_("Refresh"))
        item.connect('activate', self.onReload)
        item.show()
        menu.append(item)

        # About item menu : show About dialog
        about = Gtk.MenuItem.new_with_label(_("About"))
        about.connect('activate', self.onAbout)
        about.show()
        menu.append(about)

        # Preferences
        options = Gtk.MenuItem.new_with_label(_("Options"))
        options.connect('activate', self.onOptions)
        options.show()
        menu.append(options)

        # Quit item menu
        item = Gtk.MenuItem.new_with_label(_("Quit"))
        item.connect('activate', self.destroy)
        item.show()
        menu.append(item)

        if IsAppIndicator == True :
            menu.show()
            self.ind.set_menu(menu)

        elif IsAppIndicator == False :
            menu.popup(None, None, None,self.tray, event_button, event_time)


    ## open the dictionnary file
    def onDictionnary(self, widget):
        lngDict = CONFIGDIR + '/' + self.lang + '.dic'

        if not os.path.exists(lngDict) :
            open(lngDict, 'a').close()

        os.system('xdg-open "%s"' % ( lngDict ))


    ## onReload item function: reload script
    def onReload(self, widget):
        myscript = os.path.abspath(sys.argv[0])
        subprocess.Popen(myscript)
        sys.exit()

    ## action on language submenu items
    def onLang(self, widget, lng):
        self.lang = lng
        #~ self.icon = APPNAME + '-' + self.lang
        self.icon = os.path.join(SCRIPT_DIR, 'icons', APPNAME + '-' + self.lang + '.svg')

        if IsAppIndicator == True :
            self.ind.set_icon(self.icon)

        elif IsAppIndicator == False :
            self.tray.set_from_file(self.icon)

    # show about dialog
    def onAbout(self, widget):
        self.aboutdiag = AboutDialog()

    # show options dialog
    def onOptions(self, widget):
        self.options_dialog = OptionDialog(self.config)

    # show multimedia control dialog
    def onMediaDialog(self, widget):
        if self.window.get_property('visible'):
            self.window.hide()
        else :
            self.window.show_all()

    # error message on playing function
    def onMessage(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            #file ended, stop
            self.player.set_state(Gst.State.NULL)
        elif t == Gst.MessageType.ERROR:
            #Error ocurred, print and stop
            self.player.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            print("Error: %s" % err, debug)

    # left click on status icon function
    # function like this and not merge with onExecute
    # to have possibility to use for something different
    def onLeftClick(self, widget, data=None):
        self.onExecute(self, widget)

    # on Execute item function : execute speech
    def onExecute(self, widget, data=None):
        if widget.get_label() == _("Read selected text") :
            text = Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY).wait_for_text()
        else :
            text = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).wait_for_text()

        if text == None:
            if self.config.show_notification:
                try:
                    Notify.Notification.new(APPNAME, _("No text selected."), self.icon).show()
                except:
                    pass
        else :
            if self.config.show_notification:
                try:
                    Notify.Notification.new(APPNAME, _(u"I'm reading the text. One moment please."), self.icon).show()
                except:
                    pass
            speechtux.read(text)

            if hasattr(self, 'player'):
                self.player.set_state(Gst.State.NULL)
            #player = self.onPlayer(SPEECH)
            self.player.set_state(Gst.State.PLAYING)
            self.buttonState()


    # player fonction
    def onPlayer(self,file):
        #Element playbin automatic plays any file
        self.player = Gst.ElementFactory.make("playbin", "player")
        #self.player = Gst.ElementFactory.make("playbin", None)
        #Set the uri to the file
        self.player.set_property("uri", "file://" + file)
        #Enable message bus to check for errors in the pipeline
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.onMessage)

    # play, pause and stop function for respectivs items
    def onPlayPause(self, widget, data=None):
        if widget.get_label() == Gtk.STOCK_MEDIA_PLAY or (hasattr(widget,'get_active') and widget.get_active() == False):
            self.player.set_state(Gst.State.PLAYING)
        else:
            self.player.set_state(Gst.State.PAUSED)
        self.buttonState()

    def onStop(self, widget, data=None):
        self.player.set_state(Gst.State.NULL)
        self.buttonState()

    def buttonState(self):
        #block handler cause set_active activate the function onPlayPause
        self.MenuPlayPause.handler_block_by_func(self.onPlayPause)
        if Gst.State.PLAYING == self.player.get_state(Gst.CLOCK_TIME_NONE)[1] :
            self.WinPlayPause.set_label(Gtk.STOCK_MEDIA_PAUSE)
            self.MenuPlayPause.set_active(False)

        elif Gst.State.PAUSED == self.player.get_state(Gst.CLOCK_TIME_NONE)[1] or Gst.State.NULL == self.player.get_state(Gst.CLOCK_TIME_NONE)[1] :
            self.WinPlayPause.set_label(Gtk.STOCK_MEDIA_PLAY)
            self.MenuPlayPause.set_active(True)
        self.MenuPlayPause.handler_unblock_by_func(self.onPlayPause)

    # saving file speech on clicking Save item
    def onSave(self, widget, data=None):
        SaveFile()

    # destroy app on clicking Quit item
    def destroy(self, widget, data=None):
        # quit program
        Gtk.main_quit()

    def main(self):
        Gtk.main()

# About dialog class
class AboutDialog:
    """ the about dialog class """
    def __init__(self):
        # Create AboutDialog object
        dialog = Gtk.AboutDialog()
        #~ dialog.set_logo_icon_name(APPNAME)
        dialog.set_logo(GdkPixbuf.Pixbuf.new_from_file(ICON))
        dialog.set_name(APPNAME)
        dialog.set_version(VERSION)
        dialog.set_copyright(COPYRIGHTS)
        dialog.set_license(LICENSE)
        dialog.set_authors(AUTHORS)
        dialog.set_comments(COMMENT)
        dialog.set_translator_credits(TRANSLATORS)
        dialog.set_website(WEBSITE)
        dialog.set_website_label(_("%s's Website") % APPNAME)
        #~ dialog.set_artists(ARTISTS)

        dialog.connect("response", lambda self, *f: self.destroy())
        dialog.show_all()

class OptionDialog:
    """ the options dialog class """
    def __init__(self, config):
        dialog = Gtk.Dialog(
            APPNAME,
            None,
            Gtk.DialogFlags.MODAL| Gtk.DialogFlags.DESTROY_WITH_PARENT
        )
        dialog.set_name(APPNAME)
        dialog.set_border_width(10)
        hbox = Gtk.HBox()
        notification_check = Gtk.CheckButton(_("Active notification"))
        notification_check.set_active(config.show_notification)
        notification_check.connect("toggled", self.on_checked, config)
        hbox.add(notification_check)
        dialog.vbox.pack_start(hbox, False, False, 0)
        dialog.show_all()

    def on_checked(self, checkBox, config):
        config.show_notification = checkBox.get_active()
        config.update()

# Audio speech wav file class saving
class SaveFile:
    """ the class to save the speech .wav file """
    def __init__(self):
        dialog = Gtk.FileChooserDialog(_("Save the speech"),
                                       None,
                                       Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OK, Gtk.ResponseType.OK))
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.set_current_folder(os.path.expanduser('~'))

        #~ dialog.set_modal(False)
        #~ dialog.set_transient_for(window)
        #~ dialog.set_decorated(False)

        filter = Gtk.FileFilter()
        filter.set_name(_(u"Wave file (*.wav)"))
        filter.add_mime_type("audio/x-wav")
        filter.add_pattern("*.wav")
        dialog.add_filter(filter)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename2 = dialog.get_filename()
            filename2 = filename2 + '.wav'
            shutil.copy(SPEECH, filename2)

        dialog.destroy()


def IniRead(configfile, section, key, default):
    if os.path.isfile(configfile):
        parser = configparser.SafeConfigParser()
        parser.read(configfile)

        try:
            var = parser.get( section , key )
        except:
            var = default
    else:
        var = default

    if var.lower() in ['1', 'yes', 'true', 'on'] :
        return True
    elif var.lower() in ['0', 'no', 'false', 'off'] :
        return False
    else :
        return var

class Config:
    _path = ''
    use_appindicator = True
    default_language = ''
    section = 'CONFIGURATION'
    show_notification = True

    def __init__(self, path):
        self._path = path
        raw = configparser.ConfigParser()
        raw.read(self._path)
        if raw.has_option(self.section, 'shownotification'):
            self.show_notification = raw.getboolean(
                self.section,
                'shownotification'
            )

    def update(self):
        raw = ConfigParser.RawConfigParser()
        raw.add_section(self.section)
        raw.set(
            self.section,
            'USEAPPINDICATOR',
            self.use_appindicator
        )
        raw.set(
            self.section,
            'DEFAULTLANGUAGE',
            self.default_language
        )
        raw.set(
            self.section,
            'SHOWNOTIFICATION',
            self.show_notification
        )
        with open(self._path, 'wb') as configfile:
            raw.write(configfile)

if __name__ == "__main__":
    CONFIGDIR = os.path.join(os.path.expanduser('~'), '.config/gSpeech')
    print(CONFIGDIR)
    #if not os.path.isdir(CONFIGDIR):
    #    os.mkdir(CONFIGDIR, 0775)

    CONFIGFILE = os.path.join(CONFIGDIR, 'gspeech.conf')
    if not os.path.isfile(CONFIGFILE) :
        raw = ConfigParser.RawConfigParser()
        raw.add_section('CONFIGURATION')
        raw.set('CONFIGURATION', 'USEAPPINDICATOR', 'True')
        raw.set('CONFIGURATION', 'DEFAULTLANGUAGE', '')
        #~ config.set('CONFIGURATION', 'SHOWMEDIADIALOG', 'False')
        with open(CONFIGFILE, 'wb') as configfile:
            raw.write(configfile)

    IsAppIndicator = bool(IniRead(CONFIGFILE, 'CONFIGURATION', 'USEAPPINDICATOR', 'True' ))

    DefaultLang = str(IniRead(CONFIGFILE, 'CONFIGURATION', 'DEFAULTLANGUAGE', '' ))
    DefaultLang = DefaultLang[ : 2 ] + '-' + DefaultLang[ 3 : ][ : 2 ]
    # if SVOX Pico not support this language, find os environment language
    if not DefaultLang in LISTLANG :
        DefaultLang = os.environ.get('LANG', 'en_US')[ : 2 ] + '-' + os.environ.get('LANG', 'en_US')[ 3 : ][ : 2 ]
        # if SVOX Pico not support this language, use US english
        if not DefaultLang in LISTLANG :
            DefaultLang = "en-US"

    try :
        gi.require_version('AppIndicator3', '0.1')
        from gi.repository import AppIndicator3 as appindicator
    except :
        IsAppIndicator = False


    config = Config(CONFIGFILE)
    config.use_appindicator = IsAppIndicator
    config.default_language = DefaultLang
    gSpeech = MainApp(config)
    gSpeech.main()

