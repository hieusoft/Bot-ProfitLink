from datetime import datetime
from config.connection import get_connection
from models.subscription_model import Subscription
import pytz 
tz_vn = pytz.timezone("Asia/Ho_Chi_Minh")

class SubscriptionService:
   
    @staticmethod
    def create_subscription(user_id: int, start_date: datetime, end_date: datetime, status: str = "active", trial: bool = False):
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO subscriptions (user_id, start_date, end_date, status, trial, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        now = datetime.now(tz_vn)
        cursor.execute(sql, (user_id, start_date, end_date, status, trial, now, now))
        conn.commit()
        conn.close()
    @staticmethod
    def get_all_subscription():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM subscriptions"
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()
        return [Subscription(**row) for row in rows] if rows else []
    @staticmethod
    def get_all_subscription_active():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM subscriptions WHERE status='active'"
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()
        return [Subscription(**row) for row in rows] if rows else []


    

    @staticmethod
    def get_active_subscription(user_id: int):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT * FROM subscriptions
            WHERE user_id = %s
            AND status = 'active'
            AND end_date > NOW()
            LIMIT 1
        """
        cursor.execute(sql, (user_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return Subscription(**row)
        return None


    @staticmethod
    def deactivate_subscription(sub_id: int):
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            UPDATE subscriptions
            SET status = 'expired'
            WHERE sub_id = %s
        """
        cursor.execute(sql, (sub_id,))
        conn.commit()
        conn.close()
    @staticmethod
    def has_used_trial(user_id: int) -> bool:
        """
        Kiểm tra user đã dùng Free Trial chưa
        :param user_id: Telegram user id
        :return: True nếu đã dùng, False nếu chưa
        """
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT 1 
            FROM subscriptions
            WHERE user_id = %s
            AND trial = TRUE
            LIMIT 1
        """
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        conn.close()
        return bool(result)
    @staticmethod
    def update_subscription(sub_id: int, start_date: datetime, end_date: datetime, status: str = "active"):
        """
        Cập nhật start_date, end_date, status và trial của subscription hiện tại
        """
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            UPDATE subscriptions
            SET start_date = %s,
                end_date = %s,
                status = %s
            WHERE sub_id = %s
        """

        cursor.execute(sql, (start_date, end_date, status, sub_id))
        conn.commit()
        conn.close()

    @staticmethod
    def update_subscription_trial(sub_id: int, start_date: datetime, end_date: datetime, status: str = "active", trial: bool = False):
        """
        Cập nhật start_date, end_date, status và trial của subscription hiện tại
        """
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            UPDATE subscriptions
            SET start_date = %s,
                end_date = %s,
                status = %s,
                trial = %s
            WHERE sub_id = %s
        """

        cursor.execute(sql, (start_date, end_date, status, trial, sub_id))
        conn.commit()
        conn.close()

    @staticmethod
    def get_subscription_by_user_id(user_id: int):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)  
        sql = """
            SELECT * FROM subscriptions
            WHERE user_id = %s
            LIMIT 1
        """
        cursor.execute(sql, (user_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return Subscription(**row) 
        return None

    @staticmethod
    def update_subscription_end(sub_id: int, end_date: datetime, status: str = "active"):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        now = datetime.now(tz_vn)

        sql = """
            UPDATE subscriptions
            SET end_date = %s, 
                status = %s,
                updated_at = %s
            WHERE sub_id = %s
        """
        cursor.execute(sql, (end_date, status, now, sub_id))
        conn.commit()
        conn.close()
    @staticmethod
    def update_end_date(sub_id: int, new_end_date: datetime):
        conn = get_connection()
        cursor = conn.cursor()
        sql = "UPDATE subscriptions SET end_date = %s WHERE sub_id = %s"
        cursor.execute(sql, (new_end_date, sub_id))
        conn.commit()
        cursor.close()
        conn.close()
