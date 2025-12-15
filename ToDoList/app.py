from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

# 数据文件路径
DATA_FILE = 'todos.json'

def load_todos():
    """从文件加载待办事项"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_todos(todos):
    """保存待办事项到文件"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)

# @app.route('/')
# def index():
#     """主页"""
#     todos = load_todos()
#     return render_template('index.html', todos=todos)

@app.route('/')
def index():
    """主页"""
    todos = load_todos()
    # 传递当前日期时间到模板
    current_date = datetime.now().strftime('%Y-%m-%d')
    today_completed = sum(
        1
        for todo in todos
        if todo.get('completed_at') and todo['completed_at'].startswith(current_date)
    )
    return render_template(
        'index.html',
        todos=todos,
        datetime=datetime,
        current_date=current_date,
        today_completed=today_completed,
    )

@app.route('/add', methods=['POST'])
def add_todo():
    """添加新的待办事项"""
    title = request.form.get('title')
    if not title:
        return redirect(url_for('index'))
    
    todos = load_todos()
    new_todo = {
        'id': len(todos) + 1,
        'title': title,
        'completed': False,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'completed_at': None
    }
    todos.append(new_todo)
    save_todos(todos)
    
    return redirect(url_for('index'))

@app.route('/complete/<int:todo_id>')
def complete_todo(todo_id):
    """标记待办事项为完成"""
    todos = load_todos()
    for todo in todos:
        if todo['id'] == todo_id:
            todo['completed'] = True
            todo['completed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            break
    save_todos(todos)
    
    return redirect(url_for('index'))

@app.route('/delete/<int:todo_id>')
def delete_todo(todo_id):
    """删除待办事项"""
    todos = load_todos()
    todos = [todo for todo in todos if todo['id'] != todo_id]
    save_todos(todos)
    
    return redirect(url_for('index'))

@app.route('/uncomplete/<int:todo_id>')
def uncomplete_todo(todo_id):
    """标记待办事项为未完成"""
    todos = load_todos()
    for todo in todos:
        if todo['id'] == todo_id:
            todo['completed'] = False
            todo['completed_at'] = None
            break
    save_todos(todos)
    
    return redirect(url_for('index'))

@app.route('/api/todos', methods=['GET'])
def get_todos_api():
    """API: 获取所有待办事项"""
    todos = load_todos()
    return jsonify(todos)

@app.route('/api/todo/<int:todo_id>', methods=['PUT'])
def update_todo_api(todo_id):
    """API: 更新待办事项状态"""
    todos = load_todos()
    for todo in todos:
        if todo['id'] == todo_id:
            todo['completed'] = request.json.get('completed', todo['completed'])
            if todo['completed']:
                todo['completed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            else:
                todo['completed_at'] = None
            break
    save_todos(todos)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)