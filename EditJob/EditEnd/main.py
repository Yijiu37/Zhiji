from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql # 连接数据库
import erniebot #文心一言调用
import os  # 用于目录操作
import traceback # 反馈错误
from paddleocr import PaddleOCR # OCR功能
from datetime import datetime
from paddlespeech.cli.asr.infer import ASRExecutor
import random
asr = ASRExecutor()

app = Flask(__name__) # 初始化Flask应用并加载配置
app.config['UPLOAD_FOLDER'] = './uploads'
CORS(app, resources={r'/*': {'origins': '*'}})

erniebot.api_type = 'aistudio'

app = Flask(__name__) # 初始化Flask应用并加载配置
app.config['UPLOAD_FOLDER'] = './uploads'
CORS(app, resources={r'/*': {'origins': '*'}})

erniebot.api_type = 'aistudio'
def get_db_connection(): #连接数据库
    connection = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='root',
        db='notes_db',
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection


@app.route('/register', methods=["POST"])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    password_hash = generate_password_hash(password)
    connection = get_db_connection()
    with connection.cursor() as cursor:
        sql = "INSERT INTO users (username, password_hash) VALUES (%s, %s)"
        cursor.execute(sql, (username, password_hash))

        user_id = cursor.lastrowid  # 获取新插入用户的ID
        # 用户一旦注册，就插入名为“共享”的文件夹
        sql = "INSERT INTO folders (user_id, folder_name) VALUES (%s, %s)"
        cursor.execute(sql, (user_id, '共享'))

    connection.commit()
    connection.close()
    return jsonify({'message': '注册成功！'})

# 登录
@app.route('/login', methods=["POST"])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    connection = get_db_connection()
    with connection.cursor() as cursor:
        sql = "SELECT id, password_hash FROM users WHERE username = %s"
        cursor.execute(sql, (username,))
        user = cursor.fetchone()
    connection.close()
    if user and check_password_hash(user['password_hash'], password):
        return jsonify({'message': '登录成功！', 'user_id': user['id']})
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

# 注销账户
@app.route('/delete-user', methods=['DELETE'])
def delete_user():
    connection = get_db_connection()
    try:
        user_id = request.json.get('userid')
        if not user_id:
            return jsonify({'error': '缺少用户ID'}), 400
        with connection.cursor() as cursor:
            # 删除用户记录
            sql = "DELETE FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            connection.commit()

        return jsonify({'message': '用户已成功注销'}), 200
    except Exception as e:
        print('Error:', e)
        return jsonify({'error': '注销账户时发生错误'}), 500
    finally:
        connection.close()

# 新建文件夹
@app.route('/create-folder', methods=['POST'])
def create_folder():
    data = request.get_json()
    user_id = data.get('user_id')
    folder_name = data.get('folder_name')

    if not user_id or not folder_name:
        return jsonify({'error': '缺少用户ID或文件夹名称'}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO folders (user_id, folder_name) VALUES (%s, %s)"
            cursor.execute(sql, (user_id, folder_name))
            connection.commit()
            folder_id = cursor.lastrowid
    finally:
        connection.close()

    return jsonify({'message': '文件夹创建成功', 'folder_id': folder_id})

# 新建笔记的保存逻辑
@app.route('/save-note', methods=["POST"])
def save_note():
    data = request.get_json()
    user_id = data.get('user_id')
    document_name = data.get('document_name')
    note_cover_url = data.get('note_cover_url')
    note_content = data.get('content')
    saved_time = data.get('saved_time')
    folder_id = data.get('folder_id')  # 新增字段

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 查询当前 notes 表中最大的 id 值
            cursor.execute("SELECT MAX(id) FROM notes")
            result = cursor.fetchone()
            max_id = result['MAX(id)'] if result['MAX(id)'] is not None else 0
            note_id = max_id + 1

            # 执行插入操作
            sql = """
                INSERT INTO notes (id, user_id, document_name, content, note_cover_url, saved_time, folder_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (note_id, user_id, document_name, note_content, note_cover_url, saved_time, folder_id))
    except pymysql.Error as e:
        print(f"Error saving/updating note: {str(e)}")
        return jsonify({'message': '新建笔记时出错', 'error': str(e)}), 500
    finally:
        connection.commit()
        connection.close()

    return jsonify({'message': '保存笔记成功！', 'note_id': note_id})

# 编辑笔记内容的保存逻辑
@app.route('/update-note', methods=["POST"])
def update_note():
    data = request.get_json()
    document_name = data['document_name']
    saved_time = data['saved_time']
    note_id = data['note_id']
    content = data['content']

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 执行编辑的保存操作
            sql = """
                    UPDATE notes 
                    SET document_name = %s, content = %s, saved_time = %s
                    WHERE id = %s
                    """
            cursor.execute(sql, (document_name, content, saved_time, note_id))
    except pymysql.Error as e:
        print(f"Error saving/updating note: {str(e)}")
        return jsonify({'message': '新建笔记时出错', 'error': str(e)}), 500
    finally:
        connection.commit()
        connection.close()

    return jsonify({'message': '笔记保存成功！'})

# 删除笔记
@app.route('/delete-note', methods=["POST"])
def delete_note():
    data = request.get_json()
    note_id = data.get('note_id')
    user_id = data.get('user_id')  # 从请求中获取用户ID

    if not note_id or not user_id:
        return jsonify({'message': '未提供笔记ID或用户ID'}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 执行删除操作
            sql = "DELETE FROM notes WHERE id = %s AND user_id = %s"
            cursor.execute(sql, (note_id, user_id))
            if cursor.rowcount == 0:
                return jsonify({'message': '未找到该笔记或无权限删除该笔记'}), 404
    except pymysql.Error as e:
        print(f"Error deleting note: {str(e)}")
        return jsonify({'message': '删除笔记时出错', 'error': str(e)}), 500
    finally:
        connection.commit()
        connection.close()

    return jsonify({'message': '笔记删除成功'})

# 置顶笔记
@app.route('/top-note', methods=["POST"])
def top_note():
    data = request.get_json()
    note_id = data.get('note_id')

    if not note_id:
        return jsonify({'message': '未提供笔记ID'}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 将指定的笔记 is_top 设为 1
            cursor.execute("UPDATE notes SET is_top = 1 WHERE id = %s", (note_id,))
    except pymysql.Error as e:
        print(f"Error topping note: {str(e)}")
        return jsonify({'message': '置顶笔记时出错', 'error': str(e)}), 500
    finally:
        connection.commit()
        connection.close()

    return jsonify({'message': '笔记置顶成功'})

# 取消置顶
@app.route('/untop-note', methods=["POST"])
def untop_note():
    data = request.get_json()
    note_id = data.get('note_id')

    if not note_id:
        return jsonify({'message': '未提供笔记ID'}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 将指定的笔记 is_top 设为 0
            cursor.execute("UPDATE notes SET is_top = 0 WHERE id = %s", (note_id,))
    except pymysql.Error as e:
        print(f"Error un-topping note: {str(e)}")
        return jsonify({'message': '取消置顶时出错', 'error': str(e)}), 500
    finally:
        connection.commit()
        connection.close()

    return jsonify({'message': '笔记取消置顶成功'})

# 删除文件夹
@app.route('/delete-folder', methods=['POST'])
def delete_folder():
    data = request.get_json()
    folder_id = data.get('folder_id')

    if not folder_id:
        return jsonify({'message': '未提供文件夹ID'}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 删除文件夹中的笔记
            sql_delete_notes = "DELETE FROM notes WHERE folder_id = %s"
            cursor.execute(sql_delete_notes, (folder_id,))
            # 删除文件夹
            sql_delete_folder = "DELETE FROM folders WHERE id = %s"
            cursor.execute(sql_delete_folder, (folder_id,))
    except pymysql.Error as e:
        print(f"Error deleting folder: {str(e)}")
        return jsonify({'message': '删除文件夹时出错', 'error': str(e)}), 500
    finally:
        connection.commit()
        connection.close()

    return jsonify({'message': '文件夹删除成功'})

# 更新文件夹信息
@app.route('/update-folder', methods=['POST'])
def update_folder():
    data = request.get_json()
    folder_id = data.get('folder_id')
    folder_name = data.get('folder_name')

    if not folder_id or not folder_name:
        return jsonify({'message': '未提供文件夹ID或文件夹名称'}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql_update_folder = "UPDATE folders SET folder_name = %s WHERE id = %s"
            cursor.execute(sql_update_folder, (folder_name, folder_id))
    except pymysql.Error as e:
        print(f"Error updating folder: {str(e)}")
        return jsonify({'message': '更新文件夹信息时出错', 'error': str(e)}), 500
    finally:
        connection.commit()
        connection.close()

    return jsonify({'message': '文件夹信息更新成功'})



# 加载登录进来用户的笔记信息（包括文件夹）
@app.route('/load-notes/<user_id>', methods=["GET"])
def load_notes(user_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 获取文件夹信息
            sql_folders = "SELECT * FROM folders WHERE user_id = %s"
            cursor.execute(sql_folders, (user_id,))
            folders = cursor.fetchall()

            # 获取笔记信息
            sql_notes = "SELECT * FROM notes WHERE user_id = %s"
            cursor.execute(sql_notes, (user_id,))
            notes = cursor.fetchall()

            # 将笔记按文件夹归类
            for folder in folders:
                folder['notes'] = [note for note in notes if note['folder_id'] == folder['id']]
    finally:
        connection.close()

    return jsonify({'folders': folders})

# 加载点击的笔记信息
@app.route('/load-detailnotes/<note_id>', methods=["GET"])
def load_detailnotes(note_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM notes WHERE id = %s"
            cursor.execute(sql, (note_id,))
            notes = cursor.fetchall()
    finally:
        connection.close()

    return jsonify(notes)

# 润色
@app.route('/getpolish', methods=["GET", "POST"])
def getpolish():
    print("成功进入润色")
    # 获取用户名
    username= request.form.get("username")
    # 获取用户的访问令牌
    key = request.form.get("key")
    # 获取用户提问内容
    quescont = request.form.get("cont")
    askcont = "帮我润色下面这段话:{}".format(quescont or "")

    erniebot.access_token = key
    try:
        response = erniebot.ChatCompletion.create(
            model='ernie-bot',
            messages=[{'role': 'user', 'content':askcont}],
        )
        restext = response['result']
        webdict = {'answer': restext}
        return jsonify(webdict)
    except:
        return "error"

# 续写
@app.route('/getcontinuation', methods=["GET", "POST"])
def getcontinuation():
    # 获取用户名
    username= request.form.get("username")
    # 获取用户的访问令牌
    key = request.form.get("key")
    # 获取用户提问内容
    quescont = request.form.get("cont")
    askcont = "帮我续写下面这段话:{}".format(quescont or "")

    erniebot.access_token = key
    try:
        response = erniebot.ChatCompletion.create(
            model='ernie-bot',
            messages=[{'role': 'user', 'content':askcont}],
        )
        restext = response['result']
        webdict = {'answer': restext}
        return jsonify(webdict)
    except:
        return "error"

@app.route('/getabstract', methods=["GET", "POST"])
def getabstract():
    # 获取用户名
    username= request.form.get("username")
    # 获取用户的访问令牌
    key = request.form.get("key")
    # 获取用户提问内容
    quescont = request.form.get("cont")
    askcont = "帮我给下面这段话写摘要:{}".format(quescont or "")

    erniebot.access_token = key
    try:
        response = erniebot.ChatCompletion.create(
            model='ernie-bot',
            messages=[{'role': 'user', 'content':askcont}],
        )
        restext = response['result']
        webdict = {'answer': restext}
        return jsonify(webdict)
    except:
        return "error"

@app.route('/gettranslate', methods=["GET", "POST"])
def gettranslate():
    # 获取用户的访问令牌
    key = request.form.get("key")
    # 获取用户提问内容
    quescont = request.form.get("cont")
    askcont = "帮我翻译这段话，如果这段话是中文请翻译成英语，如果这段话不是中文请翻译成中文:{}".format(quescont or "")

    erniebot.access_token = key
    try:
        response = erniebot.ChatCompletion.create(
            model='ernie-bot',
            messages=[{'role': 'user', 'content': askcont}],
        )
        restext = response['result']
        webdict = {'answer': restext}
        return jsonify(webdict)
    except:
        return "error"

# 上传图片
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    uploads_dir = app.config['UPLOAD_FOLDER']
    os.makedirs(uploads_dir, exist_ok=True)  # 确保目录存在

    file_path = os.path.join(uploads_dir, file.filename)
    file.save(file_path)
    return jsonify({'message': '上传成功！', 'filename': file.filename}), 200

# 提供上传目录中的文件
@app.route('/uploads/<filename>', methods=['GET'])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 更新收藏状态的路由
@app.route('/update-favorite', methods=['POST'])
def update_favorite():
    data = request.get_json()
    note_id = data['note_id'] #传入该笔记的id
    is_favorite = data['is_favorite'] #最新收藏状态
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE notes SET is_favorite = %s WHERE id = %s"
            cursor.execute(sql, (is_favorite, note_id))
        connection.commit()
    except pymysql.Error as e:
        print(f"Error updating favorite status: {str(e)}")
        return jsonify({'message': '更新收藏状态时出错', 'error': str(e)}), 500
    finally:
        connection.close()

    return jsonify({'message': '收藏状态更新成功'})

# 加载登录进来用户的所有信息
@app.route('/load-userInfo', methods=["GET"])
def load_userInfo():
    user_id = request.args.get('userid')  # 获取查询参数中的userId
    print("加载用户信息:")
    print(user_id)
    if not user_id:
        return jsonify({'error': '未提供用户ID'}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            user = cursor.fetchall()
    except Exception as e:
        traceback.print_exc()  # 打印完整的错误堆栈信息
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

    if not user:
        return jsonify({'error': '未找到用户数据'}), 404

    return jsonify(user), 200

# 获取共享当前笔记的所有用户id
@app.route('/get-shared-users/<note_id>', methods=['GET'])
def get_shared_users(note_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 获取共享的用户ID
            sql = "SELECT user_id FROM notes WHERE id = %s"
            cursor.execute(sql, (note_id,))
            shared_users_ids = cursor.fetchall()

            # 根据用户ID获取用户名
            user_ids = [user['user_id'] for user in shared_users_ids]

            if not user_ids:
                return jsonify([]), 200

            format_strings = ','.join(['%s'] * len(user_ids))
            sql = f"SELECT id, username FROM users WHERE id IN ({format_strings})"
            cursor.execute(sql, tuple(user_ids))
            shared_users = cursor.fetchall()
    finally:
        connection.close()

    return jsonify(shared_users), 200

# 把分享用户信息加入数据库
@app.route('/add-user', methods=['POST'])
def add_user():
    data = request.get_json()
    note_id = data['note_id']
    new_user_id = data['new_user_id']
    current_user_id = data['current_user_id']  # 当前页面的用户ID

    print(new_user_id, current_user_id, note_id)

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 检查是否已存在相同的记录
            check_sql = """
                    SELECT * FROM message
                    WHERE from_user_id = %s AND to_user_id = %s AND note_id = %s
                """
            cursor.execute(check_sql, (current_user_id, new_user_id, note_id))
            result = cursor.fetchone()
            if result:
                return jsonify({'message': '已经邀请过此用户，请稍作等待'}), 400

            # 在message表中添加新行
            insert_sql = """
                    INSERT INTO message (from_user_id, to_user_id, note_id)
                    VALUES (%s, %s, %s)
                """
            cursor.execute(insert_sql, (current_user_id, new_user_id, note_id))
    except pymysql.Error as e:
        print(f"Error adding user: {str(e)}")
        return jsonify({'message': '添加新用户时出错', 'error': str(e)}), 500
    finally:
        connection.commit()
        connection.close()

    return jsonify({'message': '已经成功发送邀请'})

# 修改用户信息
@app.route('/updateProfile', methods=["POST"])
def update_profile():
    user_id = request.form.get('id')
    username = request.form.get('username')
    password = request.form.get('password')
    password_hash = generate_password_hash(password) #转为哈希
    avatar = request.files.get('avatar')

    if not all([user_id, username, password]):
        return jsonify({'error': '缺少必要的字段'}), 400

    avatar_url = None
    if avatar:
        uploads_dir = os.path.join(app.config['UPLOAD_FOLDER']) #上传路径
        os.makedirs(uploads_dir, exist_ok=True)  # 确保目录存在

        avatar_filename = f"{user_id}_{avatar.filename}"
        avatar_path = os.path.join(uploads_dir, avatar_filename)
        avatar.save(avatar_path)

        avatar_url = f"http://127.0.0.1:5000/uploads/{avatar_filename}"

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                UPDATE users
                SET username = %s, password_hash = %s, avatar_url = %s
                WHERE id = %s
            """
            cursor.execute(sql, (username, password_hash, avatar_url, user_id))
            connection.commit()
    except Exception as e:
        traceback.print_exc()  # 打印完整的错误堆栈信息
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

    return jsonify({'message': '更新成功', 'avatar_url': avatar_url}), 200


def ocr_recognition(image_path, det_model_path, rec_model_path, cls_model_path):
    """
    :param image_path: 待识别的图像路径
    :param det_model_path: 检测模型路径
    :param rec_model_path: 识别模型路径
    :param cls_model_path: 分类模型路径
    :return: 识别的文本结果
    """
    # 初始化PaddleOCR
    ocr = PaddleOCR(
        use_angle_cls=True,
        lang="ch",
        det_model_dir=det_model_path,
        rec_model_dir=rec_model_path,
        cls_model_dir=cls_model_path
    )

    try:
        # 进行OCR识别
        result = ocr.ocr(image_path, cls=True)
        recognized_text = []
        for idx in range(len(result)):
            res = result[idx]
            for line in res:
                recognized_text.append(line[1][0])

        # 输出识别的文本结果
        return recognized_text

    except Exception as e:
        print(f"OCR操作时出错: {e}")
        return None

@app.route('/ocr', methods=['POST'])
def ocr():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    uploads_dir = app.config['UPLOAD_FOLDER']
    os.makedirs(uploads_dir, exist_ok=True)  # 确保目录存在

    file_path = os.path.join(uploads_dir, file.filename)
    file.save(file_path)

    # 设置PaddleOCR模型路径  （存在main.py相同路径下）
    det_model_path = 'D:\\.paddleocr\\whl\\det\\ch\\ch_PP-OCRv4_det_infer'
    rec_model_path = 'D:\\.paddleocr\\whl\\rec\\ch\\ch_PP-OCRv4_rec_infer'
    cls_model_path = 'D:\\.paddleocr\\whl\\cls\\ch_ppocr_mobile_v2.0_cls_infer'

    # 调用OCR识别函数
    recognized_text = ocr_recognition(file_path, det_model_path, rec_model_path, cls_model_path)
    if recognized_text is not None:
        return jsonify({'message': 'OCR识别成功', 'recognized_text': recognized_text}), 200
    else:
        return jsonify({'message': 'OCR识别失败'}), 500

@app.route('/completeAI', methods=["GET", "POST"])
def completeAI():
    # 获取用户的访问令牌
    key = request.form.get("key")
    # 获取用户提问内容
    quescont = request.form.get("cont")
    askcont = "这是一篇文章，请你对这篇文章的全文进行校正（如果内容是中文文章则校正中文语句语法，如果是其他语言则校正对应语言的语句语法），保持文章的段落结构（以html形式来显示），直接给出校正后的结果，不准回答别的语句:{}".format(quescont or "")

    erniebot.access_token = key
    try:
        response = erniebot.ChatCompletion.create(
            model='ernie-bot',
            messages=[{'role': 'user', 'content': askcont}],
        )
        restext = response['result']
        webdict = {'answer': restext}
        return jsonify(webdict)
    except:
        return "error"

@app.route('/messages/<int:user_id>', methods=['GET'])
def get_messages(user_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT DISTINCT m.unique_id, m.note_id, u.username, n.document_name, m.from_user_id, m.to_user_id
                FROM message m
                JOIN users u ON m.from_user_id = u.id
                JOIN notes n ON m.note_id = n.id
                WHERE m.to_user_id = %s
            """
            cursor.execute(sql, (user_id,))
            messages = cursor.fetchall()
    except pymysql.Error as e:
        print(f"Error fetching messages: {str(e)}")
        return jsonify({'message': '获取消息时出错', 'error': str(e)}), 500
    finally:
        connection.close()

    return jsonify(messages)


@app.route('/accept-invitation', methods=['POST'])
def accept_invitation():
    data = request.get_json()
    note_id = data['note_id']
    new_user_id = data['new_user_id']
    current_user_id = data['current_user_id']

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 获取新用户的“共享”文件夹ID
            sql_get_folder_id = """
                SELECT id
                FROM folders
                WHERE user_id = %s AND folder_name = '共享'
            """
            cursor.execute(sql_get_folder_id, (new_user_id,))
            shared_folder = cursor.fetchone()

            if shared_folder and isinstance(shared_folder, dict) and 'id' in shared_folder:
                shared_folder_id = shared_folder['id'] #获取被分享用户的共享文件夹id
            else:
                raise Exception("共享文件夹未找到")

            # 插入新用户到 notes 表中
            sql = """
                INSERT INTO notes (id, user_id, document_name, content, saved_time, 
                is_favorite, note_cover_url, is_top, folder_id)
                  SELECT id, %s, document_name, content, saved_time, false, note_cover_url, is_top, %s
                  FROM notes
                  WHERE user_id = %s AND id = %s
            """
            cursor.execute(sql, (new_user_id, shared_folder_id, current_user_id, note_id))

            # 删除 message 表中的记录
            delete_sql = "DELETE FROM message WHERE note_id = %s AND to_user_id = %s"
            cursor.execute(delete_sql, (note_id, new_user_id))
    except pymysql.Error as e:
        print(f"Error accepting invitation: {str(e)}")
        return jsonify({'message': '接受邀请时出错', 'error': str(e)}), 500
    finally:
        connection.commit()
        connection.close()

    return jsonify({'message': '邀请接受成功'})


@app.route('/reject-invitation', methods=['POST'])
def reject_invitation():
    data = request.get_json()
    note_id = data['note_id']
    to_user_id = data['to_user_id']
    from_user_id = data['from_user_id']

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 删除 message 表中的记录
            sql = "DELETE FROM message WHERE note_id = %s AND to_user_id = %s AND from_user_id = %s"
            cursor.execute(sql, (note_id, to_user_id, from_user_id))
    except pymysql.Error as e:
        print(f"Error rejecting invitation: {str(e)}")
        return jsonify({'message': '拒绝邀请时出错', 'error': str(e)}), 500
    finally:
        connection.commit()
        connection.close()

    return jsonify({'message': '邀请拒绝成功'})

@app.route('/voiceToText', methods=['POST'])
def process_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not file.filename.endswith('.wav'):
        return jsonify({'error': 'Invalid file format'}), 400

    # Save the file
    uploads_dir = app.config['UPLOAD_FOLDER']
    os.makedirs(uploads_dir, exist_ok=True)  # Ensure directory exists
    file_path = os.path.join(uploads_dir, file.filename)
    file.save(file_path)

    result = asr(audio_file=file_path)

    # Return the result as JSON
    return jsonify({'transcribed_text': result})

def generate_random_filename():
    return f"{random.randint(0, 99999999)}.jpg"

@app.route('/tongji', methods=['POST'])
def tongji():
    # 获取用户的访问令牌
    key = request.form.get("key")
    # 获取用户内容
    quescont = request.form.get("cont")
    filename = generate_random_filename()

    upload_dir = './uploads'
    os.makedirs(upload_dir, exist_ok=True)  # 确保目录存在
    file_path = os.path.join(upload_dir, filename)

    erniebot.api_type = 'aistudio'


    askcont = ("不准回答别的语句,根据下面的数据提供能够让python绘制可视化图像的代码，只要代码，不要任何文字"
               "：{}：要求最后得到的图片不要显示出来，保存到{}之中，标签要能够用中文显示"
               "直接给出python的代码结果，不准回答别的语句").format(quescont, file_path)

    erniebot.access_token = key

    try:
        response = erniebot.ChatCompletion.create(
            model='ernie-bot',
            messages=[{'role': 'user', 'content': askcont}],
        )
        restext = response['result']
        clean_code = restext.strip('```python').strip('```')


        exec(clean_code)

        return jsonify({'message': '可视化生成成功！', 'filename': filename}), 200
    except :
        return "error"

@app.route('/biaoge', methods=['POST'])
def biaoge():
    # 获取用户的访问令牌
    key = request.form.get("key")
    # 获取用户内容
    quescont = request.form.get("cont")

    erniebot.api_type = 'aistudio'

    askcont = ("不准回答别的语句,根据下面的数据提供html表格代码，只要代码，不要任何文字"
               "：{},表格的行列不要多，不要有多余的行与列,开头不要有ml,不需要<thead>，<table>之后直接<tbody>"
               "只需要给出表格部分的html代码，别的都不需要，不准回答别的语句").format(quescont)

    erniebot.access_token = key

    try:
        response = erniebot.ChatCompletion.create(
            model='ernie-bot',
            messages=[{'role': 'user', 'content': askcont}],
        )
        restext = response['result']
        clean_code = restext.strip('```python').strip('```').strip('ml\n')

        print(clean_code)


        return jsonify({'message': '表格生成成功！', 'table' : clean_code}), 200
    except :
        return "error"

@app.route('/showliterature', methods=['POST'])
def showliterature():
    # 获取用户的访问令牌
    key = request.form.get("key")
    # 获取用户内容
    quescont = request.form.get("cont")

    erniebot.api_type = 'aistudio'

    askcont = ("不准回答别的语句，不许有除了数组的任何内容"
               "根据下面的文章内容，提供与文章内容相关的文献资料与学术论文，以{{ text: '', url: '' }},{{ text: '', url: '' }}这种格式给出"
               "文章内容：{}"
               "不准回答别的语句，url要是可访问的，最后返回的只要有数组格式的数据，不要有多余的话，不准回答别的语句").format(quescont)

    erniebot.access_token = key
    try:
        response = erniebot.ChatCompletion.create(
            model='ernie-bot',
            messages=[{'role': 'user', 'content': askcont}],
        )
        restext = response['result']
        clean_code = restext.strip('```json\n').strip('```').strip(' ')


        return jsonify({'message': '资料获取成功！', 'literature' : clean_code}), 200
    except :
        return "error"

# 加载模板
@app.route('/templates', methods=['GET'])
def get_templates():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM templates")
            templates = cursor.fetchall()
        connection.commit()
    finally:
        connection.close()
    return jsonify({'templates': templates})

#加载用户自身的模板
@app.route('/user_templates', methods=['GET'])
def get_user_templates():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'Missing user_id parameter'}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM userOwn_templates WHERE user_id = %s"
            cursor.execute(sql, (user_id,))
            templates = cursor.fetchall()
        return jsonify({'templates': templates}), 200
    except Exception as e:
        print(f"Error loading user templates: {e}")
        return jsonify({'error': 'Failed to load user templates'}), 500
    finally:
        connection.close()


# 保存用户自己的模板
# 保存用户自己的模板
@app.route('/save_template', methods=['POST'])
def save_template():
    data = request.get_json()
    user_id = data.get('user_id')
    name = data.get('name')
    content = data.get('content')
    cover_url = data.get('cover_url')

    if not user_id or not name or not content or not cover_url:
        return jsonify({'error': 'Missing data'}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO userOwn_templates (user_id, name, content, cover_url) VALUES (%s, %s, %s, %s)"
            params = (user_id, name, content, cover_url)
            cursor.execute(sql, params)
        connection.commit()
        return jsonify({'message': 'Template saved successfully'}), 200
    except Exception as e:
        print(f"Error saving template: {e}")
        traceback.print_exc()  # 打印完整的错误堆栈信息
        return jsonify({'error': 'Failed to save template'}), 500
    finally:
        connection.close()

# 根据note_id加载笔记信息
@app.route('/load-noteInfo', methods=["GET"])
def load_noteInfo():
    note_id = request.args.get('note_id')  # 获取查询参数中的userId
    if not note_id:
        return jsonify({'error': '未提供笔记ID'}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM notes WHERE id = %s"
            cursor.execute(sql, (note_id,))
            note = cursor.fetchall()
    except Exception as e:
        traceback.print_exc()  # 打印完整的错误堆栈信息
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

    if not note:
        return jsonify({'error': '未找到笔记数据'}), 404

    return jsonify(note), 200


if __name__ == '__main__':
    #app.run(host="127.0.0.1", port=5000, debug=True)
    #应用在本地运行，开启调试模式
    # 局域网测试使用 0.0.0.0 并指定一个端口
    app.run(host="0.0.0.0", port=5000, debug=True)
