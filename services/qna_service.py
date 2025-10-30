from models.qna_model import QnA_Category, QnA
from config.connection import get_connection

class QnAService:
    @staticmethod
    def get_all_active_categories():
        """Lấy tất cả danh mục QnA đang hoạt động"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        sql = "SELECT * FROM qna_category WHERE is_active = 1 ORDER BY category_name ASC"
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()

        return [QnA_Category(**row) for row in rows]

    @staticmethod
    def get_qna_by_category(category_id: int):
       
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        sql = """
            SELECT * FROM qna
            WHERE category_id = %s
            ORDER BY created_at DESC
        """
       
        cursor.execute(sql, (category_id,))
        rows = cursor.fetchall()
        conn.close()

        return [QnA(**row) for row in rows]
    @staticmethod
    def get_qna_by_id(qna_id: int):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        sql = "SELECT * FROM qna WHERE qna_id = %s"
        cursor.execute(sql, (qna_id,))
        result = cursor.fetchone()  
        
        cursor.close()
        conn.close()
        return result