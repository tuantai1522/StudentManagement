import math
from datetime import datetime

from flask import render_template, request, redirect, session, jsonify, url_for
from app import app, login, query, db
from flask_login import login_user, logout_user, login_required, current_user
from os import path
from app.models import TaiKhoan, HocSinh, QuyDinhSiSo

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


@app.route('/user/get_class', methods=['post'])
@login_required
def get_class():
    try:
        data = request.json
        semester = data.get("semester")

        if semester:
            classes = get_class_by_semester(semester)

            serialized_classes = []

            for cls in classes:
                serialized_classes.append({
                    'ma_lop': cls.ma_lop,
                    'ten_lop': cls.ten_lop,
                    'si_so': len(cls.students),
                })

        else:
            return jsonify({'error': "Vui lòng chọn học kỳ"})

    except Exception as ex:
        return jsonify({'error': "Lỗi server"})

    # Thành công gửi dữ liệu
    return jsonify({'success': "Lấy dữ liệu lớp của học kỳ thành công", 'classes': serialized_classes})


@app.route('/user/lap_danh_sach_lop', methods=['get'])
@login_required
def lap_danh_sach_lop():
    if current_user.ma_chuc_vu == 2:
        students_not_in_lop = get_students_not_int_class()
        school_years = get_school_year()

        return render_template('LapDanhSachLop.html',
                               students_not_in_lop=students_not_in_lop,
                               school_years=school_years)
    else:
        error_msg = "Bạn không có quyền truy cập"
        return render_template('Error.html', error_msg=error_msg)


@app.route('/user/lap_danh_sach_lop_send_request', methods=['post'])
@login_required
def lap_danh_sach_lop_send_request():
    try:
        data = request.json
        list_id = data.get('list_id')
        lop_id = data.get("lop_id")

        if list_id and lop_id:
            lop = Lop.query.get(lop_id)

            id_array = list(map(int, list_id.split('_')))

            max = QuyDinhSiSo.query.get(lop.ma_lop).si_so

            if(len(id_array) + len(lop.students) <= max):
                for id in id_array:
                    hoc_sinh = db.session.query((HocSinh)).get(id)
                    lop.students.append(hoc_sinh)

                db.session.commit()
            else:
                return jsonify({'error': "Số lượng học sinh vượt quá qui định"})


    except Exception as ex:
        return jsonify({'error': ex})

    # Thành công gửi dữ liệu
    return jsonify({'success': "Thêm học sinh vào lớp học thành công", 'list_id': list_id, 'lop': lop.ten_lop,
                    'si_so': len(lop.students)})


@app.route('/user/xem_danh_sach_lop', methods=['get'])
@login_required
def xem_danh_sach_lop():
    if current_user.ma_chuc_vu == 2:
        school_years = get_school_year()

        return render_template('XemDanhSachLop.html',
                               school_years=school_years)
    else:
        error_msg = "Bạn không có quyền truy cập"
        return render_template('Error.html', error_msg=error_msg)


@app.route('/user/xem_danh_sach_lop_send_request', methods=['post'])
@login_required
def xem_danh_sach_lop_send_request():
    try:
        data = request.json
        lop_id = data.get("lop_id")

        if lop_id:
            list_hoc_sinh = get_students_in_class(lop_id)

            lop = Lop.query.get(lop_id)

            serialized_classes = []
            for hoc_sinh in list_hoc_sinh:

                serialized_classes.append({
                    'ho': hoc_sinh.ho,
                    'ten': hoc_sinh.ten,
                    'gioitinh': hoc_sinh.gioi_tinh,
                    'namsinh': hoc_sinh.ngay_sinh.year,
                    'diachi': hoc_sinh.dia_chi,
                })


    except Exception as ex:
        return jsonify({'error': ex})

        # Thành công gửi dữ liệu
    return jsonify(
        {'success': "Lấy danh sách học sinh thành công", 'list_hoc_sinh': serialized_classes, 'ten_lop': lop.ten_lop,
         'siso': len(list_hoc_sinh)})


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
