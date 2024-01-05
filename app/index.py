import math

from flask import render_template, request, redirect, session, jsonify, url_for
from app import app, login, query
from app import *
from flask_login import login_user, logout_user, login_required, current_user
from os import path
from app.models import TaiKhoan, Lop, NamHoc, HocKy, QuyDinhSiSo, HocSinh, Diem, QuyDinhDoTuoi

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

@app.route('/grade_table/<ma_lop>')
def grade_table(ma_lop):
    listStudentsInClass = getstudentsinclass(ma_lop)
    listPointTypes = getlistpointtypes()
    classInfo = db.session.query(Lop.ma_lop, Lop.ten_lop, HocKy.ma_hoc_ky, HocKy.ten_hoc_ky, NamHoc.ma_nam_hoc,
                                 NamHoc.ten_nam_hoc). \
        select_from(Lop). \
        join(HocKy, Lop.ma_hoc_ky == HocKy.ma_hoc_ky). \
        join(NamHoc, HocKy.ma_nam_hoc == NamHoc.ma_nam_hoc). \
        filter(Lop.ma_lop == ma_lop).first()

    def get_grade(MaHS, ma_hoc_ky):
        # _getGrade = db.session.query(Diem). \
        #     filter(Diem.ma_hs == MaHS, Diem.ma_hoc_ky == ma_hoc_ky). \
        #     order_by(Diem.ma_loai_diem).all()
        _getGrade = db.session.query(Diem). \
            filter(Diem.ma_hs == MaHS). \
            order_by(Diem.ma_loai_diem).all()
        # tuple[MaDiem, SoDiem, MaHS, ma_hoc_ky, MaLoaiDiem]
        _getGradeToArray = [(-1, "", MaHS, ma_hoc_ky, i) for i in range(1, 10)]
        for grade in _getGrade:
            index = grade.ma_loai_diem - 1  # Lấy chỉ số phần tử trong mảng
            if 0 <= index < 10:
                _getGradeToArray[index] = (grade.ma_diem, grade.so_diem, MaHS, ma_hoc_ky, grade.ma_loai_diem)
        return _getGradeToArray

    return render_template('grade_table.html', studentsInClass=listStudentsInClass,
                           pointTypes=listPointTypes, get_grade=get_grade, classInfo=classInfo, )

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
        listClasses = getclasses()
        return render_template('NhapDiem.html', classes=listClasses, getclassessemester=getclassessemester)
    else:
        error_msg = "Bạn không có quyền truy cập"
        return render_template('Error.html', error_msg=error_msg)

@app.route('/user/nhap_diem/dslop/<MaLop>')
def class_byclassid(MaLop):
    classInfo = db.session.query(Lop.ma_lop, Lop.ten_lop, HocKy.ma_hoc_ky, HocKy.ten_hoc_ky, NamHoc.ma_nam_hoc,
                                 NamHoc.ten_nam_hoc). \
        select_from(Lop). \
        join(HocKy, Lop.ma_hoc_ky == HocKy.ma_hoc_ky). \
        join(NamHoc, HocKy.ma_nam_hoc == NamHoc.ma_nam_hoc). \
        filter(Lop.ma_lop == MaLop).first()
    return render_template('dslop.html', classInfo=classInfo)

@app.route('/user/report')
def report_page():
    listClasses = db.session.query(Lop.ten_lop, NamHoc.ten_nam_hoc, NamHoc.ma_nam_hoc). \
        select_from(Lop). \
        join(HocKy, HocKy.ma_hoc_ky == Lop.ma_hoc_ky). \
        join(NamHoc, NamHoc.ma_nam_hoc == HocKy.ma_nam_hoc). \
        distinct().all()
    return render_template('report_page.html', classes=listClasses)

@app.route('/show_report/<TenLop>/<MaNamHoc>')
def show_report(TenLop, MaNamHoc):
    _getStudentInClass = db.session.query(HocSinh.ma).\
        select_from(HocSinh). \
        join(Lop.students). \
        join(HocKy, HocKy.ma_hoc_ky == Lop.ma_hoc_ky).\
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
    _laySiSoToiDa = db.session.query(QuyDinhSiSo.si_so).select_from(Lop).join(QuyDinhSiSo, QuyDinhSiSo.ma == Lop.ma_qdss).filter(Lop.ten_lop == TenLop).first()
    # _SiSoToiDa = db.session.query(text(TenLop)).select_from(Lop).join(QuyDinhSiSo, QuyDinhSiSo.si_so)
    return render_template('report.html', _classname=TenLop, noti=_noti
                           , _studentPass=_studentPass, _studentFail=_studentFail,
                           _siSoToiDa=_laySiSoToiDa.si_so,
                           _tongSinhVien=len(_getStudentInClass))

@app.route('/add_point/<elementID>')
def add_point(elementID):
    # < !-- tuple[MaDiem, SoDiem, MaHS, ma_hoc_ky, MaLoaiDiem] -->
    _arrayValue = elementID.split('_')
    _newMaHS = _arrayValue[2]
    _newMaHocKy = _arrayValue[3]
    _newMaLoaiDiem = _arrayValue[4]

    _getStudent = db.session.query(HocSinh).filter(HocSinh.ma == _newMaHS).first()
    return render_template('popup_addpoint.html',
                           id=elementID,
                           _newMaHS=_newMaHS,
                           _newMaHocKy=_newMaHocKy,
                           _newMaLoaiDiem=_newMaLoaiDiem,
                           _getStudent=_getStudent)

@app.route('/addgrade_form', methods=['POST'])
def addgrade_form():
    _newMaHS = request.form['MaHS']
    _newma_hoc_ky = request.form['MaHocKy']
    _newMaLoaiDiem = request.form['MaLoaiDiem']
    _newSoDiem = request.form['SoDiem']
    _newPoint = Diem(so_diem=_newSoDiem, ma_loai_diem=_newMaLoaiDiem, ma_mon_hoc=1, ma_hs=_newMaHS,
                     ma_hoc_ky=_newma_hoc_ky)
    db.session.add(_newPoint)
    db.session.commit()
    _newNoti = 'Success'
    return _newNoti
# @app.route('/user/report')
# def report_page():
#     listClasses = db.session.query(Lop.ten_lop, NamHoc.ten_nam_hoc, NamHoc.ma_nam_hoc). \
#         select_from(Lop). \
#         join(HocKy, HocKy.ma_hoc_ky == Lop.ma_hoc_ky). \
#         join(NamHoc, NamHoc.ma_nam_hoc == HocKy.ma_nam_hoc). \
#         distinct().all()
#     return render_template('report_page.html', classes=listClasses)

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

# REGION THAY ĐỔI NỘI QUY
@app.route('/noiquy')
def noiquy_page():
    message = session.pop('message', None)
    return render_template('noiquy.html', max_si_so=get_max_number_student_in_class(),
                           min_age=get_min_age_limit(), max_age=get_max_age_limit(), message=message)
@app.route('/updaterule', methods=['POST'])
def updaterule():
    _siSoToiDa = request.form.get('sisotoida')
    _tuoiBeNhat = request.form.get('dotuoithapnhat')
    _tuoiLonNhat = request.form.get('dotuoilonnhat')
    update_rule(_siSoToiDa, _tuoiBeNhat, _tuoiLonNhat)
    session['message'] = 'Cập nhật quy định thành công'
    return redirect(url_for('noiquy_page'))

# ENDREGION


if __name__ == "__main__":
    app.run(debug=True)
