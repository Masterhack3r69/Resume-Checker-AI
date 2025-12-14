
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
        self.resize(720, 502)
        self.center_window()
        self.pdf_path = None
        
        self.apply_styles()
        self.setup_ui()

    def center_window(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header Title
        header_layout = QHBoxLayout()
        title_label = QLabel("Resume Checker AI")
        title_label.setObjectName("titleLabel")
        subtitle_label = QLabel("Premium Edition")
        subtitle_label.setObjectName("subtitleLabel")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Main Content Area
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setSpacing(10)
        content_layout.setContentsMargins(15, 15, 15, 15)
        
        # 1. File Upload Section
        file_label_title = QLabel("1. Upload Resume")
        file_label_title.setObjectName("sectionTitle")
        content_layout.addWidget(file_label_title)

        file_box = QFrame()
        file_box.setObjectName("sectionBox")
        file_layout_inner = QHBoxLayout(file_box)
        file_layout_inner.setContentsMargins(15, 15, 15, 15)
        
        self.select_btn = QPushButton("📁 Select PDF Resume")
        self.select_btn.setObjectName("uploadBtn")
        self.select_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.select_btn.clicked.connect(self.select_file)
        
        self.file_label = QLabel("No file selected")
        self.file_label.setObjectName("fileLabel")
        
        file_layout_inner.addWidget(self.select_btn)
        file_layout_inner.addWidget(self.file_label)
        file_layout_inner.addStretch()
        
        content_layout.addWidget(file_box)

        # 2. Job Description Section
        jd_label_title = QLabel("2. Job Description")
        jd_label_title.setObjectName("sectionTitle")
        content_layout.addWidget(jd_label_title)

        self.jd_input = QTextEdit()
        self.jd_input.setPlaceholderText("Paste the job description here...")
        self.jd_input.setMinimumHeight(120)
        content_layout.addWidget(self.jd_input)

        # 3. Action Section
        self.analyze_btn = QPushButton("✨ Analyze Resume")
        self.analyze_btn.setObjectName("analyzeBtn")
        self.analyze_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.analyze_btn.clicked.connect(self.start_analysis)
        self.analyze_btn.setMinimumHeight(45)
        content_layout.addWidget(self.analyze_btn)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0) # Indeterminate
        content_layout.addWidget(self.progress_bar)

        main_layout.addWidget(content_frame)

        # Results Area
        results_label = QLabel("Analysis Report")
        results_label.setObjectName("subHeaderLabel")
        main_layout.addWidget(results_label)

        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        self.results_area.setPlaceholderText("Analysis results will appear here...")
        main_layout.addWidget(self.results_area)

    def apply_styles(self):
        # Premium Dark Theme Palette
        # Background: #0f172a (Slate 900)
        # Surface: #1e293b (Slate 800)
        # Accent: #6366f1 (Indigo 500)
        # Text: #f8fafc (Slate 50)
        
        dark_palette = QPalette()
        bg_color = QColor(15, 23, 42)
        surface_color = QColor(30, 41, 59)
        text_color = QColor(248, 250, 252)
        accent_color = QColor(99, 102, 241)
        
        dark_palette.setColor(QPalette.ColorRole.Window, bg_color)
        dark_palette.setColor(QPalette.ColorRole.WindowText, text_color)
        dark_palette.setColor(QPalette.ColorRole.Base, surface_color)
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, bg_color)
        dark_palette.setColor(QPalette.ColorRole.Text, text_color)
        dark_palette.setColor(QPalette.ColorRole.Button, surface_color)
        dark_palette.setColor(QPalette.ColorRole.ButtonText, text_color)
        dark_palette.setColor(QPalette.ColorRole.Link, accent_color)
        
        QApplication.setPalette(dark_palette)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f172a;
            }
            QLabel {
                font-family: 'Segoe UI', 'Inter', sans-serif;
                font-size: 13px;
                color: #cbd5e1;
            }
            QLabel#titleLabel {
                font-size: 22px;
                font-weight: 800;
                color: #f8fafc;
                margin-right: 8px;
            }
            QLabel#subtitleLabel {
                font-size: 11px;
                font-weight: 600;
                color: #6366f1;
                background-color: #1e1b4b;
                border: 1px solid #312e81;
                border-radius: 4px;
                padding: 2px 6px;
                margin-top: 6px;
            }
            QLabel#sectionTitle {
                font-size: 14px;
                font-weight: 600;
                color: #94a3b8;
                margin-top: 5px;
                margin-bottom: 3px;
            }
            QLabel#subHeaderLabel {
                font-size: 16px;
                font-weight: 700;
                color: #f8fafc;
                margin-top: 5px;
            }
            QFrame#contentFrame {
                background-color: #1e293b;
                border-radius: 12px;
                border: 1px solid #334155;
            }
            QFrame#sectionBox {
                background-color: #0f172a;
                border-radius: 8px;
                border: 1px solid #334155;
            }
            QPushButton {
                background-color: #334155;
                color: #e2e8f0;
                border: 1px solid #475569;
                border-radius: 6px;
                padding: 8px 12px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #475569;
                border-color: #64748b;
            }
            QPushButton#uploadBtn {
                background-color: #1e293b;
                text-align: left;
                padding-left: 15px;
            }
            QPushButton#analyzeBtn {
                background-color: #4f46e5;
                border: none;
                color: white;
                font-size: 15px;
                font-weight: bold;
                border-radius: 8px;
                margin-top: 10px;
            }
            QPushButton#analyzeBtn:hover {
                background-color: #4338ca;
            }
            QPushButton#analyzeBtn:disabled {
                background-color: #334155;
                color: #94a3b8;
            }
            QTextEdit {
                background-color: #0f172a;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace; 
                font-size: 13px;
                selection-background-color: #6366f1;
                line-height: 1.4;
            }
            QTextEdit:focus {
                border: 1px solid #6366f1;
            }
            QLabel#fileLabel {
                color: #94a3b8;
                font-style: italic;
                margin-left: 15px;
            }
            QProgressBar {
                background-color: #0f172a;
                border: none;
                border-radius: 6px;
                height: 8px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #6366f1;
                border-radius: 6px;
            }
            QScrollBar:vertical {
                border: none;
                background: #0f172a;
                width: 12px;
                margin: 0px; 
            }
            QScrollBar::handle:vertical {
                background: #334155;
                min-height: 30px;
                border-radius: 6px;
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
            self.select_btn.setStyleSheet("background-color: #065f46; border-color: #059669; color: #d1fae5;") # Emerald tint
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
        self.results_area.setHtml("<div style='color: #94a3b8; text-align: center; margin-top: 40px; font-family: Segoe UI;'><h3>🤖 Analyzing Resume...</h3><p>Extracting text, verifying skills, and applying recruiter heuristics.</p></div>")

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
        score_color = "#4ade80" if match_score >= 80 else "#facc15" if match_score >= 50 else "#f87171"
        
        # Enhanced HTML Report
        html = f"""
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; color: #e2e8f0; }}
            h2 {{ color: {score_color}; margin-top: 0; }}
            .card {{ 
                background-color: #1e293b; 
                border: 1px solid #334155; 
                border-radius: 8px; 
                padding: 15px; 
                margin-bottom: 20px; 
            }}
            .score-container {{
                text-align: center;
                padding: 20px;
                background-color: #0f172a;
                border-radius: 12px;
                margin-bottom: 25px;
                border: 1px solid #334155;
            }}
            .score-circle {{
                font-size: 56px;
                font-weight: bold;
                color: {score_color};
                margin: 0;
            }}
            .score-label {{
                color: #94a3b8;
                font-size: 14px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            h3 {{
                color: #f8fafc;
                font-size: 18px;
                border-bottom: 2px solid #334155;
                padding-bottom: 8px;
                margin-top: 0;
            }}
            ul, ol {{ padding-left: 20px; margin-top: 10px; }}
            li {{ margin-bottom: 8px; line-height: 1.6; }}
            .match-item {{ color: #cbd5e1; }}
            .match-skill {{ color: #4ade80; font-weight: bold; }}
            .miss-skill {{ color: #f87171; font-weight: bold; }}
            .warning {{ color: #f87171; }}
            .tip {{ color: #94a3b8; font-style: italic; }}
        </style>
        
        <div class="score-container">
            <p class="score-label">Match Score</p>
            <h1 class="score-circle">{match_score}%</h1>
        </div>
        """
        
        # Red Flags
        if red_flags:
            html += """<div class="card" style="border-left: 4px solid #f87171;">
                        <h3>⚠️ Critical Red Flags</h3><ul>"""
            for flag in red_flags:
                html += f"<li class='warning'>{flag}</li>"
            html += "</ul></div>"
            
        # Matches
        html += """<div class="card" style="border-left: 4px solid #4ade80;">
                    <h3>✅ Strong Matches</h3><ul>"""
        if strong_matches:
            for match in strong_matches:
                if isinstance(match, dict):
                    html += f"<li class='match-item'><span class='match-skill'>{match.get('skill')}</span>: {match.get('evidence', '')}</li>"
                else:
                    html += f"<li>{match}</li>"
        else:
            html += "<li>No strong matches found.</li>"
        html += "</ul></div>"
        
        # Missing Skills
        html += """<div class="card" style="border-left: 4px solid #fbbf24;">
                    <h3>❌ Missing Skills & Gaps</h3><ul>"""
        if missing_skills:
            for gap in missing_skills:
                if isinstance(gap, dict):
                    html += f"<li class='match-item'><span class='miss-skill'>{gap.get('skill')}</span>: {gap.get('recommendation', '')}</li>"
                else:
                    html += f"<li>{gap}</li>"
        else:
            html += "<li>No major skills missing!</li>"
        html += "</ul></div>"

        # Style Critique
        if style_critique:
             html += """<div class="card"><h3>🎨 Style & Formatting</h3><ul>"""
             for critique in style_critique:
                 html += f"<li>{critique}</li>"
             html += "</ul></div>"

        # Interview Prep
        if interview_prep:
            html += """<div class="card"><h3>🎤 Interview Prep</h3><ol>"""
            for q in interview_prep:
                html += f"<li>{q}</li>"
            html += "</ol></div>"

        self.results_area.setHtml(html)

    def handle_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.analyze_btn.setEnabled(True)
        self.select_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", f"An error occurred:\n{error_msg}")
        self.results_area.setHtml(f"<div style='color: #f87171; padding: 20px; text-align: center;'><h3>Analysis Failed</h3><p>{error_msg}</p></div>")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set app style
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
