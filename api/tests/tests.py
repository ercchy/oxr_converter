# import unittest
#
# from sqlalchemy.testing import db
# from traitlets.config.tests.test_loader import TestConfig
#
#
# class ConvertDataCase(unittest.TestCase):
#     def setUp(self):
#         self.app = create_app(TestConfig)
#         self.app_context = self.app.app_context()
#         self.app_context.push()
#         db.create_all()
#
#     def tearDown(self):
#         db.session.remove()
#         db.drop_all()
#         self.app_context.pop()
#
#     def event_fired_on_saved_data(self):
#         pass