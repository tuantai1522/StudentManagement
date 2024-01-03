from flask import Flask, render_template, request
from app import *
from db_init import *
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from os import path

# HIỆN TRANG CHỦ CỦA DASHBOARD
@app.route('/')
def main_dashboard():
    title = "main_dashboard"
    return render_template('index.html', title=title)

# THÊM CÁC ROUTE MỚI Ở ĐÂY
if __name__ == "__main__":
    app.run(debug=True)
