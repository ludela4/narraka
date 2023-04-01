import objc
import AppKit
import time
import threading
import glob
import re
import copy as cp
import chat
import importlib

import json
import os
from shell import Shell
from app_delegate import AppDelegate
from collections.abc import Iterable
import yaml
import os
import sys


def safe_path(path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, path)


def path_in_savedir(path):
    app_data_dir = os.path.expanduser('~/Library/Application Support/narraka')

    # ディレクトリが存在しない場合は作成
    if not os.path.exists(app_data_dir):
        os.makedirs(app_data_dir)
    path_in_dir = os.path.join(app_data_dir, path)
    return path_in_dir


def load_external_module(module_name, module_file):
    # base_path
    external_module_dir = safe_path("ghosts")
    if external_module_dir not in sys.path:
        sys.path.append(external_module_dir)

    # 外部モジュールをインポート
    spec = importlib.util.spec_from_file_location(
        module_name, os.path.join(external_module_dir, module_file))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


class DraggableAreaView(AppKit.NSView):
    def mouseDownCanMoveWindow(self) -> bool:
        return True


class ClickThroughTextView(AppKit.NSTextView):
    def mouseDown_(self, event):
        super().mouseDown_(event)
        self.window().mouseDown_(event)


class PlaceholderTextView(AppKit.NSTextView):
    def initWithFrame_placeholderString_(self, frame, placeholderString):
        self = super().initWithFrame_(frame)
        if self:
            self.placeholderString = placeholderString
        return self

    def drawRect_(self, rect):
        super().drawRect_(rect)
        if not self.string() and self.placeholderString:
            placeholderAttributes = {
                AppKit.NSFontAttributeName: AppKit.NSFont.systemFontOfSize_(12.0),
                AppKit.NSForegroundColorAttributeName: AppKit.NSColor.placeholderTextColor(),
            }
            placeholder = AppKit.NSAttributedString.alloc().initWithString_attributes_(
                self.placeholderString, placeholderAttributes)
            placeholder.drawAtPoint_(AppKit.NSMakePoint(5, 0))


class TextEntryWindowController(AppKit.NSObject):
    def init(self):
        self = super().init()

        return self

    def initWithAction_Placeholder_(self, action, placeholder):
        self = self.init()
        self.action = action
        self.placeholder = placeholder
        self.closed = True
        if self:

            self.window = AppKit.NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                AppKit.NSMakeRect(200, 200, 400, 100),
                AppKit.NSWindowStyleMaskTitled,
                AppKit.NSBackingStoreBuffered,
                False)
            self.textField = AppKit.NSTextField.alloc().initWithFrame_(
                AppKit.NSMakeRect(20, 50, 360, 30))
            self.setupWindow()
        return self

    def control_textView_doCommandBySelector_(self, control, textView, commandSelector):
        if commandSelector == "insertNewline:":
            self.submitText_(control)
            return True
        return False

    def setupWindow(self):
        self.window.setBackgroundColor_(AppKit.NSColor.whiteColor())
        self.window.setOpaque_(False)
        self.window.setTitle_(self.placeholder)

        self.window.setTitleVisibility_(AppKit.NSWindowTitleHidden)
        self.window.setTitlebarAppearsTransparent_(True)

        self.textField = AppKit.NSTextField.alloc().initWithFrame_(
            AppKit.NSMakeRect(20, 50, 360, 30))
        self.textField.setBezeled_(False)
        self.textField.setDrawsBackground_(True)
        self.textField.setBackgroundColor_(AppKit.NSColor.whiteColor())
        self.textField.setFocusRingType_(AppKit.NSFocusRingTypeNone)
        self.textField.cell().setWraps_(True)
        self.textField.cell().setScrollable_(True)
        self.textField.cell().setUsesSingleLineMode_(False)  # 追加
        self.textField.cell().setLineBreakMode_(AppKit.NSLineBreakByWordWrapping)  # 追加
        self.textField.cell().setPlaceholderString_(self.placeholder)
        self.textField.setDelegate_(self)
        self.window.contentView().addSubview_(self.textField)
        submitButton = AppKit.NSButton.alloc().initWithFrame_(
            AppKit.NSMakeRect(290, 10, 100, 30))
        submitButton.setBezelStyle_(AppKit.NSBezelStyleRounded)
        submitButton.setTitle_("送信")
        submitButton.setTarget_(self)
        submitButton.setAction_(b"submitText:")
        self.window.contentView().addSubview_(submitButton)
        cancelButton = AppKit.NSButton.alloc().initWithFrame_(
            AppKit.NSMakeRect(180, 10, 100, 30))
        cancelButton.setBezelStyle_(AppKit.NSBezelStyleRounded)
        cancelButton.setTitle_("キャンセル")
        cancelButton.setTarget_(self)
        cancelButton.setAction_(b"cancel:")
        self.window.contentView().addSubview_(cancelButton)
        self.window.setLevel_(AppKit.NSFloatingWindowLevel)

        return self

    def show(self):
        self.window.makeKeyAndOrderFront_(None)
        self.textField.becomeFirstResponder()
        self.closed = False

    def close(self):
        self.textField.setStringValue_("")
        self.window.orderOut_(None)
        self.closed = True

    def cancel_(self, sender):
        self.close()

    def submitText_(self, sender):
        text = self.textField.stringValue()
        self.close()
        self.action(text)


class DraggableImageView(AppKit.NSImageView):
    def initWithFrame_(self, frame):
        super().initWithFrame_(frame)

    def initWithFrame_Controller_ImagePath_(self, frame, controller, image_path):
        self.initWithFrame_(frame)
        # self.surfaces = sorted(glob.glob("shell/surface[0-9]*.png"))
        image = AppKit.NSImage.alloc().initWithContentsOfFile_(image_path)
        self.setImage_(image)
        self.controller = controller
        return self

    def setTalkWindowController_(self, talkWindowController):
        self.talkWindowController = talkWindowController

    def setSurface_(self, img_path):
        image = AppKit.NSImage.alloc().initWithContentsOfFile_(img_path)
        self.setImage_(image)
        self.window().invalidateShadow()

    def drawRect_(self, rect):
        # 背景を透明に描画
        AppKit.NSColor.clearColor().set()
        AppKit.NSRectFill(rect)

        # 画像を描画
        super().drawRect_(rect)

    def mouseDown_(self, event):
        self.mouseDownEvent = event
        self.initialWindowFrame = self.window().frame()
        self.mouseDownTime = time.time()
        self.controller.window.mouseDown_(event)

    def mouseUp_(self, event):
        elapsedTime = time.time() - self.mouseDownTime
        if self.mouseDownEvent.locationInWindow() == event.locationInWindow() and elapsedTime <= 0.2:
            self.controller.OnClicked()

    def rightMouseDown_(self, event):
        menu = self.createContextMenu()

        # メニューを表示
        AppKit.NSMenu.popUpContextMenu_withEvent_forView_(menu, event, self)

    def createContextMenu(self):
        # コンテキストメニューを作成
        menu = AppKit.NSMenu.alloc().init()

        # メニューアイテムを作成
        quitMenuItem = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "アプリの終了", objc.selector(AppKit.NSApp().terminate_), "")
        menu.addItem_(quitMenuItem)

        sendTextItem = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "文章を送信", objc.selector(self.sendText_), "")
        menu.addItem_(sendTextItem)

        registerApiItem = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "APIキーを登録", objc.selector(self.registerApiKey_), "")
        menu.addItem_(registerApiItem)

        changeGhostMenu = AppKit.NSMenu.alloc().init()
        # サブメニューアイテムを作成
        ghost_infos = getGhostInfos()
        for ghost_dir, ghost_name in ghost_infos.items():
            switchToGhost = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                f"{ghost_name}に切り替え", objc.selector(self.switchGhost_), ghost_dir)
            changeGhostMenu.addItem_(switchToGhost)

        # サブメニューをメインメニューに追加
        changeGhostMenuItem = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "ゴーストを切り替え", None, "")
        menu.addItem_(changeGhostMenuItem)
        menu.setSubmenu_forItem_(changeGhostMenu, changeGhostMenuItem)

        return menu

    def sendText_(self, sender):
        self.controller.baseWare.talkWindowController.textEntryWindowController.show()

    def registerApiKey_(self, sender):
        self.controller.baseWare.apiKeyController.show()

    def switchGhost_(self, sender):
        ghost_name = sender.keyEquivalent()
        self.controller.baseWare.changeGhost(ghost_name)


class DraggableWindow(AppKit.NSWindow):
    def init(self):
        self=super().init()
        # 新しい属性値を定義する
        self.closed = False
        self.baseWare = None
        return self
    
    def canBecomeKeyWindow(self):
        return True

    def setBaseWare_(self,base_ware):
        self.baseWare=base_ware

    def mouseDown_(self, event):
        self.mouseDownEvent = event
        self.performWindowDragWithEvent_(event)
        self.mouseDownTime = time.time()

    def mouseUp_(self, event):
        elapsedTime = time.time() - self.mouseDownTime
        if self.mouseDownEvent.locationInWindow() == event.locationInWindow() \
                and elapsedTime <= 0.2 \
                and self.baseWare and not self.baseWare.talkWindowController.talking:
            self.close()

    def close(self):
        self.orderOut_(None)
        self.closed = True

    def reload(self):
        if not self.isVisible():
            self.orderBack_(None)
        self.closed = False

    def open(self):
        if not self.isVisible():
            self.makeKeyAndOrderFront_(None)
        self.closed = False


class ImageWindowController(AppKit.NSObject):
    def initWithBaseWare_(self, baseWare):
        self = super().init()
        self.baseWare = baseWare
        self.window = DraggableWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            AppKit.NSMakeRect(0, 0, 500, 500),
            AppKit.NSWindowStyleMaskTitled | AppKit.NSWindowStyleMaskFullSizeContentView,
            AppKit.NSBackingStoreBuffered,
            False)
        self.setupWindow()
        return self

    def setupWindow(self):
        self.window.setBackgroundColor_(AppKit.NSColor.clearColor())
        self.window.setOpaque_(False)
        self.window.setHasShadow_(True)
        image_path = self.baseWare.shell.surfaces[0]
        self.imageView = DraggableImageView.alloc().initWithFrame_Controller_ImagePath_(
            self.window.contentView().frame(), self, image_path)
        self.window.contentView().addSubview_(self.imageView)

        self.window.setTitleVisibility_(AppKit.NSWindowTitleHidden)
        self.window.setTitlebarAppearsTransparent_(True)

        self.window.contentView().setWantsLayer_(True)
        self.window.contentView().superview().setWantsLayer_(True)
        self.window.contentView().superview().layer().setBorderWidth_(0)
        self.window.setLevel_(AppKit.NSFloatingWindowLevel)

    def setSurfaceId_(self, surface_id):
        img_path = self.baseWare.shell.surfaces[surface_id]
        self.imageView.setSurface_(img_path)

    def show(self):
        self.window.makeKeyAndOrderFront_(None)

    def OnClicked(self):
        if not self.baseWare.talkWindowController.talking:
            self.baseWare.talkWindowController.chatBackground_(
                self.baseWare.ghost.OnClicked())


class CursorChangingButton(AppKit.NSButton):
    def resetCursorRects(self):
        cursor = AppKit.NSCursor.pointingHandCursor()
        self.addCursorRect_cursor_(self.bounds(), cursor)
        cursor.setOnMouseEntered_(True)

    def mouseEntered_(self, event):
        AppKit.NSCursor.pointingHandCursor().push()

    def mouseExited_(self, event):
        AppKit.NSCursor.pop()


class TalkingContextManager:
    def __init__(self, controller):
        self.controller = controller

    def __enter__(self):
        self.controller.talking = True

    def __exit__(self, exc_type, exc_value, traceback):
        self.controller.talking = False


class TalkWindowController(AppKit.NSObject):
    def initWithBaseWare_(self, baseWare):
        self = super().init()
        if self:
            self.baseWare = baseWare
            self.window = DraggableWindow.alloc().initWithContentRect_styleMask_backing_defer_(
                AppKit.NSMakeRect(550, 0, 300, 200),
                AppKit.NSWindowStyleMaskTitled,
                AppKit.NSBackingStoreBuffered,
                False)
            self.window.setBaseWare_(baseWare)
            self.setupWindow()
            self.delay = 0.1
            self.messages = []
            self.talking = False
            self.textEntryWindowController = TextEntryWindowController.alloc(
            ).initWithAction_Placeholder_(self.talkMessage_, "文章を入力してください")
        return self

    def talkMessage_(self, text):
        message = {"role": "user", "content": text} if text != "" else None
        self.chatBackground_(message)

    def setupWindow(self):
        self.window.setBackgroundColor_(AppKit.NSColor.whiteColor())
        self.window.setTitlebarAppearsTransparent_(True)
        self.window.setTitleVisibility_(AppKit.NSWindowTitleHidden)
        self.window.setLevel_(AppKit.NSFloatingWindowLevel)

        self.talkTextView = ClickThroughTextView.alloc().initWithFrame_(
            AppKit.NSMakeRect(20, 10, 260, 180))
        self.talkTextView.setRichText_(False)
        self.talkTextView.setEditable_(False)
        self.talkTextView.setSelectable_(False)
        self.talkTextView.setHorizontallyResizable_(False)
        self.talkTextView.setVerticallyResizable_(True)
        self.talkTextView.setAutoresizingMask_(
            AppKit.NSViewWidthSizable | AppKit.NSViewHeightSizable)
        self.talkTextView.setTextContainerInset_(AppKit.NSMakeSize(5, 10))

        self.scrollView = AppKit.NSScrollView.alloc().initWithFrame_(
            AppKit.NSMakeRect(20, 40, 260, 150))
        self.scrollView.setHasVerticalScroller_(True)
        self.scrollView.setAutohidesScrollers_(False)
        self.scrollView.setDocumentView_(self.talkTextView)

        # Add the scroll view to the window's content view
        self.window.contentView().addSubview_(self.scrollView)

        # self.window.contentView().addSubview_(self.talkLabel)
        self.replyButton = CursorChangingButton.alloc().initWithFrame_(
            AppKit.NSMakeRect(110, 10, 80, 30))
        self.replyButton.setTitle_("返事をする")
        self.replyButton.setBezelStyle_(AppKit.NSBezelStyleRounded)
        self.replyButton.setTarget_(self)
        self.replyButton.cell().setBordered_(False)
        self.replyButton.cell().setBackgroundColor_(AppKit.NSColor.clearColor())
        self.replyButton.setAction_(objc.selector(
            self.replyButtonClicked_))
        self.window.contentView().addSubview_(self.replyButton)

    def scrollToBottom(self):
        clipView = self.scrollView.contentView()
        documentView = self.scrollView.documentView()
        documentViewHeight = documentView.frame().size.height
        clipViewHeight = clipView.frame().size.height
        newOrigin = AppKit.NSMakePoint(0, documentViewHeight - clipViewHeight)

        if newOrigin.y < 0:
            newOrigin.y = 0

        clipView.setBoundsOrigin_(newOrigin)

    def replyButtonClicked_(self, sender):
        self.textEntryWindowController.show()

    def show(self):
        self.window.open()

    def reload(self):
        self.window.reload()

    def showTalk_(self, text):
        self.talkTextView.setString_(text)
        self.show()

    def showTalkOnMainThread_(self, text):
        self.performSelectorOnMainThread_withObject_waitUntilDone_(
            objc.selector(None, selector=b"showTalk:", signature=b"v@:@"),
            text,
            False
        )

    def showTalkWithDelay_(self, text):
        displayed_text = ""

        def check_symbols(text):
            symbols = [r"¥s\[?(\d+)\]?", "¥e"]
            m = re.match(symbols[0], text)
            if m:
                num = int(m.group(1))
                self.baseWare.imageWindowController.setSurfaceId_(num)
                return text[len(m.group(0)):]
            return text

        willWritten = cp.copy(text)
        while len(willWritten) > 0:
            willWritten = check_symbols(willWritten)
            char = willWritten[0]
            willWritten = willWritten[1:]
            displayed_text += char
            self.talkTextView.setString_(displayed_text)
            self.show()
            AppKit.NSRunLoop.currentRunLoop().runUntilDate_(
                AppKit.NSDate.dateWithTimeIntervalSinceNow_(self.delay))

    def showTalkOnMainThreadWithDelay_(self, text):
        self.performSelectorOnMainThread_withObject_waitUntilDone_(
            # Selector for the method to run on the main thread
            objc.selector(None, selector=b"showTalkWithDelay:",
                          signature=b"v@:@"),
            text,  # The argument to pass to the method
            False  # waitUntilDone: set to False for non-blocking, True for blocking
        )

    def chatWithMessageStreamOnMainThread_(self, text):
        self.performSelectorOnMainThread_withObject_waitUntilDone_(
            # Selector for the method to run on the main thread
            objc.selector(None, selector=b"chatWithMessageStream:",
                          signature=b"v@:@"),
            text,  # The argument to pass to the method
            False  # waitUntilDone: set to False for non-blocking, True for blocking
        )

    def chatBackground_(self, text):
        threading.Thread(target=self.chatWithMessageStream_,
                         args=(text,), daemon=True).start()

    def chatWithMessage_(self, message=None):
        messages = self.messages
        if message not in [None, {}]:
            messages.append(message)
        if len(messages) < 1:
            messages = [self.baseWare.ghost.Base()]
        messages = chat.talk(messages=messages)
        self.showTalkWithDelay_(messages[-1].content)
        self.messages = messages

    def showInFront(self):
        self.window.orderFront_(None)

    def showResponseStream_(self, response):
        displayed_text = ""
        total_text = ""

        def check_face_symbols(text):
            face_symbols = self.baseWare.ghost.face_symbols
            for symbol, num in face_symbols.items():
                if text.startswith(symbol):
                    self.baseWare.imageWindowController.setSurfaceId_(num)
                    return text[len(symbol):]
            return text
        willWritten = ""
        warming = True
        isFirstSymbol = True
        if not isinstance(response, Iterable):
            print(response)
            text = f"エラーが発生しました。\n\n{response}"
            self.performSelectorOnMainThread_withObject_waitUntilDone_(
                objc.selector(None, selector=b"updateTalkLabel:",
                              signature=b"v@:@"),
                text,
                False
            )
            return ""
        for i, chunk in enumerate(response):

            chunk_message = chunk['choices'][0]['delta']  # extract the message
            m = chunk_message.get('content', '')
            willWritten += m
            total_text += m
            if len(willWritten) < 10 and warming:
                continue

            willWritten = check_face_symbols(willWritten)
            if len(willWritten) < 1:
                continue
            char = willWritten[0]
            willWritten = willWritten[1:]
            displayed_text += char
            self.performSelectorOnMainThread_withObject_waitUntilDone_(
                objc.selector(None, selector=b"updateTalkLabel:",
                              signature=b"v@:@"),
                displayed_text,
                False
            )
            if isFirstSymbol:
                self.performSelectorOnMainThread_withObject_waitUntilDone_(
                    objc.selector(None, selector=b"showInFront"),
                    None,
                    False
                )
                isFirstSymbol = False

        while len(willWritten) > 0:
            willWritten = check_face_symbols(willWritten)
            if len(willWritten) < 1:
                break
            char = willWritten[0]
            willWritten = willWritten[1:]
            displayed_text += char
            self.performSelectorOnMainThread_withObject_waitUntilDone_(
                objc.selector(None, selector=b"updateTalkLabel:",
                              signature=b"v@:@"),
                displayed_text,
                False
            )
            time.sleep(0.1)
        return total_text

    def chatWithMessageStream_(self, message=None):
        if self.talking:
            return
        with TalkingContextManager(self):
            self.messages = self.baseWare.loadMessages()
            messages = self.messages

            if message not in [None, {}]:
                messages.append(message)
            token_num = chat.num_tokens_from_messages(messages)
            while token_num > 4000*0.8:
                messages.pop(1)
                token_num = chat.num_tokens_from_messages(messages)
            response = chat.talkStream(messages=messages)
            text = self.showResponseStream_(response)
            if text not in "":
                messages.append({"role": "assistant", "content": text})
                self.messages = messages
                self.baseWare.saveMessages(messages)

    def updateTalkLabel_(self, text):
        self.talkTextView.setString_(text)
        self.show()
        self.scrollToBottom()
        AppKit.NSRunLoop.currentRunLoop().runUntilDate_(
            AppKit.NSDate.dateWithTimeIntervalSinceNow_(self.delay))


class ApiKeyController(AppKit.NSObject):
    def initWithBaseWare_(self, baseWare):
        self = super().init()
        if self:
            self.baseWare = baseWare
            self.textEntryWindowController = TextEntryWindowController.alloc(
            ).initWithAction_Placeholder_(self.registerApiKey_, "OpenAIのAPIキーを入力してください")
        return self

    def show(self):
        self.textEntryWindowController.show()

    def registerApiKey_(self, api_key):
        chat.setApiKey(api_key)
        self.baseWare.data["API_Key"] = str(api_key)
        self.baseWare.saveGeneralData()
        if not self.baseWare.ghost_booted:
            self.baseWare.ghostBoot()


class BaseWare:
    def __init__(self):
        self.ghost_booted = False
        self.data_path = path_in_savedir("data.yaml")

    def initializeMessages(self):
        self.saveMessages([self.ghost.Base()])

    def saveMessages(self, messages):
        with open(self.ghost.path+"/messages.json", "w") as f:
            json.dump(messages, f, ensure_ascii=False)

    def saveGeneralData(self):

        with open(self.data_path, 'w') as f:
            yaml.dump(self.data, f)

    def loadGeneralData(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, 'r') as f:
                self.data = yaml.safe_load(f)
        else:
            self.data = {}

    def initilizeSetting(self):
        if "API_Key" in self.data.keys():
            chat.setApiKey(self.data["API_Key"])

    def loadMessages(self):
        if not os.path.exists(self.ghost.path+"/messages.json"):
            return []
        with open(self.ghost.path+"/messages.json", "r") as f:
            messages = json.load(f)
        return messages

    def changeGhost(self, name):
        self.ghost = loadGhost(name)
        self.shell = loadShell(name)
        self.initializeMessages()
        self.imageWindowController.setSurfaceId_(0)
        self.talkWindowController.chatBackground_(self.ghost.OnBoot())

    def boot(self):
        self.appBoot()

    def ghostBoot(self):
        # if 0:
        if "API_Key" not in self.data.keys():
            self.apiKeyController.show()
        else:
            self.imageWindowController.show()

            self.initializeMessages()
            self.talkWindowController.chatBackground_(self.ghost.OnBoot())

            def refresh_talk():
                while True:
                    time.sleep(30)
                    if self.talkWindowController.window.closed and self.talkWindowController.textEntryWindowController.closed:
                        self.talkWindowController.chatBackground_(
                            self.ghost.OnInterval())

            threading.Thread(target=refresh_talk, daemon=True).start()
            self.ghost_booted = True

    def appBoot(self):
        self.loadGeneralData()
        self.initilizeSetting()
        name = "selvi"
        self.ghost = loadGhost(name)
        self.shell = loadShell(name)
        self.imageWindowController = ImageWindowController.alloc().initWithBaseWare_(self)
        self.talkWindowController = TalkWindowController.alloc().initWithBaseWare_(self)
        self.apiKeyController = ApiKeyController.alloc().initWithBaseWare_(self)
        app = AppKit.NSApplication.sharedApplication()
        appDelegate = AppDelegate.alloc().initWithBaseware_(self)
        app.setDelegate_(appDelegate)
        app.run()
        # threading.Thread(target=app.run, daemon=True).start()


def loadGhost(name):
    # if getattr(sys, 'frozen', False):
    #         # PyInstallerによってパッケージングされた実行可能ファイルの場合
    #     base_path = sys._MEIPASS
    # else:
    #     # スクリプトが直接実行されている場合
    #     base_path = os.path.abspath(".")

    # module_path = f"{base_path}/ghosts/{name}/ghost.py"
    # module_name = "ghost"
    # print("module_path",module_path,module_name)
    # spec = importlib.util.spec_from_file_location(module_name, module_path)
    # module = importlib.util.module_from_spec(spec)
    # spec.loader.exec_module(module)
    # module_name = f"ghosts.{name}.ghost"
    # module = importlib.import_module(module_name)
    selected_module_file = f"{name}/ghost.py"
    module = load_external_module('selected_module', selected_module_file)
    Ghost = module.Ghost
    ghost = Ghost(safe_path(f"ghosts/{name}"))
    return ghost


def loadShell(name):
    shell_path = safe_path(f"ghosts/{name}/shell")
    return Shell(shell_path)


def getGhostInfos():
    ghost_info_paths_list = sorted(
        glob.glob(safe_path("ghosts/*/ghost_info.yaml")))
    ghost_infos = {}
    for ghost_info_path in ghost_info_paths_list:
        with open(ghost_info_path) as f:
            ghost_info = yaml.safe_load(f)
        ghost_dir = os.path.basename(os.path.dirname(ghost_info_path))
        ghost_infos[ghost_dir] = ghost_info["name"]

    return ghost_infos


def main():
    baseWare = BaseWare()
    baseWare.boot()


if __name__ == "__main__":
    main()
