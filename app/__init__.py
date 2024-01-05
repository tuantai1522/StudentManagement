from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager

app = Flask(__name__)

app.secret_key = '^%*&^^HJGHJGHJFD%^&%&*^*(^^^&^(*^^$%^GHJFGHJH'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/quanlyhocsinh?charset=utf8mb4" % quote('MySQL2k3.')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

login = LoginManager(app)

db = SQLAlchemy(app=app)

def getclasses():
    # listClasses = db.session.execute(text("SELECT DISTINCT ten_lop FROM Lop ")).fetchall()
    from app.models import Lop
    listClasses = db.session.query(Lop.ten_lop).distinct().all()
    return listClasses


def getclassessemester(tenLop):
    from sqlalchemy import func
    from app.models import Lop, HocKy, NamHoc
    # listClassesSemester = db.session.execute(text(f"SELECT Lop.*, HocKy.ten_hoc_ky, NamHoc.ten_nam_hoc "
    #                                          f"FROM (SELECT* FROM Lop WHERE  ten_lop='{tenLop}') AS Lop "
    #                                          f"JOIN HocKy ON Lop.ma_hoc_ky = HocKy.ma_hoc_ky "
    #                                          f"JOIN NamHoc ON HocKy.ma_nam_hoc = NamHoc.ma_nam_hoc ")).fetchall()

    listClassesSemester = db.session.query(
        Lop.ma_lop, HocKy.ten_hoc_ky, NamHoc.ten_nam_hoc
    ). \
        join(HocKy, Lop.ma_hoc_ky == HocKy.ma_hoc_ky). \
        join(NamHoc, HocKy.ma_nam_hoc == NamHoc.ma_nam_hoc). \
        filter(Lop.ten_lop == tenLop).all()

    return listClassesSemester


def getstudentsinclass(ma_lop):
    from app.models import HocSinh, DanhSachLop, Lop
    listStudentInClass = db.session.query(HocSinh).join(Lop.students).filter(Lop.ma_lop == ma_lop).all()
    return listStudentInClass


def getlistpointtypes():
    from app.models import LoaiDiem
    listPointTypes = db.session.query(LoaiDiem).all()
    return listPointTypes


def getinfobyusername(TenDN):
    from app.models import TaiKhoan, ChucVu, GiaoVien, Admin
    _getAccountType = db.session.query(ChucVu.ten_chuc_vu). \
        select_from(ChucVu). \
        join(TaiKhoan, TaiKhoan.ma_chuc_vu == ChucVu.ma_chuc_vu). \
        filter(TaiKhoan.ten_dang_nhap == TenDN).first()
    if _getAccountType is None:
        return None
    else:
        if _getAccountType.ten_chuc_vu == 'Giáo viên':
            _getInfo = db.session.query(GiaoVien).filter(GiaoVien.ten_dang_nhap == TenDN).first()
        elif _getAccountType.ten_chuc_vu == 'Admin':
            _getInfo = db.session.query(Admin).filter(Admin.ten_dang_nhap == TenDN).first()
        else:
            _getInfo = None
    return _getInfo

def get15mingrade(MaHS):
    from sqlalchemy import func
    from app.models import LoaiDiem, Diem
    _result = db.session.query(func.sum(Diem.so_diem).label('tongdiem'), func.count(Diem.so_diem).label('socondiem')).\
        select_from(Diem).\
        join(LoaiDiem, LoaiDiem.ma_loai_diem == Diem.ma_loai_diem).\
        filter(Diem.ma_hs == MaHS, LoaiDiem.ten_loai_diem.ilike(f'%15p%')).first()
    if _result.tongdiem is None:
        return None
    else:
        return _result

def get45mingrade(MaHS):
    from sqlalchemy import func
    from app.models import LoaiDiem, Diem
    _result = db.session.query(func.sum(Diem.so_diem).label('tongdiem'), func.count(Diem.so_diem).label('socondiem')).\
        select_from(Diem).\
        join(LoaiDiem, LoaiDiem.ma_loai_diem == Diem.ma_loai_diem).\
        filter(Diem.ma_hs == MaHS, LoaiDiem.ten_loai_diem.ilike(f'%1 tiết%')).first()
    if _result.tongdiem is None:
        return None
    else:
        return _result

def getfinalgrade(MaHS):
    from sqlalchemy import func
    from app.models import LoaiDiem, Diem
    _result = db.session.query(func.sum(Diem.so_diem).label('tongdiem'), func.count(Diem.so_diem).label('socondiem')).\
        select_from(Diem).\
        join(LoaiDiem, LoaiDiem.ma_loai_diem == Diem.ma_loai_diem).\
        filter(Diem.ma_hs == MaHS, LoaiDiem.ten_loai_diem.ilike(f'%Cuối học kỳ%')).first()

    if _result.tongdiem is None:
        return None
    else:
        return _result

def getfinalaverage(MaHS):
    _avg_15min = get15mingrade(MaHS)
    _avg_45min = get45mingrade(MaHS)
    _avg_final = getfinalgrade(MaHS)
    if _avg_15min is None or _avg_45min is None or _avg_final is None:
        return None
    else:
        _avg = (_avg_15min.tongdiem + _avg_45min.tongdiem + _avg_final.tongdiem)/(_avg_15min.socondiem + _avg_45min.socondiem + _avg_final.socondiem)
        return _avg

