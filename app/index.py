import math

from flask import render_template, request, redirect, session, jsonify, url_for
from app import app, login, query
from flask_login import login_user, logout_user, login_required, current_user
from os import path
from app.models import TaiKhoan

# HIỆN TRANG CHỦ CỦA DASHBOARD
from app.query import get_user


@app.route('/')
def main_dashboard():
    title = "main_dashboard"
    return render_template('index.html', title=title)


@app.route('/user/details/<id>')
@login_required
def details(id):
    person = get_user(current_user.ten_dang_nhap)
    return render_template('ThongTinCaNhan.html', person=person)


# Features for Admin
@app.route('/user/tiep_nhan_hoc_sinh')
@login_required
def tiep_nhan_hoc_sinh():
    if current_user.ma_chuc_vu == 2:
        return render_template('TiepNhanHocSinh.html')
    else:
        error_msg = "Bạn không có quyền truy cập"
        return render_template('Error.html', error_msg=error_msg)


@app.route('/user/thong_ke')
@login_required
def thong_ke():
    if current_user.ma_chuc_vu == 2:
        return render_template('ThongKe.html')
    else:
        error_msg = "Bạn không có quyền truy cập"
        return render_template('Error.html', error_msg=error_msg)


@app.route('/user/thay_doi_quy_dinh')
@login_required
def thay_doi_quy_dinh():
    if current_user.ma_chuc_vu == 2:
        return render_template('ThayDoiQuyDinh.html')
    else:
        error_msg = "Bạn không có quyền truy cập"
        return render_template('Error.html', error_msg=error_msg)


@app.route('/user/lap_danh_sach_lop')
@login_required
def lap_danh_sach_lop():
    if current_user.ma_chuc_vu == 2:
        return render_template('LapDanhSachLop.html')
    else:
        error_msg = "Bạn không có quyền truy cập"
        return render_template('Error.html', error_msg=error_msg)


# Features for GiaoVien
@app.route('/user/nhap_diem')
@login_required
def nhap_diem():
    if current_user.ma_chuc_vu == 1:
        return render_template('NhapDiem.html')
    else:
        error_msg = "Bạn không có quyền truy cập"
        return render_template('Error.html', error_msg=error_msg)


@app.route('/log_in', methods=['get', 'post'])
def process_user_login():
    error_msg = ""
    if request.method.__eq__('POST'):
        try:
            username = request.form.get('username')
            password = request.form.get('password')

            user = query.check_login(username, password)

            if user:
                login_user(user=user)
                person = get_user(user.ten_dang_nhap)

                return render_template('index.html',
                                       person=person)
            else:
                error_msg = "Tên đăng nhập hoặc mật khẩu không đúng"



        except Exception as ex:
            error_msg = str(ex)

    return render_template('DangNhap.html', error_msg=error_msg)


@app.route('/log_out')
def process_logout_user():
    logout_user()
    return redirect("/")


@login.user_loader
def load_user(ten_dang_nhap):
    return query.get_user_by_username(ten_dang_nhap)


@app.context_processor
def common_resp():
    person = None
    if current_user.is_authenticated:
        person = get_user(current_user.ten_dang_nhap)

    return {'person': person}


if __name__ == "__main__":
    app.run(debug=True)
