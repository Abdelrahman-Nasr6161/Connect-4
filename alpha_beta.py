from functions import *
from graphviz import Digraph
import re

DEFAULT_OUTPUT_NAME = "alpha_beta_tree"

class TreeNode:
    def __init__(self, move=None, player=None, score=None, depth=0):
        self.move = move          # which column was played
        self.player = player      # 1 or 2
        self.score = score        # heuristic score at this node
        self.depth = depth        # depth in the tree
        self.children = []        # list of TreeNode
        self.alpha = None         # final alpha value at this node
        self.beta = None          # final beta value at this node
        self.pruned = False       # whether this branch was pruned

memo = {}

def board_key(board):
    """Convert board into a tuple-of-tuples for hashing."""
    return tuple(tuple(row) for row in board)


def _sanitize_label_text(s):
    """Replace problematic Unicode with ASCII fallbacks for fallback mode."""
    if s is None:
        return s
    # replace greek alpha/beta with ascii words if needed
    s = s.replace("α", "alpha").replace("β", "beta")
    # optionally remove other non-printable or control characters
    s = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", s)
    return s

def build_graphviz(node, graph=None, force_ascii_fallback=False):
    """
    Build a Digraph from the tree. If force_ascii_fallback=True, labels will
    use ascii (alpha/beta) instead of the unicode characters.
    """
    if graph is None:
        # request utf-8 encoding for Graphviz files
        try:
            graph = Digraph(format='png', encoding='utf-8')
        except TypeError:
            # older graphviz versions may not accept encoding kwarg
            graph = Digraph(format='png')

        graph.attr(rankdir="TB")  # top → bottom tree

    nid = id(node)

    # Prepare score/alpha/beta safely
    score_val = round(node.score, 3) if node.score is not None else "N/A"
    alpha_val = round(node.alpha, 3) if node.alpha is not None else "N/A"
    beta_val  = round(node.beta, 3) if node.beta is not None else "N/A"

    # Use unicode labels by default, but allow ascii fallback
    if force_ascii_fallback:
        label_parts = [
            f"Score: {score_val}",
            f"alpha: {alpha_val}",
            f"beta: {beta_val}"
        ]
    else:
        label_parts = [
            f"Score: {score_val}",
            f"α: {alpha_val}",
            f"β: {beta_val}"
        ]

    if node.move is not None:
        label_parts.append(f"Move: {node.move}")

    label = "\n".join(label_parts)

    # If fallback requested, sanitize label text
    if force_ascii_fallback:
        label = _sanitize_label_text(label)

    # Node style
    if node.pruned:
        color = "gray"
        style = "filled,dashed"
    else:
        color = "lightblue" if node.player == 2 else "lightcoral"
        style = "filled"

    # Add node; pass label directly (graphviz will handle quoting)
    graph.node(str(nid), label=label, style=style, fillcolor=color)

    for child in node.children:
        cid = id(child)
        edge_style = "dashed" if child.pruned else "solid"
        graph.edge(str(nid), str(cid), style=edge_style)
        build_graphviz(child, graph, force_ascii_fallback=force_ascii_fallback)

    return graph


def write_tree_to_file(root, filename="ab_pruning_tree.txt", force_ascii_fallback=False):
    """
    Write tree to text file using utf-8. If writing fails due to encoding,
    retry with ascii fallback (replace α/β).
    """
    def recurse(node, f, indent=0, force_ascii=False):
        prefix = "    " * indent
        pruned_marker = " [PRUNED]" if node.pruned else ""
        # Use 'is not None' checks to avoid rounding None
        alpha_str = round(node.alpha, 3) if node.alpha is not None else "N/A"
        beta_str  = round(node.beta, 3) if node.beta is not None else "N/A"
        score_str = round(node.score, 3) if node.score is not None else "N/A"

        if force_ascii:
            alpha_beta = f" | alpha={alpha_str}, beta={beta_str}"
            line = (
                f"{prefix}- Depth {node.depth} | "
                f"Player {node.player} | "
                f"Move {node.move} | "
                f"Score {score_str}"
                f"{alpha_beta}{pruned_marker}"
            )
        else:
            alpha_beta = f" | α={alpha_str}, β={beta_str}"
            line = (
                f"{prefix}- Depth {node.depth} | "
                f"Player {node.player} | "
                f"Move {node.move} | "
                f"Score {score_str}"
                f"{alpha_beta}{pruned_marker}"
            )

        # sanitize control chars
        line = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", line)
        if force_ascii:
            line = _sanitize_label_text(line)
        f.write(line + "\n")

        for child in node.children:
            recurse(child, f, indent + 1, force_ascii)

    # First try writing with utf-8 (or default if platform handles it)
    try:
        with open(filename, "w", encoding="utf-8") as f:
            recurse(root, f, indent=0, force_ascii=force_ascii_fallback)
    except Exception as e:
        # Fallback: try again using ascii-safe labels
        try:
            with open(filename, "w", encoding="utf-8", errors="replace") as f:
                recurse(root, f, indent=0, force_ascii=True)
        except Exception as e2:
            # Last resort: open with system default but sanitize text
            with open(filename, "w", encoding="ascii", errors="replace") as f:
                recurse(root, f, indent=0, force_ascii=True)

def evaluate_move(board, col, player, depth, maximizing_player, current_depth, alpha, beta):
    """Helper function to evaluate a single move and return the child node and score."""
    new_board = drop_piece(board, col, player)
    child_node, eval_score, _ = ab_pruning_with_tree(new_board, depth - 1, not maximizing_player, current_depth + 1, alpha, beta)
    child_node.move = col
    return child_node, eval_score

def update_best(eval_score, node_value, best_move, col, maximizing_player):
    """Helper function to update best score and move based on player type."""
    if maximizing_player:
        if eval_score > node_value:
            return eval_score, col
    else:
        if eval_score < node_value:
            return eval_score, col
    return node_value, best_move

def should_prune(alpha, beta):
    """Check if pruning should occur."""
    return beta <= alpha

def ab_pruning_with_tree(board, depth, maximizing_player, current_depth=0, alpha=float('-inf'), beta=float('inf')):
    valid_moves = get_moves(board)
    key = (board_key(board) , depth,maximizing_player)
    node = TreeNode(
        move=None,
        player=2 if maximizing_player else 1,
        depth=current_depth
    )
    if key in memo:
        node.score = memo[key]
        return node , node.score, None
    # Stopping condition for recursion – max specified depth or board full
    if depth == 0 or is_terminal(board):
        node.score = heurestic(board)
        node.alpha = alpha
        node.beta = beta
        return node, node.score, None

    # Initialize node value
    node_value = float('-inf') if maximizing_player else float('inf')
    best_move = None
    
    player_piece = 2 if maximizing_player else 1

    for col in valid_moves:
        child_node, eval_score = evaluate_move(board, col, player_piece, depth, maximizing_player, current_depth, alpha, beta)
        node.children.append(child_node)
        node_value, best_move = update_best(eval_score, node_value, best_move, col, maximizing_player)
        # Update alpha or beta
        if maximizing_player:
            alpha = max(alpha, eval_score)
        else:
            beta = min(beta, eval_score)
        
        # Check for pruning
        if should_prune(alpha, beta):
            # Mark remaining moves as pruned
            for remaining_col in valid_moves:
                if remaining_col > col:  # Haven't explored these yet
                    pruned_node = TreeNode(
                        move=remaining_col,
                        player=3 - player_piece,  # Opponent
                        score=None,
                        depth=current_depth + 1
                    )
                    pruned_node.pruned = True
                    pruned_node.alpha = alpha
                    pruned_node.beta = beta
                    node.children.append(pruned_node)
            break

    node.score = node_value
    node.alpha = alpha
    node.beta = beta
    return node, node_value, best_move