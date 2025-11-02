from datetime import datetime
from config.connection import get_connection
from models.subscription_model import SubscriptionDetail
import pytz 
tz_vn = pytz.timezone("Asia/Ho_Chi_Minh") 
class SubscriptionDetailService:
    @staticmethod
    def create_subscription_detail(sub_id: int, plan_id: int, payment_id: int = None,
                                   activated_at: datetime = None, expired_at: datetime = None,
                                   renewed: bool = False):
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO subscription_details (sub_id, plan_id, payment_id, activated_at, expired_at, renewed)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (sub_id, plan_id, payment_id, activated_at, expired_at, renewed))
        conn.commit()
        conn.close()

    @staticmethod
    def get_subscription_detail(sub_id: int):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT * FROM subscription_details
            WHERE sub_id = %s
        """
        cursor.execute(sql, (sub_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if rows:
            return [SubscriptionDetail(**row) for row in rows]
        return []

    @staticmethod
    def get_latest_subscription_detail(sub_id: int):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        sql = """
            SELECT sd.*, p.name AS plan_name
            FROM subscription_details sd
            JOIN subscription_plans p ON sd.plan_id = p.plan_id
            WHERE sd.sub_id = %s
            ORDER BY sd.activated_at DESC
            LIMIT 1
        """
        cursor.execute(sql, (sub_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            
            detail = SubscriptionDetail(**{k: v for k, v in row.items() if k in SubscriptionDetail.__annotations__})
            detail.plan_name = row.get("plan_name")  
            return detail

        return None

    
    @staticmethod
    def get_active_details(sub_id: int):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        now  = datetime.now(tz_vn)
        sql = """
            SELECT * FROM subscription_details
            WHERE sub_id = %s AND expired_at > %s
        """
        cursor.execute(sql, (sub_id, now))
        rows = cursor.fetchall()
        conn.close()

        return [SubscriptionDetail(**row) for row in rows]
    @staticmethod
    def get_last_active_details(sub_id: int):
       
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        now = datetime.now(tz_vn)
        sql = """
            SELECT * FROM subscription_details
            WHERE sub_id = %s AND expired_at > %s
            ORDER BY expired_at DESC
            LIMIT 1
        """
        
        cursor.execute(sql, (sub_id, now))
        row = cursor.fetchone()
        conn.close()
        return SubscriptionDetail(**row) if row else None
    @staticmethod
    def update_end_date(sub_detail_id: int, new_end_date: datetime):
        conn = get_connection()
        cursor = conn.cursor()
        sql = "UPDATE subscription_details SET expired_at = %s WHERE sub_id = %s"
        cursor.execute(sql, (new_end_date, sub_detail_id))
        conn.commit()
        cursor.close()
        conn.close()
