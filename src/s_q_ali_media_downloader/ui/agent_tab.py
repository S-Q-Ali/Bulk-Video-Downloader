"""PySide6 Desktop User Interface Tab for YouTube Discovery & Social Inspection Agent."""

import csv

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from s_q_ali_media_downloader.agent.orchestrator import AgentOrchestrator
from s_q_ali_media_downloader.agent.schema import (
    AgentSearchResult,
    ChannelMetadata,
    SocialStatus,
)


class AgentWorkerThread(QThread):
    """Background worker thread for running AgentOrchestrator without blocking Qt main loop."""

    progress_updated = Signal(int, str)
    search_finished = Signal(object)
    search_failed = Signal(str)

    def __init__(
        self,
        query: str,
        max_channels: int,
        min_subs: int,
        check_fb: bool,
        check_ig: bool,
        only_no_socials: bool,
        api_key: str,
    ):
        super().__init__()
        self.query = query
        self.max_channels = max_channels
        self.min_subs = min_subs
        self.check_fb = check_fb
        self.check_ig = check_ig
        self.only_no_socials = only_no_socials
        self.api_key = api_key

    def run(self):
        try:
            orchestrator = AgentOrchestrator(
                api_key=self.api_key,
                progress_callback=lambda pct, msg: self.progress_updated.emit(pct, msg),
            )
            result = orchestrator.run_discovery(
                query=self.query,
                max_channels=self.max_channels,
                min_subscribers=self.min_subs,
                check_facebook=self.check_fb,
                check_instagram=self.check_ig,
                only_no_socials=self.only_no_socials,
            )
            self.search_finished.emit(result)
        except Exception as e:
            self.search_failed.emit(str(e))


class AgentTabWidget(QWidget):
    """Main UI view for AI Channel & Social Presence Discovery Agent."""

    send_to_queue_requested = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_result: AgentSearchResult = None
        self.worker: AgentWorkerThread = None
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # 1. Top Controls Header Panel
        controls_frame = QFrame()
        controls_frame.setObjectName("AgentHeader")
        controls_frame.setStyleSheet(
            "QFrame#AgentHeader { background: #1A1722; border: 1px solid #332C42; border-radius: 12px; padding: 12px; }"
        )
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setSpacing(12)

        # Header Title
        lbl_title = QLabel("🤖 AI CHANNEL FINDER & SOCIAL PRESENCE INSPECTOR")
        lbl_title.setStyleSheet("font-size: 14px; font-weight: 800; color: #22D3EE; letter-spacing: 2px;")
        controls_layout.addWidget(lbl_title)

        # Row 1: Query Input + Search Button
        row1 = QHBoxLayout()
        row1.setSpacing(10)

        self.query_edit = QLineEdit()
        self.query_edit.setPlaceholderText(
            "Enter prompt (e.g. 'IShowSpeed content edits'), tag (#techreviews), or creator handle..."
        )
        self.query_edit.setMinimumHeight(40)
        self.query_edit.returnPressed.connect(self._start_agent)

        self.btn_search = QPushButton("🤖 Find & Verify Channels")
        self.btn_search.setProperty("kind", "primary")
        self.btn_search.setMinimumHeight(40)
        self.btn_search.setMinimumWidth(180)
        self.btn_search.clicked.connect(self._start_agent)

        row1.addWidget(self.query_edit, 4)
        row1.addWidget(self.btn_search, 1)
        controls_layout.addLayout(row1)

        # Row 2: Filters & Options
        row2 = QHBoxLayout()
        row2.setSpacing(16)

        # Depth
        lbl_depth = QLabel("Depth:")
        lbl_depth.setStyleSheet("font-weight: bold; color: #9C93AE;")
        self.depth_combo = QComboBox()
        self.depth_combo.addItems(["20 channels", "50 channels", "100 channels"])
        self.depth_combo.setCurrentIndex(1)

        row2.addWidget(lbl_depth)
        row2.addWidget(self.depth_combo)

        # Min Subs
        lbl_subs = QLabel("Min Subs:")
        lbl_subs.setStyleSheet("font-weight: bold; color: #9C93AE;")
        self.subs_combo = QComboBox()
        self.subs_combo.addItems(["Any", "5K+", "10K+", "50K+", "100K+"])
        self.subs_combo.setCurrentIndex(0)

        row2.addWidget(lbl_subs)
        row2.addWidget(self.subs_combo)

        # Checkboxes
        self.chk_fb = QCheckBox("Facebook Pages")
        self.chk_fb.setChecked(True)
        self.chk_ig = QCheckBox("Instagram Profiles")
        self.chk_ig.setChecked(True)
        self.chk_no_socials = QCheckBox("Only Missing Social Pages (Targets)")
        self.chk_no_socials.setChecked(False)

        row2.addWidget(self.chk_fb)
        row2.addWidget(self.chk_ig)
        row2.addWidget(self.chk_no_socials)

        row2.addStretch()
        controls_layout.addLayout(row2)

        # Row 3: Optional YouTube API Key
        row3 = QHBoxLayout()
        lbl_key = QLabel("YouTube API Key (Optional):")
        lbl_key.setStyleSheet("color: #6E667E; font-size: 11px;")
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("Leave blank for 100% free zero-key scraper mode (yt-dlp)")
        self.api_key_edit.setEchoMode(QLineEdit.PasswordEchoOnEdit)

        row3.addWidget(lbl_key)
        row3.addWidget(self.api_key_edit)
        controls_layout.addLayout(row3)

        main_layout.addWidget(controls_frame)

        # 2. Progress Banner & Status Label
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)

        self.lbl_status = QLabel("Ready to search channels and verify social presences.")
        self.lbl_status.setStyleSheet("color: #9C93AE; font-size: 12px; font-weight: 600;")

        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.lbl_status)

        # 3. Results Table (QTableWidget)
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            [
                "Select",
                "Channel Name",
                "Handle",
                "Subscribers",
                "Facebook Page",
                "Instagram Profile",
                "Action",
            ]
        )
        self.table.setStyleSheet(
            "QTableWidget { background: #1A1722; border: 1px solid #332C42; border-radius: 8px; gridline-color: #241F30; }"
            "QHeaderView::section { background: #241F30; color: #22D3EE; font-weight: 700; padding: 6px; border: none; }"
        )
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)

        main_layout.addWidget(self.table, 1)

        # 4. Footer Actions Bar
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(10)

        self.btn_copy_fb = QPushButton("Copy FB Links")
        self.btn_copy_fb.clicked.connect(self._copy_fb_links)
        self.btn_copy_ig = QPushButton("Copy IG Links")
        self.btn_copy_ig.clicked.connect(self._copy_ig_links)

        self.btn_export_csv = QPushButton("Export CSV")
        self.btn_export_csv.clicked.connect(self._export_csv)
        self.btn_export_json = QPushButton("Export JSON")
        self.btn_export_json.clicked.connect(self._export_json)

        self.btn_send_queue = QPushButton("➔ Send Selected Videos to Queue")
        self.btn_send_queue.setProperty("kind", "primary")
        self.btn_send_queue.clicked.connect(self._send_selected_to_queue)

        footer_layout.addWidget(self.btn_copy_fb)
        footer_layout.addWidget(self.btn_copy_ig)
        footer_layout.addWidget(self.btn_export_csv)
        footer_layout.addWidget(self.btn_export_json)
        footer_layout.addStretch()
        footer_layout.addWidget(self.btn_send_queue)

        main_layout.addLayout(footer_layout)

    def _start_agent(self):
        query = self.query_edit.text().strip()
        if not query:
            QMessageBox.warning(self, "Input Required", "Please enter a search prompt or tag!")
            return

        depth_map = {0: 20, 1: 50, 2: 100}
        subs_map = {0: 0, 1: 5000, 2: 10000, 3: 50000, 4: 100000}

        max_channels = depth_map.get(self.depth_combo.currentIndex(), 50)
        min_subs = subs_map.get(self.subs_combo.currentIndex(), 0)

        self.btn_search.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.lbl_status.setText("Starting Agent...")

        self.worker = AgentWorkerThread(
            query=query,
            max_channels=max_channels,
            min_subs=min_subs,
            check_fb=self.chk_fb.isChecked(),
            check_ig=self.chk_ig.isChecked(),
            only_no_socials=self.chk_no_socials.isChecked(),
            api_key=self.api_key_edit.text().strip(),
        )

        self.worker.progress_updated.connect(self._on_progress)
        self.worker.search_finished.connect(self._on_finished)
        self.worker.search_failed.connect(self._on_failed)
        self.worker.start()

    def _on_progress(self, percent: int, message: str):
        self.progress_bar.setValue(percent)
        self.lbl_status.setText(message)

    def _on_finished(self, result: AgentSearchResult):
        self.search_result = result
        self.btn_search.setEnabled(True)
        self.progress_bar.setVisible(False)
        self._populate_table(result.channels)

    def _on_failed(self, error_msg: str):
        self.btn_search.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.lbl_status.setText(f"Error: {error_msg}")
        QMessageBox.critical(self, "Agent Error", f"Agent failed with error:\n{error_msg}")

    def _populate_table(self, channels: list[ChannelMetadata]):
        self.table.setRowCount(0)
        for row_idx, ch in enumerate(channels):
            self.table.insertRow(row_idx)

            # Col 0: Checkbox
            chk = QCheckBox()
            chk.setChecked(True)
            self.table.setCellWidget(row_idx, 0, chk)

            # Col 1: Title
            title_item = QTableWidgetItem(ch.title)
            title_item.setData(Qt.UserRole, ch)
            self.table.setItem(row_idx, 1, title_item)

            # Col 2: Handle
            self.table.setItem(row_idx, 2, QTableWidgetItem(ch.handle or "N/A"))

            # Col 3: Subs
            self.table.setItem(row_idx, 3, QTableWidgetItem(ch.subscribers_formatted))

            # Col 4: Facebook Status Badge
            fb_item = QTableWidgetItem()
            if ch.facebook.status == SocialStatus.VERIFIED:
                fb_item.setText("✓ Verified Page")
                fb_item.setForeground(QColor("#2DD4BF"))  # Teal / Green
            else:
                fb_item.setText("✗ Not Found")
                fb_item.setForeground(QColor("#F2547D"))  # Pink / Red
            self.table.setItem(row_idx, 4, fb_item)

            # Col 5: Instagram Status Badge
            ig_item = QTableWidgetItem()
            if ch.instagram.status == SocialStatus.VERIFIED:
                ig_item.setText("✓ Verified Profile")
                ig_item.setForeground(QColor("#2DD4BF"))  # Teal / Green
            else:
                ig_item.setText("✗ Not Found")
                ig_item.setForeground(QColor("#F2547D"))  # Pink / Red
            self.table.setItem(row_idx, 5, ig_item)

            # Col 6: Action Button
            btn_queue = QPushButton("➔ Queue")
            btn_queue.clicked.connect(lambda _, c=ch: self._send_single_channel_to_queue(c))
            self.table.setCellWidget(row_idx, 6, btn_queue)

    def _send_single_channel_to_queue(self, ch: ChannelMetadata):
        target_url = ch.latest_video_url or ch.youtube_url
        self.send_to_queue_requested.emit([target_url])

    def _send_selected_to_queue(self):
        selected_urls = []
        for row in range(self.table.rowCount()):
            chk = self.table.cellWidget(row, 0)
            if chk and chk.isChecked():
                title_item = self.table.item(row, 1)
                ch: ChannelMetadata = title_item.data(Qt.UserRole)
                target_url = ch.latest_video_url or ch.youtube_url
                selected_urls.append(target_url)

        if selected_urls:
            self.send_to_queue_requested.emit(selected_urls)
            QMessageBox.information(
                self, "Sent to Queue", f"Sent {len(selected_urls)} channel video URLs to download queue!"
            )
        else:
            QMessageBox.warning(self, "No Selection", "Please select at least one channel!")

    def _copy_fb_links(self):
        links = []
        if self.search_result:
            for ch in self.search_result.channels:
                if ch.facebook.status == SocialStatus.VERIFIED and ch.facebook.verified_url:
                    links.append(ch.facebook.verified_url)
        if links:
            from PySide6.QtWidgets import QApplication

            QApplication.clipboard().setText("\n".join(links))
            QMessageBox.information(self, "Copied", f"Copied {len(links)} Facebook page links!")

    def _copy_ig_links(self):
        links = []
        if self.search_result:
            for ch in self.search_result.channels:
                if ch.instagram.status == SocialStatus.VERIFIED and ch.instagram.verified_url:
                    links.append(ch.instagram.verified_url)
        if links:
            from PySide6.QtWidgets import QApplication

            QApplication.clipboard().setText("\n".join(links))
            QMessageBox.information(self, "Copied", f"Copied {len(links)} Instagram profile links!")

    def _export_csv(self):
        if not self.search_result or not self.search_result.channels:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Agent Results CSV", "channels_social_export.csv", "CSV Files (*.csv)"
        )
        if path:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "Channel Title",
                        "Handle",
                        "Subscribers",
                        "YouTube URL",
                        "Facebook Status",
                        "Facebook URL",
                        "Instagram Status",
                        "Instagram URL",
                        "Has No Social Pages",
                    ]
                )
                for ch in self.search_result.channels:
                    writer.writerow(
                        [
                            ch.title,
                            ch.handle,
                            ch.subscribers_formatted,
                            ch.youtube_url,
                            ch.facebook.status.value,
                            ch.facebook.verified_url or "",
                            ch.instagram.status.value,
                            ch.instagram.verified_url or "",
                            "YES" if ch.has_no_socials else "NO",
                        ]
                    )
            QMessageBox.information(self, "Exported", f"Successfully exported to {path}!")

    def _export_json(self):
        if not self.search_result:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Agent Results JSON", "channels_social_export.json", "JSON Files (*.json)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.search_result.model_dump_json(indent=2))
            QMessageBox.information(self, "Exported", f"Successfully exported to {path}!")
