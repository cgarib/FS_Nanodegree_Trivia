import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'De que color era el caballo blance de Napoleon?',
            'answer': 'blanco',
            'difficulty': 1,
            'category': '4'
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_questions(self):

        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_404_questions_no_page(self):
        response = self.client().get('/questions?page=100')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'not found')

    def test_delete_question(self):
        question = Question(question=self.new_question['question'], answer=self.new_question['answer'],category=self.new_question['category'], difficulty=self.new_question['difficulty'])
        question.insert()
        id = question.id

        before = Question.query.all()

        response = self.client().delete('/questions/{}'.format(id))
        data = json.loads(response.data)

        after = Question.query.all()

        question = Question.query.filter(Question.id == 1).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], id)
        self.assertTrue(len(before) - len(after) == 1)
        self.assertEqual(question, None)

    def test_422_delete_question_fails(self):
        before = Question.query.all()
        response = self.client().delete('/questions/{}'.format(1000))
        data = json.loads(response.data)
        after = Question.query.all()

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertTrue(len(before) - len(after) == 0)

    def test_create_new_question(self):
        before = Question.query.all()
        response = self.client().post('/questions', json=self.new_question)
        data = json.loads(response.data)
        after = Question.query.all()

        question = Question.query.filter_by(id=data['created']).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(after) - len(before) == 1)
        self.assertIsNotNone(question)


    def test_search_questions(self):
        response = self.client().post('/questions',json={'searchTerm': 'autobiography'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 1)
        self.assertEqual(data['questions'][0]['id'], 5)

    def test_404_search_questions_fails(self):
        response = self.client().post('/questions',json={'searchTerm': 'gjhg'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'not found')

    def test_get_questions_category(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data['questions']), 0)
        self.assertEqual(data['current_category'], 'Science')

    def test_404_questions_category_fails(self):

        response = self.client().get('/categories/1000/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'not found')

    def test_play(self):
        response = self.client().post('/quizzes',json={'previous_questions': [20],'quiz_category': {'type': 'Science', 'id': '1'}})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['category'], 1)
        self.assertNotEqual(data['question']['id'], 20)



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()