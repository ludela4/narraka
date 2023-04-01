import AppKit
class AppDelegate(AppKit.NSObject):
    def initWithBaseware_(self, base_ware):
        self = super().init()
        if self:
            self.baseWare = base_ware
        return self
    def applicationDidFinishLaunching_(self, notification):
        mainMenu = AppKit.NSMenu.alloc().init()
        
        editMenuItem = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Edit', None, '')
        editMenu = AppKit.NSMenu.alloc().init()
        
        copyItem = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Copy', 'copy:', 'c')
        pasteItem = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_('Paste', 'paste:', 'v')

        editMenu.addItem_(copyItem)
        editMenu.addItem_(pasteItem)

        editMenuItem.setSubmenu_(editMenu)
        mainMenu.addItem_(editMenuItem)

        AppKit.NSApp().setMainMenu_(mainMenu)
        self.baseWare.ghostBoot()
    