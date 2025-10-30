from typing import List, Optional
from datetime import datetime
from config.connection import get_connection
from models.affiliates_model import AffiliateReferral, AffiliateWithdrawal


class AffiliateService:
    @staticmethod
    def create_referral(referrer_id: int, referred_id: int, commission_usd: float, status: str = "pending") -> int:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO affiliate_referrals (referrer_id, referred_id, commission_usd, status, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """
        now = datetime.now()
        cursor.execute(sql, (referrer_id, referred_id, commission_usd, status, now))
        referral_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return referral_id

    @staticmethod
    def get_referrals_by_user(user_id: int) -> List[AffiliateReferral]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT * FROM affiliate_referrals
            WHERE referrer_id = %s
        """
        cursor.execute(sql, (user_id,))
        rows = cursor.fetchall()
        conn.close()

        return [AffiliateReferral(**row) for row in rows]

    @staticmethod
    def create_withdrawal(user_id: int, amount: float, wallet_address: str, status: str = "pending", tx_hash: Optional[str] = None) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO affiliate_withdrawals (user_id, amount, wallet_address, status, tx_hash, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        now = datetime.now()
        cursor.execute(sql, (user_id, amount, wallet_address, status, tx_hash, now))
        withdrawal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return withdrawal_id
    @staticmethod
    def update_referral(referrer_id: int, referred_id: int, commission_usd: float, status: str):
        conn = get_connection()
        cursor = conn.cursor()

        sql = """
            UPDATE affiliate_referrals
            SET commission_usd = %s,
                status = %s
            WHERE referrer_id = %s AND referred_id = %s
        """

        cursor.execute(sql, (commission_usd, status, referrer_id, referred_id))
        conn.commit()
        conn.close()
    @staticmethod
    def get_referrals_by_referrer_pending(referrer_id: int) -> List[AffiliateReferral]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT * FROM affiliate_referrals
            WHERE referrer_id = %s AND status = 'pending'
        """
        cursor.execute(sql, (referrer_id,))
        rows = cursor.fetchall()
        conn.close()

        return [AffiliateReferral(**row) for row in rows]
    @staticmethod
    def get_referrals_by_referrer_active(referrer_id: int) -> List[AffiliateReferral]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT * FROM affiliate_referrals
            WHERE referrer_id = %s AND status = 'approved'
        """
        cursor.execute(sql, (referrer_id,))
        rows = cursor.fetchall()
        conn.close()

        return [AffiliateReferral(**row) for row in rows]
    @staticmethod
    def get_total_commission_by_user(user_id: int) -> float:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            SELECT SUM(commission_usd) FROM affiliate_referrals
            WHERE referrer_id = %s AND status = 'approved'
        """
        cursor.execute(sql, (user_id,))
        result = cursor.fetchone()
        conn.close()

        return result[0] if result[0] is not None else 0.0
    @staticmethod
    def update_withdraw_status(withdraw_id: int, status: str):
        """
        Cập nhật trạng thái rút tiền (pending → approved hoặc rejected)
        """
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            UPDATE affiliate_withdrawals
            SET status = %s
            WHERE withdraw_id = %s
        """
        now = datetime.now()
        cursor.execute(sql, (status, withdraw_id))
        conn.commit()
        conn.close()

    @staticmethod
    def reset_user_commission(user_id: int):
        """
        Reset toàn bộ hoa hồng của user sau khi rút (đưa commission_usd về 0)
        """
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            UPDATE affiliate_referrals
            SET commission_usd = 0
            WHERE referrer_id = %s
        """
        cursor.execute(sql, (user_id,))
        conn.commit()
        conn.close()
