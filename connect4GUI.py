from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen, QRadialGradient, QLinearGradient
import sys
import random

from functions import ROWS, COLS, get_moves, drop_piece, is_terminal, count_fours

class BoardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.cell_size = 80
        self.padding = 20
        self.setMinimumSize(COLS * self.cell_size + 2 * self.padding, 
                           ROWS * self.cell_size + 2 * self.padding)
        self.hover_col = -1
        self.setMouseTracking(True)
        
    def paintEvent(self, event):
        height = max(1, self.height())  

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background gradient
        gradient = QLinearGradient(0, 0, 0, height)
        gradient.setColorAt(0, QColor(37, 99, 235))
        gradient.setColorAt(1, QColor(29, 78, 216))
        painter.fillRect(self.rect(), gradient)
        
        # Draw hover column highlight
        if self.hover_col >= 0:
            painter.fillRect(
                self.hover_col * self.cell_size + self.padding,
                self.padding,
                self.cell_size,
                ROWS * self.cell_size,
                QColor(255, 255, 255, 30)
            )
        
        # Draw cells
        for row in range(ROWS):
            for col in range(COLS):
                x = col * self.cell_size + self.padding + self.cell_size // 2
                y = row * self.cell_size + self.padding + self.cell_size // 2
                radius = self.cell_size // 2 - 10
                
                cell = self.board[row][col]
                
                # Draw slot (darker circle)
                painter.setPen(QPen(QColor(30, 58, 138), 3))
                painter.setBrush(QColor(30, 58, 138))
                painter.drawEllipse(x - radius - 3, y - radius - 3, 
                                   (radius + 3) * 2, (radius + 3) * 2)
                
                # Draw piece
                if cell == 0:
                    # Empty slot
                    gradient = QRadialGradient(x, y, max(1, radius * 1.5))
                    gradient.setColorAt(0, QColor(230, 230, 230))
                    gradient.setColorAt(1, QColor(180, 180, 180))
                    painter.setBrush(gradient)
                    painter.setPen(QPen(QColor(150, 150, 150), 2))
                elif cell == 1:
                    # Red piece with gradient
                    gradient = QRadialGradient(x, y, max(1, radius * 1.5))
                    gradient.setColorAt(0, QColor(248, 113, 113))
                    gradient.setColorAt(0.7, QColor(220, 38, 38))
                    gradient.setColorAt(1, QColor(153, 27, 27))
                    painter.setBrush(gradient)
                    painter.setPen(QPen(QColor(153, 27, 27), 3))
                else:  # cell == 2
                    # Yellow piece with gradient
                    gradient = QRadialGradient(x, y, max(1, radius * 1.5))
                    gradient.setColorAt(0, QColor(254, 240, 138))
                    gradient.setColorAt(0.7, QColor(234, 179, 8))
                    gradient.setColorAt(1, QColor(161, 98, 7))
                    painter.setBrush(gradient)
                    painter.setPen(QPen(QColor(161, 98, 7), 3))
                
                painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)
    
    def mouseMoveEvent(self, event):
        col = (event.x() - self.padding) // self.cell_size
        if 0 <= col < COLS:
            self.hover_col = col
        else:
            self.hover_col = -1
        self.update()
    
    def leaveEvent(self, event):
        self.hover_col = -1
        self.update()
    
    def mousePressEvent(self, event):
        col = (event.x() - self.padding) // self.cell_size
        if 0 <= col < COLS and self.main_window:
            self.main_window.on_column_click(col)


class Connect4Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Connect 4")
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f172a;
            }
            QLabel {
                color: white;
                font-size: 20px;
                font-weight: 600;
            }
            QPushButton {
                background: #334155;
                color: white;
                border: 2px solid #475569;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 16px;
                transition: 200ms;
            }
            QPushButton:hover {
                background: #475569;
            }
            QPushButton:pressed {
                background: #1e293b;
            }
        """)
        
        self.game_over = False
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("CONNECT 4")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 36px; font-weight: bold; color: white;")
        layout.addWidget(title)
        
        # Status label
        self.status_label = QLabel("Your Turn")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 20px; color: #f87171;")
        layout.addWidget(self.status_label)
        
        # Board
        self.board_widget = BoardWidget(self)
        layout.addWidget(self.board_widget, alignment=Qt.AlignCenter)
        
        # Button layout
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.reset_btn = QPushButton("New Game")
        self.reset_btn.clicked.connect(self.reset_game)
        btn_layout.addWidget(self.reset_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.resize(700, 750)
    
    def on_column_click(self, col):
        if self.game_over or col not in get_moves(self.board_widget.board):
            return

        # Player move
        self.board_widget.board = drop_piece(self.board_widget.board, col, 1)
        self.board_widget.update()

        # Initialize counters once
        if not hasattr(self, "player_prev_fours"):
            self.player_prev_fours = 0
            self.player_fours = 0
            self.ai_prev_fours = 0
            self.ai_fours = 0

        # Player scoring
        current_player_fours = count_fours(self.board_widget.board, 1)
        delta = current_player_fours - self.player_prev_fours

        if delta > 0:
            self.player_fours += delta
            self.status_label.setText(
                f"🎉 You connected {delta}! You: {self.player_fours} — AI: {self.ai_fours} 🎉"
            )
            self.status_label.setStyleSheet("font-size: 24px; color: #10b981;")
        else:
            self.status_label.setText(
                f"Your Turn — You: {self.player_fours} | AI: {self.ai_fours}"
            )
            self.status_label.setStyleSheet("font-size: 20px; color: #f87171;")

        self.player_prev_fours = current_player_fours

        # Board full?
        if is_terminal(self.board_widget.board):
            self.end_game()
            return

        # AI move
        self.status_label.setText("AI is thinking...")
        self.status_label.setStyleSheet("font-size: 20px; color: #fbbf24;")
        QTimer.singleShot(500, self.ai_move)

    def ai_move(self):
        valid_moves = get_moves(self.board_widget.board)
        if not valid_moves:
            self.end_game()
            return

        ai_col = random.choice(valid_moves)
        self.board_widget.board = drop_piece(self.board_widget.board, ai_col, 2)
        self.board_widget.update()

        # AI scoring
        current_ai_fours = count_fours(self.board_widget.board, 2)
        delta = current_ai_fours - self.ai_prev_fours

        if delta > 0:
            self.ai_fours += delta
            self.status_label.setText(
                f"🤖 AI connected {delta}! You: {self.player_fours} — AI: {self.ai_fours}"
            )
            self.status_label.setStyleSheet("font-size: 22px; color: #fbbf24;")
        else:
            self.status_label.setText(
                f"Your Turn — You: {self.player_fours} | AI: {self.ai_fours}"
            )
            self.status_label.setStyleSheet("font-size: 20px; color: #f87171;")

        self.ai_prev_fours = current_ai_fours

        # End game if board full
        if is_terminal(self.board_widget.board):
            self.end_game()
    
    def reset_game(self):
        self.board_widget.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.game_over = False

        self.player_fours = 0
        self.player_prev_fours = 0
        self.ai_fours = 0
        self.ai_prev_fours = 0

        self.status_label.setText("Your Turn — You: 0 | AI: 0")
        self.status_label.setStyleSheet("font-size: 20px; color: #f87171;")
        self.board_widget.update()
        
    def end_game(self):
        self.game_over = True

        if self.player_fours > self.ai_fours:
            self.status_label.setText(f"🎉 You Win! Final Score — You: {self.player_fours}, AI: {self.ai_fours}")
            self.status_label.setStyleSheet("font-size: 24px; color: #10b981;")
        elif self.ai_fours > self.player_fours:
            self.status_label.setText(f"AI Wins! Final Score — You: {self.player_fours}, AI: {self.ai_fours}")
            self.status_label.setStyleSheet("font-size: 24px; color: #ef4444;")
        else:
            self.status_label.setText(f"Draw! Final Score — You: {self.player_fours}, AI: {self.ai_fours}")
            self.status_label.setStyleSheet("font-size: 24px; color: #fbbf24;")

    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Connect4Window()
    QTimer.singleShot(10, window.show)
    sys.exit(app.exec())
