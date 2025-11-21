from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QRadialGradient, QLinearGradient
import sys
import random
import os

from functions import ROWS, COLS, get_moves, drop_piece, is_terminal, count_fours
from treeGraphWindow import GraphWindow
from PyQt5.QtWidgets import QComboBox

from minimax import minimax_with_tree as minimax_func
from minimax import build_graphviz as minimax_build_graph
from minimax import write_tree_to_file as minimax_write_tree
from minimax import DEFAULT_OUTPUT_NAME as MINIMAX_DEFAULT_NAME
MINIMAX_AVAILABLE = True

from alpha_beta import ab_pruning_with_tree as ab_func
from alpha_beta import build_graphviz as ab_build_graph
from alpha_beta import write_tree_to_file as ab_write_tree
from alpha_beta import DEFAULT_OUTPUT_NAME as AB_DEFAULT_NAME
AB_AVAILABLE = True

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

        # Background gradient
        gradient = QLinearGradient(0, 0, 0, height)
        gradient.setColorAt(0, QColor(37, 99, 235))
        gradient.setColorAt(1, QColor(29, 78, 216))
        painter.fillRect(self.rect(), gradient)

        # Hover column
        if self.hover_col >= 0:
            painter.fillRect(
                self.hover_col * self.cell_size + self.padding,
                self.padding,
                self.cell_size,
                ROWS * self.cell_size,
                QColor(255, 255, 255, 30)
            )

        # Draw board cells
        for row in range(ROWS):
            for col in range(COLS):
                x = col * self.cell_size + self.padding + self.cell_size // 2
                y = row * self.cell_size + self.padding + self.cell_size // 2
                radius = self.cell_size // 2 - 10
                cell = self.board[row][col]

                # Slot bg
                painter.setPen(QPen(QColor(30, 58, 138), 3))
                painter.setBrush(QColor(30, 58, 138))
                painter.drawEllipse(x - radius - 3, y - radius - 3, 
                                    (radius + 3) * 2, (radius + 3) * 2)

                # Piece rendering
                if cell == 0:
                    grad = QRadialGradient(x, y, max(1, radius * 1.5))
                    grad.setColorAt(0, QColor(230, 230, 230))
                    grad.setColorAt(1, QColor(180, 180, 180))
                    painter.setBrush(grad)
                    painter.setPen(QPen(QColor(150, 150, 150), 2))
                elif cell == 1:
                    grad = QRadialGradient(x, y, max(1, radius * 1.5))
                    grad.setColorAt(0, QColor(248, 113, 113))
                    grad.setColorAt(0.7, QColor(220, 38, 38))
                    grad.setColorAt(1, QColor(153, 27, 27))
                    painter.setBrush(grad)
                    painter.setPen(QPen(QColor(153, 27, 27), 3))
                else:  # AI piece
                    grad = QRadialGradient(x, y, max(1, radius * 1.5))
                    grad.setColorAt(0, QColor(254, 240, 138))
                    grad.setColorAt(0.7, QColor(234, 179, 8))
                    grad.setColorAt(1, QColor(161, 98, 7))
                    painter.setBrush(grad)
                    painter.setPen(QPen(QColor(161, 98, 7), 3))

                painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)

    def mouseMoveEvent(self, event):
        col = (event.x() - self.padding) // self.cell_size
        self.hover_col = col if 0 <= col < COLS else -1
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

        # ALGORITHMS WITH NO HARD-CODED NAMES
        self.available_algorithms = {}
        if MINIMAX_AVAILABLE:
            self.available_algorithms["Minimax"] = {
                "func": minimax_func,
                "build_graph": minimax_build_graph,
                "write_tree": minimax_write_tree,
                "output_base": MINIMAX_DEFAULT_NAME
            }
        if AB_AVAILABLE:
            self.available_algorithms["Alpha-Beta Pruning"] = {
                "func": ab_func,
                "build_graph": ab_build_graph,
                "write_tree": ab_write_tree,
                "output_base": AB_DEFAULT_NAME
            }

        self.algorithm_config = None
        self.is_player_turn = True
        self.game_over = False

        # ---- UI Setup ----
        self.setStyleSheet("""
            QMainWindow { background-color: #0f172a; }
            QLabel { color: white; font-size: 20px; font-weight: 600; }
            QPushButton {
                background: #334155; color: white;
                border: 2px solid #475569; border-radius: 10px;
                padding: 10px 20px; font-size: 16px;
            }
            QPushButton:hover { background: #475569; }
            QPushButton:pressed { background: #1e293b; }
            QComboBox {
                background: #1f2937; color: white;
                border: 1px solid #374151; padding: 6px;
                border-radius: 6px; min-width: 140px;
            }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("CONNECT 4")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 36px; font-weight: bold; color: white;")
        layout.addWidget(title)

        self.status_label = QLabel("Select algorithm and press Start")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 20px; color: #f87171;")
        layout.addWidget(self.status_label)

        # Algorithm selection row
        self.selection_widget = QWidget()
        sel_layout = QHBoxLayout(self.selection_widget)
        sel_layout.addStretch()

        sel_label = QLabel("Choose AI Algorithm:")
        sel_label.setStyleSheet("font-size: 18px; color: #e5e7eb;")
        sel_layout.addWidget(sel_label)

        self.alg_combo = QComboBox()
        self.alg_combo.addItems(list(self.available_algorithms.keys()))
        sel_layout.addWidget(self.alg_combo)

        self.start_btn = QPushButton("Start Game")
        self.start_btn.clicked.connect(self.start_game)
        sel_layout.addWidget(self.start_btn)

        sel_layout.addStretch()
        layout.addWidget(self.selection_widget)

        # Board (hidden before start)
        self.board_widget = BoardWidget(self)
        self.board_widget.setVisible(False)
        layout.addWidget(self.board_widget, alignment=Qt.AlignCenter)

        # Bottom buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.reset_btn = QPushButton("New Game")
        self.reset_btn.clicked.connect(self.reset_game)
        self.reset_btn.setVisible(False)
        btn_layout.addWidget(self.reset_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.resize(700, 750)

    def start_game(self):
        name = self.alg_combo.currentText()
        self.algorithm_config = self.available_algorithms[name]

        self.selection_widget.setVisible(False)
        self.board_widget.setVisible(True)
        self.reset_btn.setVisible(True)

        self.player_fours = 0
        self.player_prev_fours = 0
        self.ai_fours = 0
        self.ai_prev_fours = 0

        self.status_label.setText(f"Your Turn — You: 0 | AI: 0 ({name})")
        self.status_label.setStyleSheet("font-size: 20px; color: #f87171;")

    def on_column_click(self, col):
        if self.game_over or not self.is_player_turn or col not in get_moves(self.board_widget.board):
            return

        # Player move
        self.board_widget.board = drop_piece(self.board_widget.board, col, 1)
        self.board_widget.update()

        _, cur_fours = count_fours(self.board_widget.board, 1)
        delta = cur_fours - self.player_prev_fours

        if delta > 0:
            self.player_fours += delta
            self.status_label.setText(
                f"🎉 You connected {delta}! You: {self.player_fours} — AI: {self.ai_fours} 🎉"
            )
        else:
            self.status_label.setText(
                f"Your Turn — You: {self.player_fours} | AI: {self.ai_fours}"
            )

        self.player_prev_fours = cur_fours

        if is_terminal(self.board_widget.board):
            self.end_game()
            return

        self.is_player_turn = False
        self.status_label.setText("AI is thinking...")
        QTimer.singleShot(500, self.ai_move)

    def ai_move(self):
        moves = get_moves(self.board_widget.board)
        if not moves:
            self.end_game()
            return

        cfg = self.algorithm_config
        func = cfg["func"]
        build_graph = cfg["build_graph"]
        write_tree = cfg["write_tree"]
        output_base = cfg["output_base"]

        tree, _, ai_col = func(self.board_widget.board, 4, True)

        # Generate graph
        try:
            graph = build_graph(tree)
            png_path = output_base + ".png"
            txt_path = output_base + ".txt"

            # try utf-8 graph rendering first
            try:
                graph.render(filename=output_base, cleanup=True)
            except (UnicodeEncodeError, IOError, OSError) as e:
                # retry with ascii fallback: rebuild the graph with ascii labels using the same builder
                try:
                    ascii_graph = build_graph(tree, force_ascii_fallback=True)
                    ascii_graph.render(filename=output_base, cleanup=True)
                except Exception as e2:
                    print("Graph generation failed even after ascii fallback:", e2)
                    # continue without graph

            write_tree(tree, txt_path)

            if os.path.exists(png_path):
                self.tree_window = GraphWindow(png_path)
                self.tree_window.show()

        except Exception as e:
            print("Graph generation error:", e)

        if ai_col not in moves:
            ai_col = random.choice(moves)

        # AI places piece
        self.board_widget.board = drop_piece(self.board_widget.board, ai_col, 2)
        self.board_widget.update()

        # AI score
        _, cur_fours = count_fours(self.board_widget.board, 2)
        delta = cur_fours - self.ai_prev_fours

        if delta > 0:
            self.ai_fours += delta
            self.status_label.setText(
                f"🤖 AI connected {delta}! You: {self.player_fours} — AI: {self.ai_fours}"
            )
        else:
            self.status_label.setText(
                f"Your Turn — You: {self.player_fours} | AI: {self.ai_fours}"
            )

        self.ai_prev_fours = cur_fours

        if is_terminal(self.board_widget.board):
            self.end_game()

        self.is_player_turn = True

    def reset_game(self):
        self.board_widget.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.game_over = False

        self.player_fours = 0
        self.player_prev_fours = 0
        self.ai_fours = 0
        self.ai_prev_fours = 0

        name = self.alg_combo.currentText()
        self.status_label.setText(f"Your Turn — You: 0 | AI: 0 ({name})")
        self.board_widget.update()

    def end_game(self):
        self.game_over = True

        if self.player_fours > self.ai_fours:
            self.status_label.setText(
                f"🎉 You Win! Final Score — You: {self.player_fours}, AI: {self.ai_fours}"
            )
        elif self.ai_fours > self.player_fours:
            self.status_label.setText(
                f"AI Wins! Final Score — You: {self.player_fours}, AI: {self.ai_fours}"
            )
        else:
            self.status_label.setText(
                f"Draw! Final Score — You: {self.player_fours}, AI: {self.ai_fours}"
            )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Connect4Window()
    QTimer.singleShot(10, window.show)
    sys.exit(app.exec())
