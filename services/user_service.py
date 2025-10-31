from config.connection import get_connection
from models.user_model import User
from datetime import datetime


class UserService:
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
    async def register_user(user_id: int, username: str, language: str, verified_kol: str = "not_submitted"):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        sql = """
            INSERT INTO users (user_id, username, language, verified_kol, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        now = datetime.now()
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

        now = datetime.now()

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

    
        
