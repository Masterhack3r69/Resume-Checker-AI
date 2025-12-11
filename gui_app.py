
import sys
import os
import json
import asyncio
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTextEdit, QLabel, 
                             QFileDialog, QProgressBar, QMessageBox, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon

# Ensure we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_processor import extract_text_from_pdf, clean_text, chunk_text
from vector_store import VectorStore
from analyzer import ResumeAnalyzer

class AnalysisWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, pdf_path, job_description):
        super().__init__()
        self.pdf_path = pdf_path
        self.job_description = job_description

    def run(self):
        try:
            # Create a new event loop for this thread to handle async calls
            # Windows ProactorEventLoop policy might be needed for some async ops, 
            # but standard loop usually works for http calls.
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.perform_analysis())
            self.finished.emit(result)
            loop.close()
        except Exception as e:
            self.error.emit(str(e))

    async def perform_analysis(self):
        # 1. Read PDF
        try:
            with open(self.pdf_path, 'rb') as f:
                content = f.read()
        except Exception as e:
            raise Exception(f"Failed to read file: {e}")
        
        try:
            raw_text, page_count = extract_text_from_pdf(content)
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {e}")

        cleaned_text = clean_text(raw_text)
        chunks = chunk_text(cleaned_text)

        if not chunks:
            raise Exception("Could not extract text from PDF (empty chunks).")

        file_metadata = {
            "filename": os.path.basename(self.pdf_path),
            "page_count": page_count
        }

        # 2. Vector Store
        try:
            vs = VectorStore()
            collection, collection_name = vs.create_collection_from_chunks(chunks)
        except Exception as e:
            raise Exception(f"Failed to initialize Vector Store: {e}")

        try:
            # 3. Analyze
            analyzer = ResumeAnalyzer(vector_store=vs)
            result = await analyzer.analyze(self.job_description, collection, raw_text, file_metadata)
            return result
        finally:
            if 'vs' in locals() and 'collection_name' in locals():
                vs.delete_collection(collection_name)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Resume Checker AI")
        self.resize(1000, 850)
        self.pdf_path = None
        
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Header Title
        header_layout = QHBoxLayout()
        title_label = QLabel("Resume Checker AI 🤖")
        title_label.setObjectName("titleLabel")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Main Content Area
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # 1. File Upload Section
        file_box = QFrame()
        file_box.setObjectName("sectionBox")
        file_layout_inner = QHBoxLayout(file_box)
        
        self.select_btn = QPushButton("📁 Upload Resume (PDF)")
        self.select_btn.setObjectName("uploadBtn")
        self.select_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.select_btn.clicked.connect(self.select_file)
        
        self.file_label = QLabel("No file selected")
        self.file_label.setObjectName("fileLabel")
        
        file_layout_inner.addWidget(self.select_btn)
        file_layout_inner.addWidget(self.file_label)
        file_layout_inner.addStretch()
        
        content_layout.addWidget(QLabel("1. Upload Resume"))
        content_layout.addWidget(file_box)

        # 2. Job Description Section
        content_layout.addWidget(QLabel("2. Job Description"))
        self.jd_input = QTextEdit()
        self.jd_input.setPlaceholderText("Paste the job description here to compare against...")
        self.jd_input.setMinimumHeight(120)
        content_layout.addWidget(self.jd_input)

        # 3. Action Section
        self.analyze_btn = QPushButton("✨ Analyze Resume")
        self.analyze_btn.setObjectName("analyzeBtn")
        self.analyze_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.analyze_btn.clicked.connect(self.start_analysis)
        self.analyze_btn.setMinimumHeight(55)
        content_layout.addWidget(self.analyze_btn)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0)
        content_layout.addWidget(self.progress_bar)

        main_layout.addWidget(content_frame)

        # Results Area
        results_label = QLabel("Analysis Results")
        results_label.setObjectName("subHeaderLabel")
        main_layout.addWidget(results_label)

        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        self.results_area.setPlaceholderText("Results will appear here...")
        main_layout.addWidget(self.results_area)

    def apply_styles(self):
        # Set Dark Theme Palette
        dark_palette = QPalette()
        # Backgrounds
        bg_color = QColor(18, 18, 18)
        surface_color = QColor(30, 30, 30)
        text_color = QColor(240, 240, 240)
        accent_color = QColor(59, 130, 246) # Blue-500
        
        dark_palette.setColor(QPalette.ColorRole.Window, bg_color)
        dark_palette.setColor(QPalette.ColorRole.WindowText, text_color)
        dark_palette.setColor(QPalette.ColorRole.Base, surface_color)
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, bg_color)
        dark_palette.setColor(QPalette.ColorRole.Text, text_color)
        dark_palette.setColor(QPalette.ColorRole.Button, surface_color)
        dark_palette.setColor(QPalette.ColorRole.ButtonText, text_color)
        dark_palette.setColor(QPalette.ColorRole.Link, accent_color)
        
        QApplication.setPalette(dark_palette)

        # Stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QLabel {
                font-family: 'Segoe UI', 'Roboto', sans-serif;
                font-size: 14px;
                color: #e0e0e0;
            }
            QLabel#titleLabel {
                font-size: 28px;
                font-weight: 700;
                color: #ffffff;
                padding: 5px;
            }
            QLabel#subHeaderLabel {
                font-size: 18px;
                font-weight: 600;
                color: #ffffff;
                margin-top: 10px;
            }
            QFrame#contentFrame {
                background-color: #1e1e1e;
                border-radius: 12px;
                border: 1px solid #333333;
            }
            QFrame#sectionBox {
                background-color: #252525;
                border-radius: 8px;
                border: 1px solid #333333;
            }
            QPushButton {
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: 500;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #404040;
                border-color: #555555;
            }
            QPushButton#uploadBtn {
                background-color: #2a2a2a;
                text-align: left;
                padding-left: 15px;
            }
            QPushButton#analyzeBtn {
                background-color: #2563eb; /* Blue-600 */
                border: none;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton#analyzeBtn:hover {
                background-color: #1d4ed8; /* Blue-700 */
            }
            QPushButton#analyzeBtn:disabled {
                background-color: #333;
                color: #777;
            }
            QTextEdit {
                background-color: #252525;
                color: #e0e0e0;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 12px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                selection-background-color: #2563eb;
            }
            QTextEdit:focus {
                border: 1px solid #2563eb;
            }
            QLabel#fileLabel {
                color: #aaaaaa;
                font-style: italic;
                margin-left: 10px;
            }
            QProgressBar {
                background-color: #333;
                border: none;
                border-radius: 4px;
                height: 6px;
            }
            QProgressBar::chunk {
                background-color: #2563eb;
                border-radius: 4px;
            }
            QScrollBar:vertical {
                border: none;
                background: #1e1e1e;
                width: 10px;
                margin: 0px; 
            }
            QScrollBar::handle:vertical {
                background: #444;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

    def select_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Resume", "", "PDF Files (*.pdf)")
        
        if file_path:
            self.pdf_path = file_path
            self.file_label.setText(os.path.basename(file_path))
            # Visual feedback
            self.select_btn.setStyleSheet("background-color: #064e3b; border-color: #059669; color: #a7f3d0;") # Green tint
            self.select_btn.setText("✅ Resume Selected")

    def start_analysis(self):
        if not self.pdf_path:
            QMessageBox.warning(self, "No File", "Please select a resume PDF first.")
            return

        jd_text = self.jd_input.toPlainText().strip()
        if not jd_text:
            QMessageBox.warning(self, "No Job Description", "Please enter a job description.")
            return

        self.analyze_btn.setEnabled(False)
        self.select_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.results_area.setHtml("<div style='color: #888; text-align: center; margin-top: 20px;'><i>Analyzing your resume... This may take up to 30 seconds.</i></div>")

        self.worker = AnalysisWorker(self.pdf_path, jd_text)
        self.worker.finished.connect(self.display_results)
        self.worker.error.connect(self.handle_error)
        self.worker.start()

    def display_results(self, result):
        self.progress_bar.setVisible(False)
        self.analyze_btn.setEnabled(True)
        self.select_btn.setEnabled(True)
        
        match_score = result.get("match_score", 0)
        analysis = result.get("analysis", {})
        strong_matches = analysis.get("strong_matches", [])
        missing_skills = analysis.get("missing_skills", [])
        recruiter_feedback = result.get("recruiter_feedback", {})
        red_flags = recruiter_feedback.get("red_flags", [])
        style_critique = recruiter_feedback.get("style_critique", [])
        interview_prep = result.get("interview_prep", [])
        
        # Color for Score
        score_color = "#22c55e" if match_score >= 80 else "#eab308" if match_score >= 50 else "#ef4444"
        
        # HTML Report Construction
        html = f"""
        <style>
            h2 {{ color: {score_color}; margin-bottom: 5px; }}
            h3 {{ color: #ffffff; margin-top: 20px; font-size: 16px; background-color: #333; padding: 5px; border-radius: 4px; }}
            p, li {{ line-height: 1.5; color: #d1d5db; }}
            .warning {{ color: #f87171; font-weight: bold; }}
            .success {{ color: #4ade80; }}
            .highlight {{ color: #60a5fa; }}
        </style>
        
        <div style="text-align: center;">
            <p style="font-size: 14px; color: #aaa; margin-bottom: 0;">MATCH SCORE</p>
            <h1 style="color: {score_color}; font-size: 48px; margin: 0;">{match_score}%</h1>
        </div>
        """
        
        # Red Flags
        if red_flags:
            html += "<h3>⚠️ Critical Red Flags</h3><ul>"
            for flag in red_flags:
                html += f"<li class='warning'>{flag}</li>"
            html += "</ul>"
            
        # Analysis
        html += "<h3>✅ Strong Matches</h3><ul>"
        if strong_matches:
            for match in strong_matches:
                if isinstance(match, dict):
                    html += f"<li><b>{match.get('skill')}</b>: {match.get('evidence', '')}</li>"
                else:
                    html += f"<li>{match}</li>"
        else:
            html += "<li>No strong matches found.</li>"
        html += "</ul>"
        
        html += "<h3>❌ Missing Skills & Gaps</h3><ul>"
        if missing_skills:
            for gap in missing_skills:
                if isinstance(gap, dict):
                    html += f"<li><b>{gap.get('skill')}</b>: {gap.get('recommendation', '')}</li>"
                else:
                    html += f"<li>{gap}</li>"
        else:
            html += "<li>No major skills missing!</li>"
        html += "</ul>"

        # Style Critique
        if style_critique:
             html += "<h3>🎨 Style & Formatting</h3><ul>"
             for critique in style_critique:
                 html += f"<li>{critique}</li>"
             html += "</ul>"

        # Interview Prep
        if interview_prep:
            html += "<h3>🎤 Interview Prep Questions</h3><ol>"
            for q in interview_prep:
                html += f"<li>{q}</li>"
            html += "</ol>"

        self.results_area.setHtml(html)

    def handle_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.analyze_btn.setEnabled(True)
        self.select_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", f"An error occurred:\n{error_msg}")
        self.results_area.setHtml(f"<p style='color: red;'>Analysis failed: {error_msg}</p>")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set app style
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
