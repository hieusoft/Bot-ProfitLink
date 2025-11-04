from datetime import datetime
from config.connection import get_connection
from models.payment_model import Payment
import pytz 
tz_vn = pytz.timezone("Asia/Ho_Chi_Minh")

class PaymentService:

    @staticmethod
    def create_payment(payment: Payment) -> int:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            sql = """
            INSERT INTO payments
            (user_id, plan_id, order_id, amount, currency, method, status, merchant_id, track_id, expired_at, invoice_date, completed_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                payment.user_id,
                payment.plan_id,
                payment.order_id,
                payment.amount,
                payment.currency,
                payment.method,
                payment.status,
                payment.merchant_id,
                payment.track_id,
                payment.expired_at,
                payment.invoice_date,
                payment.completed_at
            ))
            payment_id = cursor.lastrowid
            cursor.close()
            return payment_id
        finally:
            conn.close()

    @staticmethod
    def get_payment_by_track(track_id: str) -> Payment | None:
    
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT * FROM payments WHERE track_id=%s"
            cursor.execute(sql, (track_id,))
            row = cursor.fetchone()
            cursor.close()
            if row:
                return Payment(**row)
            return None
        finally:
            conn.close()

    @staticmethod
    def update_payment_status(track_id: str, status: str, completed_at: datetime = None) -> bool:
       
        conn = get_connection()
        try:
            cursor = conn.cursor()
            sql = "UPDATE payments SET status=%s, completed_at=%s, updated_at=NOW() WHERE track_id=%s"
            cursor.execute(sql, (status, completed_at, track_id))
            conn.commit()
            rowcount = cursor.rowcount
            cursor.close()
            return rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def get_latest_payment(user_id: int, plan_id: int) -> Payment | None:
        """Lấy payment mới nhất của user cho 1 plan cụ thể (KHÔNG chứa 'RENEW' trong order_id)"""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT * 
                FROM payments 
                WHERE user_id = %s 
                AND plan_id = %s 
                AND (order_id NOT LIKE %s OR order_id IS NULL)
                ORDER BY created_at DESC
                LIMIT 1
            """
            cursor.execute(sql, (user_id, plan_id, '%RENEW%'))
            row = cursor.fetchone()
            cursor.close()
            if row:
                return Payment(**row)
            return None
        finally:
            conn.close()

    @staticmethod
    def get_latest_payment_renew(user_id: int, plan_id: int) -> Payment | None:
        """Lấy payment mới nhất của user cho 1 plan cụ thể (chỉ lấy các order có 'RENEW' trong order_id)"""
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT * 
                FROM payments 
                WHERE user_id = %s 
                AND plan_id = %s 
                AND order_id LIKE %s
                AND status = 'pending'
                ORDER BY created_at DESC
                LIMIT 1
            """
            cursor.execute(sql, (user_id, plan_id, '%RENEW%'))
            row = cursor.fetchone()
            cursor.close()
            if row:
                return Payment(**row)
            return None
        finally:
            conn.close()

    @staticmethod
    def get_user_payments(user_id: int) -> list[Payment]:
       
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT * FROM payments WHERE user_id=%s ORDER BY created_at DESC"
            cursor.execute(sql, (user_id,))
            rows = cursor.fetchall()
            cursor.close()
            return [Payment(**row) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def get_latest_payment_pending(user_id: int, plan_id: int) -> Payment | None:
        """
        Lấy payment gần nhất của user cho plan cụ thể mà đang ở trạng thái 'pending'
        """
        conn = get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT * 
                FROM payments 
                WHERE user_id = %s AND plan_id = %s AND status = 'pending' AND (order_id NOT LIKE %s OR order_id IS NULL)
                ORDER BY created_at DESC
                LIMIT 1
            """
            cursor.execute(sql, (user_id, plan_id, '%RENEW%'))
            row = cursor.fetchone()
            cursor.close()

            if row:
                
                if 'status' not in row or row['status'] is None:
                    row['status'] = "pending"
                return Payment(**row)
            return None
        finally:
            conn.close()
