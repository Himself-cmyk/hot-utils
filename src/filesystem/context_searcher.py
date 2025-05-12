'''

1.选中一个标签之后，文本框中，设置为富文本，需要渲染匹配到的文本为暗红色。
2.快捷键设置复制文件名，右键标签复制完整的路径，增加一个按钮复制完整路径。
'''

import os
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QListWidget, QTextEdit,
                             QComboBox, QCheckBox, QDialog, QFileDialog, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


class FileTypeDialog(QDialog):
    """文件类型设置对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("文件类型设置")
        self.setModal(True)
        self.resize(300, 200)
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        group = QGroupBox("选择要搜索的文件类型")
        self.checkboxes = {
            'txt': QCheckBox("文本文件 (.txt)"),
            'pdf': QCheckBox("PDF 文件 (.pdf)"),
            'docx': QCheckBox("Word 文档 (.docx)"),
            'xlsx': QCheckBox("Excel 文件 (.xlsx)"),
            'pptx': QCheckBox("PowerPoint 文件 (.pptx)"),
            'csv': QCheckBox("CSV 文件 (.csv)"),
            'html': QCheckBox("HTML 文件 (.html, .htm)"),
            'xml': QCheckBox("XML 文件 (.xml)"),
            'json': QCheckBox("JSON 文件 (.json)"),
            'md': QCheckBox("Markdown 文件 (.md)"),
        }
        
        vbox = QVBoxLayout()
        for cb in self.checkboxes.values():
            vbox.addWidget(cb)
        group.setLayout(vbox)
        
        layout.addWidget(group)
        
        # 按钮
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.cancel_btn = QPushButton("取消")
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # 信号连接
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
    
    def load_settings(self):
        """加载设置，这里简单设置为默认选中前几个"""
        for i, cb in enumerate(self.checkboxes.values()):
            cb.setChecked(i < 5)  # 默认选中前5个
    
    def get_selected_types(self):
        """获取选中的文件类型"""
        selected = []
        for ext, cb in self.checkboxes.items():
            if cb.isChecked():
                selected.append(ext)
        return selected


class FileSearchApp(QMainWindow):
    """主应用程序窗口"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("文件搜索工具 V1.0")
        self.resize(800, 600)

        
        # 搜索设置
        self.search_folder = ""
        self.file_types = ['txt', 'docx', 'pdf', 'xlsx', 'pptx']  # 默认文件类型
        self.match_mode = "exact"  # 默认精确匹配
        
        self.init_ui()
    
    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # 搜索控制区域
        control_layout = QHBoxLayout()
        
        self.folder_label = QLabel("搜索文件夹:")
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("点击浏览按钮选择文件夹...")
        self.browse_btn = QPushButton("浏览...")
        
        control_layout.addWidget(self.folder_label)
        control_layout.addWidget(self.folder_input, stretch=1)
        control_layout.addWidget(self.browse_btn)
        
        # 搜索关键词区域
        search_layout = QHBoxLayout()
        
        self.search_label = QLabel("搜索内容:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入要搜索的关键词...")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["精确匹配", "正则表达式"])
        self.search_btn = QPushButton("搜索")
        self.settings_btn = QPushButton("设置")
        self.copy_path_btn = QPushButton("复制完整路径")
        
        search_layout.addWidget(self.search_label)
        search_layout.addWidget(self.search_input, stretch=1)
        search_layout.addWidget(self.mode_combo)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.settings_btn)
        search_layout.addWidget(self.copy_path_btn)  # 添加新按钮
        
        # 结果展示区域
        result_layout = QHBoxLayout()
        
        self.file_list = QListWidget()
        self.file_list.setMinimumWidth(300)
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)

        self.content_display = QTextEdit()
        self.content_display.setReadOnly(True)
        
        result_layout.addWidget(self.file_list, stretch=1)
        result_layout.addWidget(self.content_display, stretch=2)
        
        # 添加到主布局
        main_layout.addLayout(control_layout)
        main_layout.addLayout(search_layout)
        main_layout.addLayout(result_layout)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # 信号连接
        self.browse_btn.clicked.connect(self.browse_folder)
        self.search_btn.clicked.connect(self.start_search)
        self.settings_btn.clicked.connect(self.show_settings)
        self.file_list.itemClicked.connect(self.show_file_content)
        self.copy_path_btn.clicked.connect(self.copy_selected_path)

    
    def browse_folder(self):
        """选择文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择搜索文件夹")
        if folder:
            self.search_folder = folder
            self.folder_input.setText(folder)
    
    def show_settings(self):
        """显示文件类型设置对话框"""
        dialog = FileTypeDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.file_types = dialog.get_selected_types()
    
    def start_search(self):
        """开始搜索"""
        keyword = self.search_input.text().strip()
        if not keyword:
            self.content_display.setPlainText("请输入搜索关键词！")
            return
        
        if not self.search_folder:
            self.content_display.setPlainText("请选择搜索文件夹！")
            return
        
        self.match_mode = "exact" if self.mode_combo.currentIndex() == 0 else "regex"
        
        # 清空之前的结果
        self.file_list.clear()
        self.content_display.clear()
        
        # 执行搜索
        matched_files = self.search_files(self.search_folder, keyword, self.match_mode, self.file_types)
        
        if not matched_files:
            self.content_display.setPlainText("没有找到匹配的文件。")
            return
        
        for file_path in matched_files:
            self.file_list.addItem(file_path)
    
    def search_files(self, folder, keyword, mode, extensions):
        """递归搜索文件"""
        matched_files = []
        
        # 构建扩展名正则表达式
        ext_pattern = re.compile(r'\.(' + '|'.join(extensions) + r')$', re.IGNORECASE)
        
        # 编译正则表达式（如果是正则模式）
        if mode == "regex":
            try:
                pattern = re.compile(keyword)
            except re.error:
                self.content_display.setPlainText("无效的正则表达式！")
                return []
        
        for root, _, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                
                # 检查文件扩展名
                if not ext_pattern.search(file):
                    continue
                
                # 检查文件内容
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        if mode == "exact":
                            if keyword in content:
                                matched_files.append(file_path)
                        else:  # regex
                            if pattern.search(content):
                                matched_files.append(file_path)
                except Exception as e:
                    print(f"无法读取文件 {file_path}: {e}")
        
        return matched_files
    
    def show_file_content(self, item):
        """显示选中文件的内容，并高亮关键词"""
        file_path = item.text()
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            keyword = self.search_input.text().strip()
            if keyword and self.match_mode == "exact":
                # 替换匹配部分为带颜色的 span
                highlight = lambda txt: txt.replace(keyword, f'<span style="color: #8B0000;">{keyword}</span>')
                content = highlight(content)

            elif keyword and self.match_mode == "regex":
                pattern = re.compile(keyword)
                content = pattern.sub(lambda m: f'<span style="color: #8B0000;">{m.group()}</span>', content)

            self.content_display.setHtml(content)  # 使用 HTML 模式显示

        except Exception as e:
            self.content_display.setPlainText(f"无法读取文件:\n{str(e)}")

    def copy_selected_path(self):
        selected_items = self.file_list.selectedItems()
        if selected_items:
            QApplication.clipboard().setText(selected_items[0].text())

    def show_context_menu(self, pos):
        menu = QMenu(self)
        copy_name_action = menu.addAction("复制文件名")
        copy_path_action = menu.addAction("复制完整路径")
        action = menu.exec_(self.file_list.mapToGlobal(pos))

        selected_item = self.file_list.currentItem()
        if not selected_item:
            return

        file_path = selected_item.text()
        filename = os.path.basename(file_path)

        if action == copy_name_action:
            QApplication.clipboard().setText(filename)
        elif action == copy_path_action:
            QApplication.clipboard().setText(file_path)


if __name__ == "__main__":
    # 设置应用程序图标
    icon_path = r"../../ICON/FileSearch.ico"

    app = QApplication([])
    app.setWindowIcon(QIcon(icon_path))

    window = FileSearchApp()
    window.show()
    app.exec_()
