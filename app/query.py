import hashlib

from flask import jsonify
from sqlalchemy import select, distinct, desc, asc

from app import db
from app.models import TaiKhoan, NguoiDung, GiaoVien, Admin, QuyDinhDoTuoi, HocSinh, DanhSachLop, Lop, HocKy, NamHoc, \
    QuyDinhSiSo


def get_user(ten_dang_nhap):
    user = GiaoVien.query.filter(GiaoVien.ten_dang_nhap == ten_dang_nhap).first() or \
           Admin.query.filter(Admin.ten_dang_nhap == ten_dang_nhap).first()
    return user


def get_user_by_username(ten_dang_nhap):
    user = TaiKhoan.query.filter_by(ten_dang_nhap=ten_dang_nhap).first()
    return user


def check_login(ten_dang_nhap, mat_khau):
    if ten_dang_nhap and mat_khau:
        mat_khau = str(hashlib.md5(mat_khau.strip().encode('utf-8')).hexdigest())

        check = TaiKhoan.query.filter(TaiKhoan.ten_dang_nhap.__eq__(ten_dang_nhap.strip()),
                                      TaiKhoan.mat_khau.__eq__(mat_khau)).first()
        return check


def get_max_age():
    max = QuyDinhDoTuoi.query.get(1).max_age
    return max


def get_min_age():
    min = QuyDinhDoTuoi.query.get(1).min_age
    return min


def get_qdss(qd_id):
    qd = QuyDinhSiSo.query.get(qd_id)
    return qd



def get_school_year():
    school_year = db.session.query(NamHoc).order_by(desc(NamHoc.ma_nam_hoc)).all()
    return school_year


def get_class_by_semester(semester_id):
    my_class = db.session.query(Lop).order_by(asc(Lop.ten_lop)).filter(Lop.ma_hoc_ky == semester_id).all()
    return my_class


# Lấy danh sách học sinh thuộc một lớp
def get_students_in_class(lop_id):
    students = (db.session.query(HocSinh)
                .join(Lop.students)
                .filter(Lop.ma_lop == lop_id)
                .all())
    return students


def get_students_not_int_class():
    # Lấy toàn bộ học sinh trong bảng phụ DanhSachLop
    students = db.session.query(HocSinh).join(Lop.students).distinct().all()

    # Sau đó lấy danh sách học sinh trong bảng HocSinh mà không có trong bảng DanhSachLop
    students_not_in_class = HocSinh.query.filter(~HocSinh.ma.in_([student.ma for student in students])).all()

    return students_not_in_class
