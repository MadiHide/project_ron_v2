import sys
import time # Added for sleep in worker
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QFrame, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QPalette, QColor, QFont, QPixmap, QPainter
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread, QTimer

# Assuming decision_logic.py, and exploiter modules are in the same pentest_project directory or accessible via PYTHONPATH
from decision_logic import DecisionEngine
# Import exploiter modules - for now, we'll simulate their calls within BackendWorker
# from exploit_modules.ssh_exploiter import SSHExploiter
# from exploit_modules.http_exploiter import HTTPExploiter

# Worker para simular o backend e emitir sinais
class BackendWorker(QObject):
    progress_update = pyqtSignal(str) # Sinal para logs
    result_update = pyqtSignal(str)   # Sinal para resultados
    status_update = pyqtSignal(str)   # Sinal para status geral
    vulnerability_found = pyqtSignal(str, str) # Sinal para animação (tipo, detalhe)
    ask_user_decision = pyqtSignal(str) # Sinal para pedir decisão ao usuário
    finished = pyqtSignal() # Signal when the worker's main task loop is done or stopped

    def __init__(self):
        super().__init__()
        self.is_running = False
        self.target = ""
        self.decision_engine = DecisionEngine()
        self.current_service_suggestions = []
        self.current_suggestion_index = 0
        self.current_pending_action_details = None
        self.services_to_process = [] # list of (service_name, port, details) tuples
        self.service_processing_index = 0
        self.current_pending_action_details_for_gui = None # Added to store details for GUI confirmation path

    def _process_service_or_suggestion(self):
        if not self.is_running:
            self.status_update.emit("Processo interrompido.")
            self.progress_update.emit("[INFO] Processo interrompido.")
            self.finished.emit()
            return

        if self.current_pending_action_details: # This means user confirmed
            action_details = self.current_pending_action_details
            self.current_pending_action_details = None # Clear it
            self.progress_update.emit(f"[ACTION] Executando ação: {action_details.get('action', 'N/A')}") # Corrected f-string
            time.sleep(1) # Simulate work
            self.result_update.emit(f"Resultado da ação {action_details.get('action')}: Sucesso (Simulado)") # Corrected f-string
            if "http" in action_details.get('action', '').lower(): # Corrected f-string
                 self.vulnerability_found.emit("xss_attempt", self.target)
            
            self.current_suggestion_index += 1
            self._process_next_suggestion_for_current_service()
            return

        if self.current_service_suggestions and self.current_suggestion_index < len(self.current_service_suggestions):
            suggestion = self.current_service_suggestions[self.current_suggestion_index]
            self.current_pending_action_details_for_gui = suggestion['action_details']
            self.ask_user_decision.emit(suggestion['text'])
            return
        else:
            self.service_processing_index += 1
            self._process_next_service()

    def _process_next_suggestion_for_current_service(self):
        if self.current_service_suggestions and self.current_suggestion_index < len(self.current_service_suggestions):
            suggestion = self.current_service_suggestions[self.current_suggestion_index]
            self.current_pending_action_details_for_gui = suggestion['action_details']
            self.ask_user_decision.emit(suggestion['text'])
        else:
            self.service_processing_index += 1
            self._process_next_service()

    def _process_next_service(self):
        if self.service_processing_index < len(self.services_to_process):
            service_name, port, details = self.services_to_process[self.service_processing_index]
            self.progress_update.emit(f"[DECISION] Analisando serviço {service_name} na porta {port}.")
            self.current_service_suggestions = self.decision_engine.get_suggestions(service_name, port, details)
            self.current_suggestion_index = 0
            self._process_next_suggestion_for_current_service()
        else:
            self.status_update.emit("Pentest concluído.")
            self.progress_update.emit("[INFO] Todas as descobertas processadas.")
            self.is_running = False
            self.finished.emit()

    def run_pentest_flow(self, target):
        self.is_running = True
        self.target = target
        self.status_update.emit(f"Iniciando varredura em {self.target}...")
        self.progress_update.emit(f"[INFO] Varredura iniciada em {self.target}.")
        
        self.services_to_process = []
        self.service_processing_index = 0
        self.current_service_suggestions = []
        self.current_suggestion_index = 0
        self.current_pending_action_details = None
        self.current_pending_action_details_for_gui = None

        time.sleep(2)
        if not self.is_running: self.stop_process(); return
        self.progress_update.emit("[SCAN] Nmap scan concluído (simulado).")
        
        simulated_nmap_results = [
            {"port": 80, "name": "http", "details": {"product": "Apache httpd"}},
            {"port": 22, "name": "ssh", "details": {"product": "OpenSSH"}}
        ]

        for r in simulated_nmap_results:
            self.result_update.emit(f"Host: {self.target}\n  Porta {r['port']} ({r['name']}): Aberta - {r['details']['product']}")
            self.vulnerability_found.emit(f"{r['name']}_open", self.target)
            self.services_to_process.append((r['name'], r['port'], r['details']))
        
        if not self.services_to_process:
            self.progress_update.emit("[INFO] Nenhum serviço ativo encontrado para processar.")
            self.status_update.emit("Concluído - Nenhum serviço encontrado.")
            self.is_running = False
            self.finished.emit()
            return

        self.status_update.emit("Analisando serviços e buscando sugestões...")
        self._process_next_service()

    def user_responded_to_decision(self, confirmed):
        if not self.is_running:
            return

        if confirmed:
            self.progress_update.emit("[USER_ACTION] Usuário confirmou a sugestão.")
            self.current_pending_action_details = self.current_pending_action_details_for_gui
        else:
            self.progress_update.emit("[USER_ACTION] Usuário ignorou a sugestão.")
            self.current_pending_action_details = None
            self.current_suggestion_index += 1
        
        self.current_pending_action_details_for_gui = None
        self._process_service_or_suggestion()

    def stop_process(self):
        if self.is_running:
            self.progress_update.emit("[INFO] Interrompendo processo...")
            self.is_running = False

class AnimationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(200)
        self.setStyleSheet("background-color: #101010; border: 1px dashed #0A7E07;")
        self.animation_step = 0
        self.target_infected_parts = {} 
        self.current_animation_type = None
        self.virus_pos_x = 20
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_frame)

    def start_infection_animation(self, type, detail):
        self.current_animation_type = type 
        self.animation_step = 0 
        self.virus_pos_x = 20
        if type.endswith("_open"):
            part_name = type.split("_")[0]
            if part_name not in self.target_infected_parts:
                self.target_infected_parts[part_name] = 1
        elif type.endswith("_attempt") or type.endswith("_vuln"):
            part_name = type.split("_")[0]
            self.target_infected_parts[part_name] = self.target_infected_parts.get(part_name, 0) + 1
        if not self.timer.isActive():
            self.timer.start(100)
        self.update()

    def next_frame(self):
        self.animation_step += 1
        max_steps = (self.width() // 2 - 70 - 20) // 5
        if max_steps <=0: max_steps = 10
        if self.animation_step <= max_steps:
            self.virus_pos_x = 20 + self.animation_step * 5
        else:
            self.timer.stop()
        self.update() 

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(16, 16, 16))
        target_rect_x = self.width() // 2 - 50
        target_rect_y = self.height() // 2 - 30
        target_rect_w = 100
        target_rect_h = 60
        painter.setPen(QColor(0, 200, 0)) 
        painter.setBrush(QColor(30, 50, 30))
        painter.drawRect(target_rect_x, target_rect_y, target_rect_w, target_rect_h)
        painter.drawText(target_rect_x + 10, target_rect_y + 35, "ALVO")
        for i, (part, intensity) in enumerate(self.target_infected_parts.items()): # Use enumerate for index
            color_intensity = min(255, 50 + intensity * 50)
            painter.setBrush(QColor(color_intensity, 0, 0, 180 + min(75, intensity*20) ))
            painter.drawRect(target_rect_x + (i % 2) * (target_rect_w // 2),
                             target_rect_y + (i // 2) * (target_rect_h // 2), # Basic grid layout for parts
                             target_rect_w // 2, 
                             target_rect_h // 2 )
        if self.timer.isActive():
            painter.setBrush(Qt.red)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(self.virus_pos_x, self.height() // 2 - 5, 10, 10)

class PentestMainWindow(QMainWindow):
    user_decision_signal = pyqtSignal(bool)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manus Pentest Automation - v0.4 Corrected")
        self.setGeometry(100, 100, 1200, 800)
        self.backend_thread = None
        self.backend_worker = None
        self.init_ui()
        self.apply_dark_theme()

    def apply_dark_theme(self):
        self.setAutoFillBackground(True); palette = QPalette()
        palette.setColor(QPalette.Window, QColor(35,35,35)); palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25,25,25)); palette.setColor(QPalette.AlternateBase, QColor(53,53,53))
        palette.setColor(QPalette.ToolTipBase, Qt.white); palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white); palette.setColor(QPalette.Button, QColor(53,53,53))
        palette.setColor(QPalette.ButtonText, Qt.white); palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42,130,218)); palette.setColor(QPalette.Highlight, QColor(42,130,218))
        palette.setColor(QPalette.HighlightedText, Qt.black); self.setPalette(palette)
        style_sheet = """
            QMainWindow{background-color:#232323} QLineEdit{background-color:#191919;border:1px solid #0A7E07;color:#0A7E07;padding:5px;font-family:Monospace}
            QTextEdit{background-color:#101010;border:1px solid #0A7E07;color:#00FF00;font-family:Monospace;font-size:10pt}
            QPushButton{background-color:#353535;border:1px solid #0A7E07;color:#0A7E07;padding:5px 10px;font-family:Monospace}
            QPushButton:hover{background-color:#454545} QPushButton:pressed{background-color:#191919}
            QLabel{color:#E0E0E0;font-family:Monospace} QFrame#separator_line{background-color:#0A7E07}
            QWidget#DecisionPanel{background-color:#1E1E1E;border:2px solid #FFBF00;border-radius:5px}
            QLabel#DecisionLabel{color:#FFBF00;font-size:11pt}
            QPushButton#ConfirmButton{background-color:#006400;color:white} QPushButton#IgnoreButton{background-color:#8B0000;color:white}
        """
        self.setStyleSheet(style_sheet)

    def init_ui(self):
        central_widget=QWidget();self.setCentralWidget(central_widget);main_layout=QHBoxLayout(central_widget)
        left_panel_layout=QVBoxLayout();left_panel_widget=QWidget();left_panel_widget.setLayout(left_panel_layout);left_panel_widget.setFixedWidth(350)
        control_label=QLabel("CONTROLES");control_label.setFont(QFont("Monospace",12,QFont.Bold));left_panel_layout.addWidget(control_label)
        self.target_input=QLineEdit();self.target_input.setPlaceholderText("Alvo (ex: localhost)");self.target_input.setText("localhost");left_panel_layout.addWidget(self.target_input)
        self.start_button=QPushButton("INICIAR PENTEST");self.start_button.clicked.connect(self.start_pentest_clicked);left_panel_layout.addWidget(self.start_button)
        self.stop_button=QPushButton("PARAR");self.stop_button.clicked.connect(self.stop_pentest_clicked);self.stop_button.setEnabled(False);left_panel_layout.addWidget(self.stop_button)
        self.status_label=QLabel("Status: Ocioso");left_panel_layout.addWidget(self.status_label)
        separator1=QFrame();separator1.setObjectName("separator_line");separator1.setFrameShape(QFrame.HLine);separator1.setFrameShadow(QFrame.Sunken);separator1.setFixedHeight(2);left_panel_layout.addWidget(separator1)
        results_label=QLabel("DESCOBERTAS");results_label.setFont(QFont("Monospace",12,QFont.Bold));left_panel_layout.addWidget(results_label)
        self.results_display=QTextEdit();self.results_display.setReadOnly(True);self.results_display.setPlaceholderText("Resultados...");left_panel_layout.addWidget(self.results_display);left_panel_layout.addStretch(1)
        right_panel_layout=QVBoxLayout();right_panel_widget=QWidget();right_panel_widget.setLayout(right_panel_layout)
        self.animation_widget=AnimationWidget();right_panel_layout.addWidget(self.animation_widget,1)
        separator2=QFrame();separator2.setObjectName("separator_line");separator2.setFrameShape(QFrame.HLine);separator2.setFrameShadow(QFrame.Sunken);separator2.setFixedHeight(2);right_panel_layout.addWidget(separator2)
        log_label=QLabel("LOG DE ATIVIDADES");log_label.setFont(QFont("Monospace",12,QFont.Bold));right_panel_layout.addWidget(log_label)
        self.log_display=QTextEdit();self.log_display.setReadOnly(True);self.log_display.setPlaceholderText("Logs...");right_panel_layout.addWidget(self.log_display,2)
        main_layout.addWidget(left_panel_widget);main_layout.addWidget(right_panel_widget)
        self.decision_panel=QWidget(self);self.decision_panel.setObjectName("DecisionPanel");self.decision_panel.setFixedWidth(450);self.decision_panel.setFixedHeight(180)
        decision_layout=QVBoxLayout(self.decision_panel)
        self.decision_label=QLabel("Aguardando decisão...");self.decision_label.setObjectName("DecisionLabel");self.decision_label.setWordWrap(True);self.decision_label.setAlignment(Qt.AlignCenter);decision_layout.addWidget(self.decision_label)
        decision_buttons_layout=QHBoxLayout()
        self.confirm_button=QPushButton("Confirmar Ação");self.confirm_button.setObjectName("ConfirmButton");self.confirm_button.clicked.connect(self.user_confirmed_decision)
        self.ignore_button=QPushButton("Ignorar Sugestão");self.ignore_button.setObjectName("IgnoreButton");self.ignore_button.clicked.connect(self.user_ignored_decision)
        decision_buttons_layout.addWidget(self.confirm_button);decision_buttons_layout.addWidget(self.ignore_button);decision_layout.addLayout(decision_buttons_layout);self.decision_panel.hide()

    def update_log(self,message):self.log_display.append(message)
    def update_results(self,result_text):self.results_display.append(result_text)
    def update_status(self,status_text):self.status_label.setText(f"Status: {status_text}")
    def trigger_animation(self,type,detail):self.animation_widget.start_infection_animation(type,detail)
    def show_decision_panel(self,question):
        self.decision_label.setText(question);panel_x=(self.width()-self.decision_panel.width())//2;panel_y=(self.height()-self.decision_panel.height())//2
        self.decision_panel.move(panel_x,panel_y);self.decision_panel.show();self.decision_panel.raise_();self.start_button.setEnabled(False);self.stop_button.setEnabled(False)
    def user_confirmed_decision(self):
        self.decision_panel.hide()
        if self.backend_worker:self.user_decision_signal.emit(True)
    def user_ignored_decision(self):
        self.decision_panel.hide()
        if self.backend_worker:self.user_decision_signal.emit(False)
    def start_pentest_clicked(self):
        target=self.target_input.text().strip()
        if not target:self.update_log("[ERROR] Alvo não especificado.");self.status_label.setText("Status: Erro - Alvo");return
        self.log_display.clear();self.results_display.clear();self.animation_widget.target_infected_parts={};self.animation_widget.update()
        self.update_log(f"[GUI] Iniciando pentest para: {target}");self.start_button.setEnabled(False);self.stop_button.setEnabled(True)
        self.backend_thread=QThread();self.backend_worker=BackendWorker();self.backend_worker.moveToThread(self.backend_thread)
        self.backend_worker.progress_update.connect(self.update_log);self.backend_worker.result_update.connect(self.update_results)
        self.backend_worker.status_update.connect(self.update_status);self.backend_worker.vulnerability_found.connect(self.trigger_animation)
        self.backend_worker.ask_user_decision.connect(self.show_decision_panel);self.user_decision_signal.connect(self.backend_worker.user_responded_to_decision)
        self.backend_worker.finished.connect(self.on_backend_finished)
        self.backend_thread.started.connect(lambda:self.backend_worker.run_pentest_flow(target));self.backend_thread.finished.connect(self.backend_thread.deleteLater);self.backend_thread.start()
        self.update_status(f"Iniciando em {target}...")
    def on_backend_finished(self):
        self.update_log("[GUI] Processo do backend finalizado.");self.start_button.setEnabled(True);self.stop_button.setEnabled(False)
        if not self.decision_panel.isVisible():
            current_status=self.status_label.text()
            if "Iniciando" in current_status or "Analisando" in current_status or "interrompido" not in current_status.lower():self.update_status("Concluído")
    def stop_pentest_clicked(self):
        self.update_log("[GUI] Botão PARAR clicado.")
        if self.backend_worker:self.backend_worker.stop_process()
        if self.decision_panel.isVisible():self.decision_panel.hide()
    def closeEvent(self,event):
        self.stop_pentest_clicked()
        if self.backend_thread and self.backend_thread.isRunning():self.backend_thread.quit();self.backend_thread.wait(1000)
        super().closeEvent(event)

if __name__=="__main__":
    app=QApplication(sys.argv);main_window=PentestMainWindow();main_window.show();sys.exit(app.exec_())

