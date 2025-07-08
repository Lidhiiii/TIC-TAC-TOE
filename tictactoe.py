import gradio as gr
from functools import partial

# === Game Logic ===
def create_board():
    return [["" for _ in range(3)] for _ in range(3)]

def check_win(board, player):
    win_cells = []
    for i in range(3):
        if all(board[i][j] == player for j in range(3)):
            win_cells = [(i, j) for j in range(3)]
            return True, win_cells
        if all(board[j][i] == player for j in range(3)):
            win_cells = [(j, i) for j in range(3)]
            return True, win_cells
    if all(board[i][i] == player for i in range(3)):
        win_cells = [(i, i) for i in range(3)]
        return True, win_cells
    if all(board[i][2 - i] == player for i in range(3)):
        win_cells = [(i, 2 - i) for i in range(3)]
        return True, win_cells
    return False, []

def check_draw(board):
    return all(cell in ["X", "O"] for row in board for cell in row)

def make_move(row, col, board, current_player, status):
    if board[row][col] != "" or "wins" in status or "draw" in status:
        return board, current_player, status, []

    board[row][col] = current_player
    win, win_cells = check_win(board, current_player)
    if win:
        status = f"🏆 Player {current_player} wins!"
    elif check_draw(board):
        status = "🤝 It's a draw!"
    else:
        current_player = "O" if current_player == "X" else "X"
        status = f"Player {current_player}'s turn"

    return board, current_player, status, win_cells

def reset_game():
    return create_board(), "X", "Player X's turn", []

# === CSS for Beautiful UI ===
custom_css = """
body {
    background-color: #ffffff !important;
    font-family: 'Segoe UI', sans-serif;
}
.gr-button {
    font-size: 28px !important;
    height: 80px !important;
    width: 80px !important;
    border-radius: 12px !important;
    border: 2px solid #ccc !important;
    background-color: #f7f7f7 !important;
    transition: 0.2s ease-in-out;
    font-weight: bold;
}
.gr-button:hover {
    background-color: #e3f2fd !important;
    border-color: #2196f3 !important;
}
.win {
    background-color: #a5d6a7 !important;
    border-color: #2e7d32 !important;
}
#status-box {
    font-size: 20px;
    font-weight: bold;
    text-align: center;
    background-color: #f0f0f0;
    border: 2px solid #ccc;
    border-radius: 10px;
    padding: 10px;
}
#title {
    font-size: 34px;
    text-align: center;
    font-weight: bold;
    color: #3f51b5;
    margin-bottom: 15px;
}
"""

# === Gradio UI ===
with gr.Blocks(css=custom_css) as demo:
    board_state = gr.State(create_board())
    current_player = gr.State("X")
    winning_cells = gr.State([])

    gr.Markdown("🎮 Tic Tac Toe", elem_id="title")
    status_text = gr.Textbox(value="Player X's turn", interactive=False, elem_id="status-box")

    buttons = [[None for _ in range(3)] for _ in range(3)]
    for i in range(3):
        with gr.Row():
            for j in range(3):
                buttons[i][j] = gr.Button("", elem_id=f"btn-{i}-{j}")

    def update_buttons(board, win_cells):
        updates = []
        for i in range(3):
            for j in range(3):
                is_win = (i, j) in win_cells
                updates.append(gr.update(value=board[i][j], elem_classes=["win"] if is_win else []))
        return updates

    for i in range(3):
        for j in range(3):
            buttons[i][j].click(
                fn=partial(make_move, i, j),
                inputs=[board_state, current_player, status_text],
                outputs=[board_state, current_player, status_text, winning_cells]
            ).then(
                fn=update_buttons,
                inputs=[board_state, winning_cells],
                outputs=[btn for row in buttons for btn in row]
            )

    reset_btn = gr.Button("🔄 Reset Game", variant="primary")
    reset_btn.click(fn=reset_game, outputs=[board_state, current_player, status_text, winning_cells])
    reset_btn.click(fn=update_buttons, inputs=[board_state, winning_cells], outputs=[btn for row in buttons for btn in row])

demo.launch()
