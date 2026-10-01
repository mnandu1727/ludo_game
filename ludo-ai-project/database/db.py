import sqlite3
from config import DB_PATH
from database.models import CREATE_USERS_TABLE, CREATE_MATCHES_TABLE

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CREATE_USERS_TABLE)
        cursor.execute(CREATE_MATCHES_TABLE)
        conn.commit()

def record_match_result(user_id: int, winner_color: str, player_color: str = "RED", ai_color: str = "YELLOW"):
    is_win = (winner_color == player_color)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO matches (user_id, winner, player_color, ai_color) VALUES (?, ?, ?, ?)",
            (user_id, winner_color, player_color, ai_color)
        )
        if is_win:
            cursor.execute("UPDATE users SET games_played = games_played + 1, games_won = games_won + 1 WHERE id = ?", (user_id,))
        else:
            cursor.execute("UPDATE users SET games_played = games_played + 1 WHERE id = ?", (user_id,))
        conn.commit()

def get_user_stats(user_id: int) -> dict | None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, games_played, games_won FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return None
        user_dict = dict(user)
        played = user_dict["games_played"]
        won = user_dict["games_won"]
        user_dict["win_rate"] = round((won / played * 100), 1) if played > 0 else 0.0
        return user_dict


def get_all_users() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, username, games_played, games_won, created_at FROM users ORDER BY id DESC"
        ).fetchall()
        result = []
        for row in rows:
            user = dict(row)
            played = user["games_played"]
            user["win_rate"] = round(user["games_won"] / played * 100, 1) if played else 0.0
            result.append(user)
        return result


def get_all_matches(limit: int = 50) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT m.id, u.username, m.winner, m.player_color, m.ai_color, m.played_at
               FROM matches m JOIN users u ON m.user_id = u.id
               ORDER BY m.id DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def delete_user_by_id(user_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM matches WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
