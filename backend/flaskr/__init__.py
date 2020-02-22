import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def questions_paginator(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  questions = [question.format() for question in selection]
  paginated_questions = questions[start:end]
  return paginated_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app, resources={r'/*': {'origins': '*'}})

  @app.after_request
  def set_headers(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods','GET, PATCH, POST, DELETE, OPTIONS')
    return response

  @app.route('/categories', methods=['GET'])
  def get_categories():
    all_categories = Category.query.all()
    categories = {}
    for category in all_categories:
      categories[category.id] = category.type
    result = {
      "success": True,
      "categories": categories
    }
    return jsonify(result)


  '''
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions', methods=['GET'])
  def retrieve_questions():
    selection = Question.query.all()
    questions = questions_paginator(request, selection)
    all_categories = Category.query.all()
    categories = {}
    for category in all_categories:
      categories[category.id] = category.type

    if len(questions) == 0:
      abort(404)

    return jsonify({
      "success": True,
      "questions": questions,
      "total_questions": len(selection),
      "categories": categories
    })
  '''
 
  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    try:
      question = Question.query.get(id)
      question.delete()

      return jsonify({
        'success': True,
        'deleted': id
      }), 200
    except Exception:
      abort(422)
  '''

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route('/questions', methods=['POST'])
  def post_question_and_search():

    body = request.get_json()
    if (body.get('searchTerm')):
      try:
        search_term = body.get('searchTerm','')
        selection = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
        if (len(selection) == 0):
          abort(404)

        paginated = questions_paginator(request, selection)
        return jsonify({
          'success': True,
          'questions': paginated,
          'total_questions': len(Question.query.all())
        })
      except:
        abort(404)

    else:
      new_question = body.get('question')
      new_answer = body.get('answer')
      new_difficulty = body.get('difficulty')
      new_category = body.get('category')

      if (new_question is None) or (new_answer is None) or (new_difficulty is None) or (new_category is None):
        abort(422)

      try:
        question = Question(question=new_question, answer=new_answer,difficulty=new_difficulty, category=new_category)
        question.insert()
        selection = Question.query.all()
        questions = questions_paginator(request, selection)

        return jsonify({
          'success': True,
          'created': question.id,
          'question_created': question.question,
          'questions': questions,
          'total_questions': len(selection)
        }),200

      except:
        abort(422)


  '''
  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:id>/questions')
  def get_questions_by_category(id):
    category = Category.query.filter_by(id=id).one_or_none()

    if (category is None):
      abort(422)

    selection = Question.query.filter_by(category=id).all()
    questions = questions_paginator(request, selection)

    return jsonify({
      'success': True,
      'questions': questions,
      'total_questions': len(selection),
      'current_category': category.type
    })

  '''
  @TODO: 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/quizzes', methods=['POST'])
  def get_random_quiz_question():
    body = request.get_json()

    previous = body.get('previous_questions')
    category = body.get('quiz_category')
    if (category is None) or (previous is None):
      abort(404)

    if category['id'] == 0:
      questions = Question.query.all()
    else:
      questions = Question.query.filter_by(category=category['id']).all()

    total = len(questions)
    if len(previous) == total:
      return jsonify({
        'success': True
      })

    question = questions[random.randrange(0, len(questions), 1)]
    while True:
      used=False
      for p in previous:
        if p == question.id:
          used = True
          break
      if not used:
        break
      question = questions[random.randrange(0, len(questions), 1)]

    return jsonify({
      'success': True,
      'question': question.format()
    })


  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "not found"
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "unprocessable"
    }), 422

  return app

    