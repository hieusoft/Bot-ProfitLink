from config.connection import get_connection
from models.user_model import User
from datetime import datetime
import pytz 
tz_vn = pytz.timezone("Asia/Ho_Chi_Minh")


class UserService:
    @staticmethod
    def get_all_user():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM users"
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [User(**row) for row in rows] if rows else []

    @staticmethod
    def get_user_by_telegram_id(user_id: int):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM users WHERE user_id = %s"
        cursor.execute(sql, (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return User(**row) if row else None
    @staticmethod
    def update_verified_kol(user_id: int, verified_kol: str):
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            UPDATE users
            SET verified_kol = %s, updated_at = %s
            WHERE user_id = %s
        """
        now = datetime.now(tz_vn)
        cursor.execute(sql, (verified_kol, now, user_id))
        conn.commit()

        cursor.close()
        conn.close()
    @staticmethod
    def update_ban_status(user_id: int, banned: bool):
        conn = get_connection()
        cursor = conn.cursor()
        sql = "UPDATE users SET is_banned = %s, updated_at = NOW() WHERE user_id = %s"
        cursor.execute(sql, (1 if banned else 0, user_id))
        conn.commit()
        cursor.close()
        conn.close()
  
    @staticmethod
    async def register_user(user_id: int, username: str, language: str, verified_kol: str = "not_submitted"):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
            INSERT INTO users (user_id, username, language, verified_kol, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        now = datetime.now(tz_vn)
        cursor.execute(sql, (user_id, username, language, verified_kol, now, now))
        conn.commit()

        cursor.close()
        conn.close()

    @staticmethod
    async def register_with_referral(
        user_id: int,
        username: str,
        language: str,
        verified_kol: str = "not_submitted",
        ref_code: int = None
    ):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        referrer = None
        if ref_code:
            cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (ref_code,))
            referrer = cursor.fetchone()

        now = datetime.now(tz_vn)

        if not referrer:        
            cursor.execute("""
                INSERT INTO users (user_id, username, language, verified_kol, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, username, language or "en", verified_kol, now, now))
            conn.commit()
            cursor.close()
            conn.close()         
            return

        cursor.execute("""
            INSERT INTO users (user_id, username, language, verified_kol, ref_by, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, username, language or "en", verified_kol, ref_code, now, now))

        cursor.execute("""
            INSERT INTO affiliate_referrals (referrer_id, referred_id, created_at)
            VALUES (%s, %s, %s)
        """, (ref_code, user_id, now))

        conn.commit()
        cursor.close()
        conn.close()

    
        
    @staticmethod
    def update_language(user_id: int, language: str):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT updated_at FROM users WHERE user_id = %s", (user_id,))
        row = cursor.fetchone()
        if not row:
            cursor.close()
            conn.close()
            return

        current_updated_at = row["updated_at"]

       
        sql = """
            UPDATE users
            SET language = %s, updated_at = %s
            WHERE user_id = %s
        """
        cursor.execute(sql, (language, current_updated_at, user_id))
        conn.commit()

        cursor.close()
        conn.close()
