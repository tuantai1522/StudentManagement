import math
from datetime import datetime

from flask import render_template, request, redirect, session, jsonify, url_for
from app import *
from flask_login import login_user, logout_user, login_required, current_user
from os import path
from app.models import TaiKhoan, Lop, NamHoc, HocKy, QuyDinhSiSo, HocSinh, Diem, QuyDinhDoTuoi, GiaoVien, MonHoc
from sqlalchemy import delete

# from app import app, login, query, db

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

            max = QuyDinhSiSo.query.get(lop.ma_qdss).si_so

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
                    'ma': hoc_sinh.ma,
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


@app.route('/user/xoa_hoc_sinh_in_danh_sach_lop', methods=['delete'])
@login_required
def xoa_hoc_sinh_in_danh_sach_lop():
    try:
        data = request.json
        lop_id = data.get("lop_id")
        hs_id = data.get("hs_id")

        if lop_id and hs_id:
            # Lấy đối tượng Lop từ DB
            lop_obj = Lop.query.get(lop_id)

            # Lấy đối tượng HocSinh từ DB
            hocsinh_obj = HocSinh.query.get(hs_id)

            lop_obj.students.remove(hocsinh_obj)
            db.session.commit()

            list_hoc_sinh = get_students_in_class(lop_id)

            lop = Lop.query.get(lop_id)

            serialized_classes = []
            for hoc_sinh in list_hoc_sinh:
                serialized_classes.append({
                    'ma': hoc_sinh.ma,
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
        {'success': "Xóa học sinh khỏi lớp thành công",
         'siso': len(list_hoc_sinh),
         'ten_lop': lop.ten_lop,
         'list_hoc_sinh': serialized_classes})


# Features for GiaoVien
@app.route('/user/nhap_diem')
@login_required
# Hiển thị trang thay đổi nội quy
def noiquy_page():
    if current_user.ma_chuc_vu == 2:
        message = session.pop('message', None)
        return render_template('noiquy.html', max_si_so=get_max_number_student_in_class(),
                               min_age=get_min_age_limit(), max_age=get_max_age_limit(), message=message)
    else:
        error_msg = "Bạn không có quyền truy cập"
        return render_template('Error.html', error_msg=error_msg)


@app.route('/updaterule', methods=['POST'])
def updaterule():
    _siSoToiDa = request.form.get('sisotoida')
    _tuoiBeNhat = request.form.get('dotuoithapnhat')
    _tuoiLonNhat = request.form.get('dotuoilonnhat')
    update_rule(_siSoToiDa, _tuoiBeNhat, _tuoiLonNhat)
    session['message'] = 'Cập nhật quy định thành công'
    return redirect(url_for('noiquy_page'))


# endregion

# region HIỆN BIỂU ĐỒ ĐẬU RỚT
@app.route('/user/report')
@login_required
# Hiện header trang xem biểu đồ
def report_page():
    if current_user.ma_chuc_vu == 2:
        listClasses = db.session.query(Lop.ten_lop, NamHoc.ten_nam_hoc, NamHoc.ma_nam_hoc). \
            select_from(Lop). \
            join(HocKy, HocKy.ma_hoc_ky == Lop.ma_hoc_ky). \
            join(NamHoc, NamHoc.ma_nam_hoc == HocKy.ma_nam_hoc). \
            distinct().all()
        return render_template('report_page.html', classes=listClasses)
    else:
        error_msg = "Bạn không có quyền truy cập"
        return render_template('Error.html', error_msg=error_msg)


@app.route('/show_report/<TenLop>/<MaNamHoc>')
# Truyền dữ liệu vào trang thống kê
def show_report(TenLop, MaNamHoc):
    _getStudentInClass = db.session.query(HocSinh.ma). \
        select_from(HocSinh). \
        join(Lop.students). \
        join(HocKy, HocKy.ma_hoc_ky == Lop.ma_hoc_ky). \
        filter(HocKy.ma_nam_hoc == MaNamHoc, Lop.ten_lop == TenLop).distinct().all()
    _studentPass = 0
    _studentFail = 0
    _noti = None
    if len(_getStudentInClass) == 0:
        _noti = 'Lớp không có học sinh'
    else:
        for student in _getStudentInClass:
            if getfinalaverage(student.ma) is None:
                _noti = 'Có học sinh chưa đủ điểm để tổng kết'
                break
            elif getfinalaverage(student.ma) >= 5:
                _studentPass += 1
            else:
                _studentFail += 1
    _laySiSoToiDa = db.session.query(QuyDinhSiSo.si_so).select_from(Lop).join(QuyDinhSiSo,
                                                                              QuyDinhSiSo.ma == Lop.ma_qdss).filter(
        Lop.ten_lop == TenLop).first()
    return render_template('report.html', _classname=TenLop, noti=_noti
                           , _studentPass=_studentPass, _studentFail=_studentFail,
                           _siSoToiDa=_laySiSoToiDa.si_so,
                           _tongSinhVien=len(_getStudentInClass))


# endregion

# endregion


# Features for GiaoVien ---------------------------------------------------------

# region Giáo viên thêm điểm cho học sinh
@app.route('/user/nhap_diem/dslop/<MaLop>')
# Header trang danh sách học sinh và thông tin lớp học
def class_byclassid(MaLop):
    classInfo = db.session.query(Lop.ma_lop, Lop.ten_lop, HocKy.ma_hoc_ky, HocKy.ten_hoc_ky, NamHoc.ma_nam_hoc,
                                 NamHoc.ten_nam_hoc). \
        select_from(Lop). \
        join(HocKy, Lop.ma_hoc_ky == HocKy.ma_hoc_ky). \
        join(NamHoc, HocKy.ma_nam_hoc == NamHoc.ma_nam_hoc). \
        filter(Lop.ma_lop == MaLop).first()
    return render_template('dslop.html', classInfo=classInfo)


@app.route('/grade_table/<ma_lop>')
# Hiện danh sách học sinh của lớp và bảng điểm
def grade_table(ma_lop):
    listStudentsInClass = getstudentsinclass(ma_lop)
    listPointTypes = getlistpointtypes()
    classInfo = db.session.query(Lop.ma_lop, Lop.ten_lop, HocKy.ma_hoc_ky, HocKy.ten_hoc_ky, NamHoc.ma_nam_hoc,
                                 NamHoc.ten_nam_hoc). \
        select_from(Lop). \
        join(HocKy, Lop.ma_hoc_ky == HocKy.ma_hoc_ky). \
        join(NamHoc, HocKy.ma_nam_hoc == NamHoc.ma_nam_hoc). \
        filter(Lop.ma_lop == ma_lop).first()
    giaovien = None
    person = get_user(current_user.ten_dang_nhap)
    if isinstance(person, GiaoVien):
        # Nếu đúng, gán kiểu dữ liệu là GiaoVien
        giaovien = person

    def get_grade(MaHS, ma_hoc_ky):
        # _getGrade = db.session.query(Diem). \
        #     filter(Diem.ma_hs == MaHS, Diem.ma_hoc_ky == ma_hoc_ky). \
        #     order_by(Diem.ma_loai_diem).all()
        _getSubjectOfTeacher = db.session.query(MonHoc).join(GiaoVien.subjects).filter(
            GiaoVien.ma == giaovien.ma).first()
        _getGrade = db.session.query(Diem). \
            filter(Diem.ma_hs == MaHS, Diem.ma_mon_hoc == _getSubjectOfTeacher.ma_mon_hoc). \
            order_by(Diem.ma_loai_diem).all()
        # tuple[MaDiem, SoDiem, MaHS, ma_hoc_ky, MaLoaiDiem, ma_mon_hoc]
        _getGradeToArray = [(-1, "", MaHS, ma_hoc_ky, i, _getSubjectOfTeacher.ma_mon_hoc) for i in range(1, 10)]
        for grade in _getGrade:
            index = grade.ma_loai_diem - 1  # Lấy chỉ số phần tử trong mảng
            if 0 <= index < 10:
                _getGradeToArray[index] = (grade.ma_diem, grade.so_diem, MaHS, grade.ma_hoc_ky, grade.ma_loai_diem,
                                           _getSubjectOfTeacher.ma_mon_hoc)

        return _getGradeToArray

    def get_avggrade_bysemester(MaHS):
        result = get_avg_bysubject_semester(MaHS, ma_lop)
        return result

    return render_template('grade_table.html', studentsInClass=listStudentsInClass,
                           pointTypes=listPointTypes, get_grade=get_grade, classInfo=classInfo,
                           get_avggrade_bysemester=get_avggrade_bysemester)


@app.route('/user/nhap_diem')
@login_required
# Hiển thị danh sách các lớp học mà giáo viên đó dạy
def nhap_diem():
    if current_user.ma_chuc_vu == 1:
        person = get_user(current_user.ten_dang_nhap)
        listClasses = getclassesofteacher(person.ma)
        return render_template('NhapDiem.html', classes=listClasses, getclassessemester=getclassessemester)
    else:
        error_msg = "Bạn không có quyền truy cập"
        return render_template('Error.html', error_msg=error_msg)


@app.route('/add_point/<elementID>')
# Hàm hiển thị modal nhập điểm
def add_point(elementID):
    # < !-- tuple[MaDiem, SoDiem, MaHS, ma_hoc_ky, MaLoaiDiem] -->
    _arrayValue = elementID.split('_')
    _newMaHS = _arrayValue[2]
    _newMaHocKy = _arrayValue[3]
    _newMaLoaiDiem = _arrayValue[4]
    _newMaMonHoc = _arrayValue[5]
    _getStudent = db.session.query(HocSinh).filter(HocSinh.ma == _newMaHS).first()
    return render_template('popup_addpoint.html',
                           id=elementID,
                           _newMaHS=_newMaHS,
                           _newMaHocKy=_newMaHocKy,
                           _newMaLoaiDiem=_newMaLoaiDiem,
                           _newMaMonHoc=_newMaMonHoc,
                           _getStudent=_getStudent)


@app.route('/addgrade_form', methods=['POST'])
# Hàm nhập điểm
def addgrade_form():
    _newMaHS = request.form['MaHS']
    _newma_hoc_ky = request.form['MaHocKy']
    _newMaLoaiDiem = request.form['MaLoaiDiem']
    _newSoDiem = request.form['SoDiem']
    _newMaMonHoc = request.form['MaMonHoc']
    _newPoint = Diem(so_diem=_newSoDiem, ma_loai_diem=_newMaLoaiDiem, ma_mon_hoc=_newMaMonHoc, ma_hs=_newMaHS,
                     ma_hoc_ky=_newma_hoc_ky)
    db.session.add(_newPoint)
    db.session.commit()
    _newNoti = 'Success'
    return _newNoti


# endregion

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
