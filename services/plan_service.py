from config.connection import get_connection
from models.subscription_model import SubscriptionPlan


class PlanService:
    @staticmethod
    def get_plan_by_id(plan_id: int):
        """Lấy thông tin gói theo ID"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM subscription_plans WHERE plan_id = %s AND is_active = 1"
        cursor.execute(sql, (plan_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return SubscriptionPlan(**row)
        return None

    @staticmethod
    def get_all_active_plans():
        """Lấy danh sách tất cả gói đang hoạt động (trừ Trial)"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM subscription_plans WHERE is_active = 1 AND plan_id != 1 ORDER BY price ASC"
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()

        return [SubscriptionPlan(**r) for r in rows]


    @staticmethod
    def create_plan(name: str, price: float, duration_days: int, description: str = ""):
        """Tạo gói mới"""
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO subscription_plans (name, price, duration_days, description, is_active, created_at)
            VALUES (%s, %s, %s, %s, 1, NOW())
        """
        cursor.execute(sql, (name, price, duration_days, description))
        conn.commit()
        conn.close()

    @staticmethod
    def deactivate_plan(plan_id: int):
        """Vô hiệu hóa gói"""
        conn = get_connection()
        cursor = conn.cursor()
        sql = "UPDATE subscription_plans SET is_active = 0 WHERE plan_id = %s"
        cursor.execute(sql, (plan_id,))
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_plan_by_name(name: str):
       
        try:
            with get_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    sql = "SELECT * FROM subscription_plans WHERE name = %s AND is_active = 1"
                    cursor.execute(sql, (name,))
                    row = cursor.fetchone()
                    if row:
                        return SubscriptionPlan(**row)
        except Exception as e:
            print("DB Error:", e)
        return None
