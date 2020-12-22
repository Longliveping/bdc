from flask import jsonify, request, g, url_for, current_app
from .. import db
from ..models import Word
from . import api

@api.route('/words')
def get_words():
    page = request.args.get('page', 1, type=int)
    pagination = Word.query.paginate(page, per_page=1, error_out=False)
    words = pagination.items
    if pagination.has_next:
        next = url_for('api.get_words', page=page+1)
    return jsonify({
        'words':[word.to_json() for word in words],
        'next': next,
        'count': pagination.total
    })