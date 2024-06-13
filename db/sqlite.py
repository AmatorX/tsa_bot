# import sqlite3
#
#
# class DB:
#     def __init__(self, path_to_db):
#         self.path_to_db = path_to_db
#
#     @property
#     def connection(self):
#         return sqlite3.connect(self.path_to_db)
#
#     def execute(self,
#                 command: str,
#                 parameters: tuple = None,
#                 fetchone: bool = False,
#                 fetchall: bool = False,
#                 commit: bool = False):
#         connection = self.connection
#         cursor = connection.cursor()
#         data = None
#         cursor.execute(command, parameters)
#         if commit:
#             connection.commit()
#         if fetchone:
#             data = cursor.fetchone()
#         if fetchall:
#             data = cursor.fetchall()
#
#         connection.close()
#
#         return data



