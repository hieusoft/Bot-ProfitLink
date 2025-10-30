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
    async def register_user(user):
        """Đăng ký người dùng mới bình thường (nếu chưa tồn tại)"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user.id,))
        exists = cursor.fetchone()
        if not exists:
            sql = """
                INSERT INTO users (user_id, username, language, created_at)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (user.id, user.username, user.language_code or "en", datetime.now()))
            conn.commit()

        cursor.close()
        conn.close()
        print(f"✅ User {user.id} registered normally")

    @staticmethod
    async def register_with_referral(user, ref_code: str):
       
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user.id,))
        exists = cursor.fetchone()
        if exists:
            print(f"⚠️ User {user.id} đã tồn tại, bỏ qua.")
            cursor.close()
            conn.close()
            return
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (ref_code,))
        referrer = cursor.fetchone()
        if not referrer:
            print(f"⚠️ Referrer {ref_code} không tồn tại, đăng ký bình thường.")
            cursor.execute("""
                INSERT INTO users (user_id, username, language, created_at)
                VALUES (%s, %s, %s, %s)
            """, (user.id, user.username, user.language_code or "en", datetime.now()))
            conn.commit()
            cursor.close()
            conn.close()
            return
        sql = """
            INSERT INTO users (user_id, username, language, ref_by, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (user.id, user.username, user.language_code or "en", ref_code, datetime.now()))
        cursor.execute("""
            INSERT INTO affiliate_referrals (referrer_id, referred_id, created_at)
            VALUES (%s, %s, %s)
        """, (ref_code, user.id, datetime.now()))

        conn.commit()
        cursor.close()
        conn.close()
        
        
