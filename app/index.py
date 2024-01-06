import math
from datetime import datetime

from flask import render_template, request, redirect, session, jsonify, url_for
from app import app, login, query, db
from flask_login import login_user, logout_user, login_required, current_user
from os import path
from app.models import TaiKhoan, HocSinh

# HIỆN TRANG CHỦ CỦA DASHBOARD
from app.query import *


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
@app.route('/user/tiep_nhan_hoc_sinh', methods=['get'])
@login_required
def tiep_nhan_hoc_sinh():
    if current_user.ma_chuc_vu == 2:
        return render_template('TiepNhanHocSinh.html')
    else:
        error_msg = "Bạn không có quyền truy cập"
        return render_template('Error.html', error_msg=error_msg)


@app.route('/user/tiep_nhan_hoc_sinh_send_request', methods=['post'])
@login_required
def tiep_nhan_hoc_sinh_send_request():
    try:
        data = request.json
        ho = data.get("ho")
        ten = data.get("ten")
        gioitinh = data.get("gioitinh")
        diachi = data.get("diachi")
        sodienthoai = data.get("sodienthoai")
        email = data.get("email")
        ngaysinh = data.get("ngaysinh")

        if ho and ten and gioitinh and diachi and sodienthoai and email and ngaysinh:
            ngaysinh = datetime.strptime(ngaysinh, '%Y-%m-%d')

            min = get_min_age()
            max = get_max_age()

            age = datetime.now().year - ngaysinh.year

            if (min <= age and age <= max):
                # Add vào database
                new_student = HocSinh(ho=ho,
                                      ten=ten,
                                      so_dien_thoai=sodienthoai,
                                      gioi_tinh=gioitinh,
                                      ngay_sinh=ngaysinh,
                                      dia_chi=diachi,
                                      email=email)
                db.session.add(new_student)

                db.session.commit()
            else:
                return jsonify({'error': 'Độ tuổi tiếp nhận từ {} tới {}'.format(min, max)})
        else:
            return jsonify({'error': "Vui lòng điền đầy đủ thông tin"})

    except Exception as ex:
        return jsonify({'error': "Lỗi server"})

    # Thành công gửi dữ liệu
    return jsonify({'success': "Thêm học sinh thành công"})


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
