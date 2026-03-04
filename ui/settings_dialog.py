import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QTextEdit, QPushButton, QListWidget,
    QListWidgetItem, QMessageBox, QCheckBox, QFormLayout
)
from PyQt6.QtCore import Qt
from core.config import ConfigManager

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(700, 500)
        self.config_manager = ConfigManager()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_agents_tab(), "Agents")
        self.tabs.addTab(self._create_models_tab(), "Models")
        self.tabs.addTab(self._create_tools_tab(), "Tools")
        self.tabs.addTab(self._create_search_tab(), "Search")
        
        layout.addWidget(self.tabs)
        
        # Bottom Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton("Save All")
        save_btn.setObjectName("sendBtn") # Use the premium style
        save_btn.clicked.connect(self._save_and_close)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _create_agents_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Left sidebar: List of agents
        self.agent_list = QListWidget()
        self.agent_list.setFixedWidth(180)
        self.agent_list.currentRowChanged.connect(self._on_agent_selected)
        
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Agent Profiles"))
        left_layout.addWidget(self.agent_list)
        
        add_btn = QPushButton("+ Add")
        add_btn.clicked.connect(self._add_agent)
        left_layout.addWidget(add_btn)
        
        layout.addLayout(left_layout)
        
        # Right area: Agent editor
        self.agent_editor = QWidget()
        edit_layout = QFormLayout(self.agent_editor)
        
        self.agent_name = QLineEdit()
        self.agent_prompt = QTextEdit()
        self.agent_color = QLineEdit()
        self.agent_color.setPlaceholderText("#00f2ff")
        
        edit_layout.addRow("Name:", self.agent_name)
        edit_layout.addRow("System Prompt:", self.agent_prompt)
        edit_layout.addRow("Accent Color (HEX):", self.agent_color)
        
        layout.addWidget(self.agent_editor, 1)
        
        self._load_agents()
        return tab

    def _create_models_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)
        
        self.ollama_url = QLineEdit(self.config_manager.config.get("ollama_url", "http://localhost:11434"))
        layout.addRow("Ollama Endpoint:", self.ollama_url)
        
        layout.addWidget(QLabel("\n* Available models are automatically listed in the main toolbar."))
        return tab

    def _create_search_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)
        
        self.brave_api_key = QLineEdit(self.config_manager.config.get("brave_api_key", ""))
        self.brave_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.brave_api_key.setPlaceholderText("Enter Brave Search API Key...")
        
        layout.addRow("Brave API Key:", self.brave_api_key)
        
        help_text = QLabel("\nTo get an API key, visit: https://api.search.brave.com/")
        help_text.setOpenExternalLinks(True)
        help_text.setStyleSheet("color: #8b949e; font-size: 11px;")
        layout.addWidget(help_text)
        
        return tab

    def _create_tools_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("Enable/Disable Agent Capabilities"))
        
        self.tool_checks = {}
        tools_data = self.config_manager.config.get("tools", {})
        
        for tool_id, enabled in tools_data.items():
            check = QCheckBox(tool_id.replace("_", " ").title())
            check.setChecked(enabled)
            self.tool_checks[tool_id] = check
            layout.addWidget(check)
            
        layout.addStretch()
        return tab

    def _load_agents(self):
        self.agent_list.clear()
        agents = self.config_manager.get_agents()
        for agent in agents:
            item = QListWidgetItem(agent["name"])
            item.setData(Qt.ItemDataRole.UserRole, agent["id"])
            self.agent_list.addItem(item)
        
        if agents:
            self.agent_list.setCurrentRow(0)

    def _on_agent_selected(self, index):
        if index < 0: return
        agent_id = self.agent_list.currentItem().data(Qt.ItemDataRole.UserRole)
        agent = self.config_manager.get_agent(agent_id)
        if agent:
            self.agent_name.setText(agent["name"])
            self.agent_prompt.setText(agent["prompt"])
            self.agent_color.setText(agent.get("color", "#00f2ff"))

    def _add_agent(self):
        new_id = f"agent_{len(self.config_manager.get_agents())}"
        new_agent = {
            "id": new_id,
            "name": "New Agent",
            "prompt": "You are an assistant...",
            "color": "#00f2ff"
        }
        self.config_manager.config["agents"].append(new_agent)
        self._load_agents()
        self.agent_list.setCurrentRow(self.agent_list.count() - 1)

    def _save_and_close(self):
        # Update current agent being edited
        current_item = self.agent_list.currentItem()
        if current_item:
            agent_id = current_item.data(Qt.ItemDataRole.UserRole)
            for agent in self.config_manager.config["agents"]:
                if agent["id"] == agent_id:
                    agent["name"] = self.agent_name.text()
                    agent["prompt"] = self.agent_prompt.toPlainText()
                    agent["color"] = self.agent_color.text()
        
        # Update other tabs
        self.config_manager.config["ollama_url"] = self.ollama_url.text()
        self.config_manager.config["brave_api_key"] = self.brave_api_key.text()
        
        for tool_id, check in self.tool_checks.items():
            self.config_manager.config["tools"][tool_id] = check.isChecked()
            
        self.config_manager.save()
        QMessageBox.information(self, "Settings", "Changes saved successfully.")
        self.accept()
