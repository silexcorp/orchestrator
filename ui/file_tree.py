from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QTreeWidgetItemIterator
from PyQt6.QtCore import Qt, pyqtSignal, QFileSystemWatcher
from PyQt6.QtGui import QAction, QColor
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import os

class TreeWatcher(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
    def on_any_event(self, event):
        self.callback()

class FileTreeWidget(QTreeWidget):
    file_clicked = pyqtSignal(str)
    file_renamed = pyqtSignal(str, str)
    file_deleted = pyqtSignal(str)
    folder_created = pyqtSignal(str)
    needs_refresh = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.root_path = None
        self.observer = None
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.needs_refresh.connect(self.refresh)

    def set_root(self, path: str):
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        self.root_path = os.path.abspath(path)
        self.refresh()
        
        # Start watchdog
        self.observer = Observer()
        handler = TreeWatcher(lambda: self.needs_refresh.emit())
        self.observer.schedule(handler, self.root_path, recursive=True)
        self.observer.start()

    def refresh(self):
        self.clear()
        if not self.root_path or not os.path.exists(self.root_path):
            return
        
        root_item = self._create_item(self.root_path)
        self.addTopLevelItem(root_item)
        self._populate_tree(self.root_path, root_item)
        root_item.setExpanded(True)

    def _populate_tree(self, path: str, parent_item: QTreeWidgetItem):
        try:
            items = sorted(os.listdir(path))
            # Ignored patterns
            ignored = {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}
            
            for item_name in items:
                if item_name in ignored:
                    continue
                
                full_path = os.path.join(path, item_name)
                item = self._create_item(full_path)
                parent_item.addChild(item)
                
                if os.path.isdir(full_path):
                    self._populate_tree(full_path, item)
        except Exception as e:
            print(f"Error populating tree: {e}")

    def _create_item(self, path: str) -> QTreeWidgetItem:
        name = os.path.basename(path)
        item = QTreeWidgetItem([name])
        item.setData(0, Qt.ItemDataRole.UserRole, path)
        
        if os.path.isdir(path):
            item.setText(0, f"📁 {name}")
        else:
            ext = os.path.splitext(name)[1].lower()
            icon = "📄"
            if ext == ".py": icon = "🐍"
            elif ext == ".md": icon = "📝"
            elif ext in (".json", ".toml", ".yaml", ".yml"): icon = "⚙️"
            item.setText(0, f"{icon} {name}")
            
        return item

    def _on_item_double_clicked(self, item, column):
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if os.path.isfile(path):
            self.file_clicked.emit(path)

    def _show_context_menu(self, position):
        item = self.itemAt(position)
        if not item:
            return
        
        path = item.data(0, Qt.ItemDataRole.UserRole)
        menu = QMenu()
        
        if os.path.isfile(path):
            open_act = menu.addAction("Open")
            open_act.triggered.connect(lambda: self.file_clicked.emit(path))
        
        rename_act = menu.addAction("Rename")
        delete_act = menu.addAction("Delete")
        copy_path_act = menu.addAction("Copy path")
        
        action = menu.exec(self.viewport().mapToGlobal(position))
        
        # Basic logic for demonstration (stubbed for now)
        if action == copy_path_act:
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(path)

    def highlight_file(self, path: str):
        path = os.path.abspath(path)
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            item = iterator.value()
            item_path = item.data(0, Qt.ItemDataRole.UserRole)
            if item_path == path:
                self.setCurrentItem(item)
                item.setBackground(0, QColor("#1f6feb"))
                item.setForeground(0, QColor("white"))
            else:
                item.setBackground(0, QColor("transparent"))
                item.setForeground(0, Qt.GlobalColor.white if os.path.isdir(item_path) else QColor("#e6edf3"))
            iterator += 1
