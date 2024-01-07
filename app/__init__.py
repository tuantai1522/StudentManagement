from flask import Flask
from urllib.parse import quote
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user


app = Flask(__name__)

app.secret_key = '^%*&^^HJGHJGHJFD%^&%&*^*(^^^&^(*^^$%^GHJFGHJH'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/quanlyhocsinh?charset=utf8mb4" % quote(
    'MySQL2k3.')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

login = LoginManager(app)

db = SQLAlchemy(app=app)


def getclasses():
    from app.models import Lop, HocKy, NamHoc
    listClasses = db.session.query(Lop.ten_lop, NamHoc.ma_nam_hoc, NamHoc.ten_nam_hoc). \
        join(HocKy, HocKy.ma_hoc_ky == Lop.ma_hoc_ky). \
        join(NamHoc, NamHoc.ma_nam_hoc == HocKy.ma_nam_hoc). \
        order_by(Lop.ten_lop). \
        distinct().all()
    return listClasses


def getclassesofteacher(idTeacher):
    from app.models import Lop, HocKy, NamHoc
    from app.models import GiaoVien
    listClasses = db.session.query(Lop.ten_lop, NamHoc.ma_nam_hoc, NamHoc.ten_nam_hoc). \
        join(HocKy, HocKy.ma_hoc_ky == Lop.ma_hoc_ky). \
        join(NamHoc, NamHoc.ma_nam_hoc == HocKy.ma_nam_hoc). \
        join(GiaoVien, Lop.teachers). \
        filter(GiaoVien.ma == idTeacher). \
        order_by(Lop.ten_lop). \
        distinct().all()
    return listClasses


def getclassessemester(tenLop, tenNH):
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
        filter(Lop.ten_lop == tenLop, NamHoc.ten_nam_hoc == tenNH).all()

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
    _result = db.session.query(func.sum(Diem.so_diem).label('tongdiem'), func.count(Diem.so_diem).label('socondiem')). \
        select_from(Diem). \
        join(LoaiDiem, LoaiDiem.ma_loai_diem == Diem.ma_loai_diem). \
        filter(Diem.ma_hs == MaHS, LoaiDiem.ten_loai_diem.ilike(f'%15p%')).first()
    if _result.tongdiem is None:
        return None
    else:
        return _result


def get45mingrade(MaHS):
    from sqlalchemy import func
    from app.models import LoaiDiem, Diem
    _result = db.session.query(func.sum(Diem.so_diem).label('tongdiem'), func.count(Diem.so_diem).label('socondiem')). \
        select_from(Diem). \
        join(LoaiDiem, LoaiDiem.ma_loai_diem == Diem.ma_loai_diem). \
        filter(Diem.ma_hs == MaHS, LoaiDiem.ten_loai_diem.ilike(f'%1 tiết%')).first()
    if _result.tongdiem is None:
        return None
    else:
        return _result


def getfinalgrade(MaHS):
    from sqlalchemy import func
    from app.models import LoaiDiem, Diem
    _result = db.session.query(func.sum(Diem.so_diem).label('tongdiem'), func.count(Diem.so_diem).label('socondiem')). \
        select_from(Diem). \
        join(LoaiDiem, LoaiDiem.ma_loai_diem == Diem.ma_loai_diem). \
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
        _avg = (_avg_15min.tongdiem + _avg_45min.tongdiem * 2 + _avg_final.tongdiem * 3) / (
                _avg_15min.socondiem + _avg_45min.socondiem * 2 + _avg_final.socondiem * 3)
        return _avg


def update_rule(SiSoToiDa, tuoibenhat, tuoilonnhat):
    from app.models import QuyDinhSiSo, QuyDinhDoTuoi
    _getSiSoToiDa = db.session.query(QuyDinhSiSo).filter(QuyDinhSiSo.ma == 1).first()
    _getSiSoToiDa.si_so = SiSoToiDa
    _getAgeLimitData = db.session.query(QuyDinhDoTuoi).filter(QuyDinhDoTuoi.ma).first()
    _getAgeLimitData.min_Age = tuoibenhat
    _getAgeLimitData.max_age = tuoilonnhat
    db.session.commit()


def get_max_number_student_in_class():
    from app.models import QuyDinhSiSo
    _getSiSoToiDa = db.session.query(QuyDinhSiSo).filter(QuyDinhSiSo.ma == 1).first()
    return _getSiSoToiDa.si_so


def get_max_age_limit():
    from app.models import QuyDinhDoTuoi
    _getAgeLimitData = db.session.query(QuyDinhDoTuoi).filter(QuyDinhDoTuoi.ma).first()
    return _getAgeLimitData.max_age


def get_min_age_limit():
    from app.models import QuyDinhDoTuoi
    _getAgeLimitData = db.session.query(QuyDinhDoTuoi).filter(QuyDinhDoTuoi.ma).first()
    return _getAgeLimitData.min_age


def get_grade_by_classid_typegrade(MaLop, TenLoaiDiem, SoHocKy):
    from sqlalchemy import func
    from app.models import LoaiDiem, Diem, HocKy, NamHoc, Lop, HocSinh, DanhSachLop
    from sqlalchemy import text
    index = f"'%{TenLoaiDiem}%'"
    index2 = f"'%{SoHocKy}%'"
    query = text(
        f"SELECT SUM(Diem.so_diem) as tongdiem, count(Diem.so_diem) as socondiem "
        f"FROM diem "
        f"JOIN danhsachlop ON danhsachlop.ma_hoc_sinh = diem.ma_hs "
        f"JOIN hoc_sinh ON hoc_sinh.ma = danhsachlop.ma_hoc_sinh "
        f"JOIN lop ON lop.ma_lop = danhsachlop.ma_lop "
        f"JOIN loai_diem ON loai_diem.ma_loai_diem = diem.ma_loai_diem "
        f"JOIN hoc_ky ON hoc_ky.ma_hoc_ky = diem.ma_hoc_ky "
        f"WHERE lop.ma_lop = {MaLop} AND loai_diem.ten_loai_diem LIKE N{index} and hoc_ky.ten_hoc_ky like N{index2}"
    )
    _result = db.session.execute(query).fetchall()
    # _result = db.session.query(
    #     func.sum(Diem.so_diem).label('tongdiem'),
    #     func.count(Diem.so_diem).label('socondiem')
    # ).select_from(HocSinh). \
    #     join(Diem, Diem.ma_hs == HocSinh.ma).\
    #     join(Lop.students). \
    #     join(LoaiDiem, LoaiDiem.ma_loai_diem == Diem.ma_loai_diem). \
    #     filter(Lop.ma_lop == MaLop). \
    #     filter(LoaiDiem.ten_loai_diem.ilike(f'%{TenLoaiDiem}%')).first()
    # join(HocSinh, HocSinh.ma == Diem.ma_hs). \

    return _result


def getavggradebyclass(TenLop, MaNamHoc):
    from sqlalchemy import func
    from app.models import LoaiDiem, Diem, HocKy, NamHoc, Lop, HocSinh, DanhSachLop
    # Lấy ra các lớp theo tên lớp
    _getClassByTenLop = (db.session.query(Lop.ma_lop, HocKy.ten_hoc_ky, HocKy.ma_hoc_ky).select_from(Lop)
                         .join(HocKy, HocKy.ma_hoc_ky == Lop.ma_hoc_ky)
                         .filter(Lop.ten_lop == TenLop).all())
    if len(_getClassByTenLop) == 0:
        arr_Grade = [None, None]
        return arr_Grade
    _HK1 = None
    _HK2 = None
    for _getClass in _getClassByTenLop:
        if '1' in _getClass.ten_hoc_ky:
            _15pHK1 = get_grade_by_classid_typegrade(_getClass.ma_lop, '15p', 1)
            _45pHK1 = get_grade_by_classid_typegrade(_getClass.ma_lop, '1 tiết', 1)
            if _15pHK1 and _45pHK1:  # Kiểm tra xem kết quả có tồn tại không
                if _15pHK1[0].tongdiem is not None and _45pHK1[0].tongdiem is not None:
                    _HK1 = (_15pHK1[0].tongdiem + _45pHK1[0].tongdiem * 2) / (
                            _15pHK1[0].socondiem + _45pHK1[0].socondiem * 2)
        if '2' in _getClass.ten_hoc_ky:
            _15pHK2 = get_grade_by_classid_typegrade(_getClass.ma_lop, '15p', 2)
            _45pHK2 = get_grade_by_classid_typegrade(_getClass.ma_lop, '1 tiết', 2)
            if _15pHK2 and _45pHK2:  # Kiểm tra xem kết quả có tồn tại không
                if _15pHK2[0].tongdiem is not None and _45pHK2[0].tongdiem is not None:
                    _HK2 = (_15pHK2[0].tongdiem + _45pHK2[0].tongdiem * 2) / (
                            _15pHK2[0].socondiem + _45pHK2[0].socondiem * 2)
    arr_Grade = [_HK1, _HK2]
    return arr_Grade


def get15mingradebysubject_semester(MaHS, MaHocKy):
    from app.query import get_user
    from sqlalchemy import func
    from app.models import LoaiDiem, Diem, GiaoVien, MonHoc
    giaovien = None
    person = get_user(current_user.ten_dang_nhap)
    if isinstance(person, GiaoVien):
        # Nếu đúng, gán kiểu dữ liệu là GiaoVien
        giaovien = person
    _getSubject = db.session.query(MonHoc).join(GiaoVien.subjects).filter(
        GiaoVien.ma == giaovien.ma).first()
    _result = db.session.query(func.sum(Diem.so_diem).label('tongdiem'), func.count(Diem.so_diem).label('socondiem')). \
        select_from(Diem). \
        join(LoaiDiem, LoaiDiem.ma_loai_diem == Diem.ma_loai_diem). \
        filter(Diem.ma_hs == MaHS, LoaiDiem.ten_loai_diem.ilike(f'%15p%'), Diem.ma_mon_hoc == _getSubject.ma_mon_hoc,
               Diem.ma_hoc_ky == MaHocKy).first()
    if _result.tongdiem is None:
        return None
    else:
        return _result


def get45mingradebysubject_semester(MaHS, MaHocKy):
    from app.query import get_user
    from sqlalchemy import func
    from app.models import LoaiDiem, Diem, GiaoVien, MonHoc
    giaovien = None
    person = get_user(current_user.ten_dang_nhap)
    if isinstance(person, GiaoVien):
        # Nếu đúng, gán kiểu dữ liệu là GiaoVien
        giaovien = person
    _getSubject = db.session.query(MonHoc).join(GiaoVien.subjects).filter(
        GiaoVien.ma == giaovien.ma).first()
    _result = db.session.query(func.sum(Diem.so_diem).label('tongdiem'), func.count(Diem.so_diem).label('socondiem')). \
        select_from(Diem). \
        join(LoaiDiem, LoaiDiem.ma_loai_diem == Diem.ma_loai_diem). \
        filter(Diem.ma_hs == MaHS, LoaiDiem.ten_loai_diem.ilike(f'%1 tiết%'), Diem.ma_mon_hoc == _getSubject.ma_mon_hoc,
               Diem.ma_hoc_ky == MaHocKy).first()
    if _result.tongdiem is None:
        return None
    else:
        return _result

def get_avg_bysubject_semester(MaHS, MaLop):
    from app.models import HocKy, Lop
    _getMaHK = db.session.query(HocKy).join(Lop, Lop.ma_hoc_ky == HocKy.ma_hoc_ky).filter(Lop.ma_lop == MaLop).all()
    _HK1 = None
    _HK2 = None
    for semester in _getMaHK:
        if '1' in semester.ten_hoc_ky:
            _15pHK1 = get15mingradebysubject_semester(MaHS, semester.ma_hoc_ky)
            _45pHK1 = get45mingradebysubject_semester(MaHS, semester.ma_hoc_ky)
            if _15pHK1 and _45pHK1:
                _HK1 = round((_15pHK1.tongdiem + _45pHK1.tongdiem * 2) / (_15pHK1.socondiem + _45pHK1.socondiem * 2), 2)

        if '2' in semester.ten_hoc_ky:
            _15pHK2 = get15mingradebysubject_semester(MaHS, semester.ma_hoc_ky)
            _45pHK2 = get45mingradebysubject_semester(MaHS, semester.ma_hoc_ky)
            if _15pHK2 and _45pHK2:
                _HK1 = round((_15pHK2.tongdiem + _45pHK2.tongdiem * 2) / (_15pHK2.socondiem + _45pHK2.socondiem * 2), 2)
    result = [_HK1, _HK2]
    return result

