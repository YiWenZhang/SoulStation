from flask import Blueprint, jsonify

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/test', methods=['GET'])
def test_api():
    return jsonify({
        "code": 200,
        "msg": "后端环境连接成功！(SQLite)",
        "data": None
    })