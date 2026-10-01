import sqlite3
from config import DB_PATH
from database.model import CREATE_USERS_TABLE, CREATE_MATCHES_TABLE


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
    is_win = winner_color == player_color
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO matches (user_id, winner, player_color, ai_color) VALUES (?, ?, ?, ?)",
            (user_id, winner_color, player_color, ai_color),
        )
        cursor.execute(
            "UPDATE users SET games_played = games_played + 1, games_won = games_won + ? WHERE id = ?",
            (int(is_win), user_id),
        )
        conn.commit()


def get_user_stats(user_id: int) -> dict | None:
    with get_connection() as conn:
        user = conn.execute(
            "SELECT id, username, games_played, games_won FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if not user:
            return None
        result = dict(user)
        played = result["games_played"]
        result["win_rate"] = round(result["games_won"] / played * 100, 1) if played else 0.0
        return result

def get_all_users() -> list[dict]:
    """Fetches all registered users with their full match statistics."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, username, games_played, games_won, created_at 
            FROM users 
            ORDER BY id DESC
            """
        )
        rows = cursor.fetchall()
        result = []
        for r in rows:
            u = dict(r)
            played = u["games_played"]
            won = u["games_won"]
            u["win_rate"] = round((won / played * 100), 1) if played > 0 else 0.0
            result.append(u)
        return result

def get_all_matches(limit=50) -> list[dict]:
    """Fetches recent match history logs across all users."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT m.id, u.username, m.winner, m.player_color, m.ai_color, m.played_at
            FROM matches m
            JOIN users u ON m.user_id = u.id
            ORDER BY m.id DESC
            LIMIT ?
            """,
            (limit,)
        )
        return [dict(r) for r in cursor.fetchall()]

def delete_user_by_id(user_id: int):
    """Admin function to remove a user and their match records."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM matches WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()