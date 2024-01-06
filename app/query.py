import hashlib

from flask import jsonify

from app.models import TaiKhoan, NguoiDung, GiaoVien, Admin, QuyDinhDoTuoi


def get_user(ten_dang_nhap):
    return GiaoVien.query.filter(GiaoVien.ten_dang_nhap == ten_dang_nhap).first() or \
           Admin.query.filter(Admin.ten_dang_nhap == ten_dang_nhap).first()


def get_user_by_username(ten_dang_nhap):
    return TaiKhoan.query.filter_by(ten_dang_nhap=ten_dang_nhap).first()


def check_login(ten_dang_nhap, mat_khau):
    if ten_dang_nhap and mat_khau:
        mat_khau = str(hashlib.md5(mat_khau.strip().encode('utf-8')).hexdigest())

        return TaiKhoan.query.filter(TaiKhoan.ten_dang_nhap.__eq__(ten_dang_nhap.strip()),
                                     TaiKhoan.mat_khau.__eq__(mat_khau)).first()


def get_max_age():
    return QuyDinhDoTuoi.query.get(1).max_age


def get_min_age():
    return QuyDinhDoTuoi.query.get(1).min_age
