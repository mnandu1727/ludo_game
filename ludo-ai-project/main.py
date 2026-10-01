import sys
import queue
import pygame
from database.db import init_db, record_match_result
from game.game_state import GameState
from game.dice import roll_dice
from game.rules import Rules
from ai.expectimax import ExpectimaxAI
from gui.login_screen import LoginScreen
from gui.home_screen import HomeScreen
from gui.game_screen import GameScreen
from gui.room_lobby_screen import RoomLobbyScreen
from gui.dice_widget import DiceWidget
from gui.animation import PawnAnimator
from gui.admin_screen import AdminScreen
from network.network_manager import LANServer, LANClient
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, LIGHT_BG

def main():
    pygame.init()
    init_db()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Ludo AI Engine")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Helvetica", 20, bold=True)

    app_state = "LOGIN"
    login_ui = LoginScreen(screen)
    admin_ui = AdminScreen(screen)
    home_ui = None
    room_ui = None
    board_ui = GameScreen(screen, board_origin=(80, 100), board_size=600)
    dice_widget = DiceWidget(x=705, y=365, size=65)
    animator = PawnAnimator(speed=0.18)
    
    game = None
    ai_bots = {}
    match_persisted = False
    
    lan_server = None
    lan_client = None
    local_player_color = None
    net_queue = queue.Queue()

    def handle_net_message(msg: dict):
        net_queue.put(msg)

    def execute_animated_move(pawn_idx: int):
        color = game.current_player
        curr_pos = game.state[color]["pawns"][pawn_idx]
        target_pos = Rules.get_next_position(curr_pos, game.last_roll)

        animator.start_animation(
            color=color,
            pawn_idx=pawn_idx,
            from_pos=curr_pos,
            to_pos=target_pos,
            board_ui=board_ui,
            on_complete=lambda: game.finalize_move(pawn_idx, target_pos)
        )

    running = True
    while running:
        clock.tick(FPS)
        dice_finished = dice_widget.update()
        animator.update()

        # Process Network Packets
        while not net_queue.empty():
            msg = net_queue.get_nowait()
            mtype = msg.get("type")
            
            if mtype == "INIT":
                if room_ui:
                    lan_client.send_action({
                        "type": "JOIN_METADATA",
                        "name": room_ui.username,
                        "color": msg.get("assigned_color"),
                        "is_host": msg.get("is_host")
                    })

            elif mtype == "LOBBY_UPDATE":
                if room_ui:
                    room_ui.slots = msg.get("slots", [])

            elif mtype == "GAME_START":
                players_in_game = msg.get("players", ["RED", "GREEN", "YELLOW", "BLUE"])
                game = GameState(custom_players=players_in_game)
                app_state = "PLAYING"

            elif mtype == "ROLL":
                val = msg.get("value")
                game.last_roll = val
                dice_widget.trigger_roll(val, duration_frames=14)

            elif mtype == "MOVE":
                p_idx = msg.get("pawn_idx")
                execute_animated_move(p_idx)

            elif mtype == "PASS_TURN":
                game.switch_turn()

        # Turn auto-pass if no legal moves
        if dice_finished and game and not animator.is_animating:
            if not game.has_any_valid_move():
                is_lan = (lan_client is not None)
                if not is_lan:
                    pygame.time.delay(350)
                    game.switch_turn()
                elif game.current_player == local_player_color:
                    pygame.time.delay(350)
                    lan_client.send_action({"type": "PASS_TURN"})

        # Login Screen
        if app_state == "LOGIN":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                res = login_ui.handle_event(event)
                if res == "HOME":
                    home_ui = HomeScreen(screen, login_ui.user_data)
                    room_ui = RoomLobbyScreen(screen, current_username=login_ui.user_data["username"])
                    app_state = "HOME"
                elif res == "GOTO_ADMIN":
                    admin_ui.reset()
                    app_state = "ADMIN"
            login_ui.render()

        elif app_state == "ADMIN":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                action = admin_ui.handle_event(event)
                if action == "EXIT_TO_LOGIN":
                    app_state = "LOGIN"
            admin_ui.render()

        # Home Menu
        elif app_state == "HOME":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                action = home_ui.handle_event(event)
                if action:
                    cmd, val = action
                    if cmd == "START_GAME":
                        if val == "LAN_MODE":
                            app_state = "ROOM_LOBBY"
                        else:
                            game = GameState(mode=val)
                            ai_bots = {c: ExpectimaxAI(color=c, depth=2) for c in game.ai_players}
                            local_player_color = None
                            match_persisted = False
                            app_state = "PLAYING"
                    elif cmd == "LOGOUT":
                        login_ui = LoginScreen(screen)
                        app_state = "LOGIN"
            home_ui.render()

        # Room Lobby Screen
        elif app_state == "ROOM_LOBBY":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                action = room_ui.handle_event(event)
                if action:
                    cmd, val = action
                    if cmd == "START_HOST":
                        lan_server = LANServer(max_clients=4)
                        try:
                            lan_server.start()
                        except OSError:
                            lan_server.stop()
                            lan_server = None
                            room_ui.sub_state = "MENU"
                            room_ui.status_msg = "Room unavailable. Try again or use another host."
                            continue
                        lan_client = LANClient(handle_net_message)
                        lan_client.connect("127.0.0.1")
                        local_player_color = "RED"
                    elif cmd == "START_JOIN":
                        lan_client = LANClient(handle_net_message)
                        if lan_client.connect(val):
                            room_ui.sub_state = "INSIDE_ROOM"
                            room_ui.status_msg = ""
                        else:
                            room_ui.status_msg = "Invalid Room Code or Host Unreachable!"
                    elif cmd == "TRIGGER_START" and lan_server:
                        active_colors = [s["color"] for s in room_ui.slots]
                        lan_server.broadcast({
                            "type": "GAME_START",
                            "players": active_colors
                        })
                    elif cmd in ["BACK_TO_HOME", "LEAVE_ROOM"]:
                        if lan_server:
                            lan_server.stop()
                            lan_server = None
                        if lan_client:
                            lan_client.disconnect()
                            lan_client = None
                        app_state = "HOME"
            room_ui.render()

        # Gameplay Screen
        elif app_state == "PLAYING":
            is_animating = animator.is_animating or dice_widget.is_rolling
            is_lan = (lan_client is not None)
            
            if is_lan and lan_client and lan_client.assigned_color:
                local_player_color = lan_client.assigned_color
                
            is_my_turn = (not is_lan) or (game.current_player == local_player_color)

            if not is_lan and game.is_current_ai and not game.winner and not is_animating:
                if game.last_roll is None:
                    r_val = roll_dice()
                    game.last_roll = r_val
                    dice_widget.trigger_roll(r_val, duration_frames=14)
                else:
                    pygame.time.delay(250)
                    if not game.has_any_valid_move():
                        game.switch_turn()
                    else:
                        best = ai_bots[game.current_player].get_best_move(game, game.last_roll)
                        if best is not None:
                            execute_animated_move(best)
                        else:
                            game.switch_turn()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if lan_server:
                        lan_server.stop()
                        lan_server = None
                    if lan_client:
                        lan_client.disconnect()
                        lan_client = None
                    if home_ui:
                        home_ui.refresh_stats()
                    app_state = "HOME"

                elif event.type == pygame.MOUSEBUTTONDOWN and not is_animating and not game.winner and is_my_turn:
                    if game.last_roll is None:
                        if dice_widget.is_clicked(event.pos):
                            r_val = roll_dice()
                            if is_lan:
                                lan_client.send_action({"type": "ROLL", "value": r_val})
                            else:
                                game.last_roll = r_val
                                dice_widget.trigger_roll(r_val, duration_frames=16)

                    elif game.last_roll is not None:
                        mx, my = event.pos
                        c_col = game.current_player
                        for idx, pos in enumerate(game.state[c_col]["pawns"]):
                            px, py = board_ui.get_pawn_pixel_pos(c_col, idx, pos)
                            if (mx - px) ** 2 + (my - py) ** 2 <= 22 ** 2:
                                if Rules.can_move(pos, game.last_roll):
                                    if is_lan:
                                        lan_client.send_action({"type": "MOVE", "pawn_idx": idx})
                                    else:
                                        execute_animated_move(idx)
                                break

            screen.fill(LIGHT_BG)
            board_ui.render(game.state, game.current_player, game.last_roll, animator)

            dice_widget.render(
                screen, 
                is_player_turn=is_my_turn, 
                can_roll=(game.last_roll is None and not is_animating)
            )

            hud_turn = f"Turn: {game.current_player}" + (f" (You: {local_player_color})" if is_lan else "")
            screen.blit(font.render(hud_turn, True, BLACK), (80, 45))
            
            if is_my_turn:
                sub = "Your Turn: Click Dice to Roll!" if game.last_roll is None else "Click an eligible pawn to move."
            else:
                sub = f"Waiting for {game.current_player}'s move..."
            screen.blit(font.render(sub, True, (90, 90, 90)), (80, 70))

            if game.winner:
                screen.blit(font.render(f"Winner: {game.winner}! Press ESC for Lobby", True, (40, 167, 69)), (80, 720))

        pygame.display.flip()

    if lan_server:
        lan_server.stop()
    if lan_client:
        lan_client.disconnect()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
