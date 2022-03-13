import os

from app.db.database import DataBase


class questions_db_connector:

    path = DataBase.base_path + '/install_files/questions.db'

    @staticmethod
    def create_db():
        if not os.path.exists(questions_db_connector.path):
            sql = "CREATE TABLE questions(" \
                  "QUESTION_ID INTEGER PRIMARY KEY autoincrement," \
                  "QUESTION TEXT, " \
                  "CORRECT_ANSWER NUMBER, " \
                  "KATEGORY NUMBER)"
            DataBase.make_no_response_query(sql, questions_db_connector.path)

    @staticmethod
    def insert_question(user_id, q, kat, a1, a2, a3, a4, answer):
        query = "INSERT INTO questions(USER_ID, KATEGORY, QUESTION, ANSWER1, " \
                "ANSWER2, ANSWER3, ANSWER4, CORRECT_ANSWER) " \
                "VALUES({},{},'{}','{}','{}','{}','{}',{})".format(user_id, kat, q, a1, a2, a3, a4, answer)
        DataBase.make_no_response_query(query, questions_db_connector.path)

    @staticmethod
    def get_questions():
        query = "SELECT * from questions"
        return DataBase.make_multi_response_query(query, questions_db_connector.path)

    @staticmethod
    def get_question(question_id):
        query = "SELECT * FROM questions WHERE question_id = " + str(question_id)
        return DataBase.make_multi_response_query(query, questions_db_connector.path)

    @staticmethod
    def edit_question(question_id, kat, question, a1, a2, a3, a4, answer):
        query = "UPDATE QUESTIONS SET KATEGORY = '{}', QUESTION = '{}', ANSWER1='{}', " \
                "ANSWER2='{}', ANSWER3='{}', ANSWER4='{}', " \
                "CORRECT_ANSWER={} WHERE QUESTION_ID = {}".format(kat, question, a1, a2, a3, a4, answer, question_id)
        return DataBase.make_no_response_query(query, questions_db_connector.path)
