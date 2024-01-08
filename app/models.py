from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, text
from sqlalchemy.orm import relationship, backref
from app import db
from flask_login import UserMixin
from datetime import datetime


# REGION CREATE TABLE

class ChucVu(db.Model):
    ma_chuc_vu = Column(Integer, primary_key=True, autoincrement=True)
    ten_chuc_vu = Column(String(20))

    # Thiết lập để lấy đối tượng
    TaiKhoan = relationship('TaiKhoan', backref="ChucVu", lazy=True)


class TaiKhoan(db.Model, UserMixin):
    ten_dang_nhap = Column(String(100), primary_key=True)
    mat_khau = Column(String(100), nullable=False)

    ma_chuc_vu = Column(Integer, ForeignKey(ChucVu.ma_chuc_vu))

    # Thiết lập để lấy đối tượng
    GiaoVien = relationship('GiaoVien', backref="TaiKhoan", lazy=True)
    Admin = relationship('Admin', backref="TaiKhoan", lazy=True)

    def __str__(self):
        return self.ten_dang_nhap

    def get_id(self):
        return self.ten_dang_nhap


class NguoiDung(db.Model):
    __abstract__ = True

    ma = Column(db.Integer, primary_key=True, autoincrement=True)
    ho = Column(String(50), nullable=False)
    ten = Column(String(50), nullable=False)
    so_dien_thoai = Column(String(12))


class HocSinh(NguoiDung):
    gioi_tinh = Column(String(10))
    ngay_sinh = Column(DateTime)
    dia_chi = Column(String(50))
    email = Column(String(100))

    # Thiết lập để lấy đối tượng
    Diem = relationship('Diem', backref="HocSinh", lazy=True)


class Admin(NguoiDung):
    ten_dang_nhap = Column(db.String(100), db.ForeignKey(TaiKhoan.ten_dang_nhap))


class GiaoVien(NguoiDung):
    luong_co_ban = Column(Float)
    he_so_luong = Column(Float)
    ten_dang_nhap = Column(String(100), ForeignKey(TaiKhoan.ten_dang_nhap))
    # Backref đến bảng môn học để lấy giá trị và ngược lại
    subjects = relationship('MonHoc', secondary='GiaoVien_MonHoc', backref=db.backref('teachers', lazy='dynamic'))
    # classes = relationship('Lop', secondary='GiaoVien_Lop', backref='teachers')


class MonHoc(db.Model):
    ma_mon_hoc = Column(Integer, primary_key=True, autoincrement=True)
    ten_mon_hoc = Column(String(20))

    # Thiết lập để lấy đối tượng
    Diem = relationship('Diem', backref="MonHoc", lazy=True)


GiaoVien_MonHoc = db.Table('GiaoVien_MonHoc',
                           Column('ma_mon_hoc', Integer, ForeignKey(MonHoc.ma_mon_hoc)),
                           Column('ma_giao_vien', Integer, ForeignKey(GiaoVien.ma))
                           )


class KhoiLop(db.Model):
    ma_khoi_lop = Column(Integer, primary_key=True)
    ten_khoi_lop = Column(String(20))

    # Thiết lập để lấy đối tượng
    Lop = relationship('Lop', backref="KhoiLop", lazy=True)


class QuyDinh(db.Model):
    __abstract__ = True
    ma = Column(db.Integer, autoincrement=True, primary_key=True)
    ten = Column(String(40), nullable=False, unique=True)


class QuyDinhSiSo(QuyDinh):
    si_so = Column(Integer)

    # Thiết lập để lấy đối tượng
    Lop = relationship('Lop', backref="QuyDinhSiSo", lazy=True)


class QuyDinhDoTuoi(QuyDinh):
    min_age = Column(Integer, nullable=False)
    max_age = Column(Integer, nullable=False)


class NamHoc(db.Model):
    ma_nam_hoc = Column(Integer, primary_key=True)
    ten_nam_hoc = Column(String(20))

    # Thiết lập để lấy đối tượng
    HocKy = relationship('HocKy', backref="NamHoc", lazy=True)


class HocKy(db.Model):
    ma_hoc_ky = db.Column(Integer, primary_key=True, autoincrement=True)
    ten_hoc_ky = db.Column(String(20))
    ma_nam_hoc = db.Column(Integer, ForeignKey(NamHoc.ma_nam_hoc))

    # Thiết lập để lấy đối tượng
    Lop = relationship('Lop', backref="HocKy", lazy=True)

    Diem = relationship('Diem', backref="HocKy", lazy=True)


class Lop(db.Model):
    ma_lop = Column(Integer, primary_key=True, autoincrement=True)
    ten_lop = Column(String(10), nullable=False)
    ma_qdss = Column(Integer, ForeignKey(QuyDinhSiSo.ma))
    ma_khoi_lop = Column(Integer, ForeignKey(KhoiLop.ma_khoi_lop))
    ma_hoc_ky = Column(Integer, ForeignKey(HocKy.ma_hoc_ky))

    # Sử dụng relationship để thiết lập quan hệ với bảng HOCSINH thông qua bảng trung gian DSLOP
    students = relationship('HocSinh', secondary='DanhSachLop', backref=db.backref('classes', lazy='dynamic'))
    # Sử dụng relationship để thiết lập quan hệ với bảng GiaoVien thông qua bảng trung gian GiaoVien_Lop
    teachers = relationship('GiaoVien', secondary='GiaoVien_Lop', backref=db.backref('classes', lazy='dynamic'))


DanhSachLop = db.Table('DanhSachLop',
                       Column('ma_lop', Integer, ForeignKey(Lop.ma_lop)),
                       Column('ma_hoc_sinh', Integer, ForeignKey(HocSinh.ma))
                       )

GiaoVien_Lop = db.Table('GiaoVien_Lop',
                        Column('ma_lop', Integer, ForeignKey(Lop.ma_lop)),
                        Column('ma_giao_vien', Integer, ForeignKey(GiaoVien.ma))
                        )


class LoaiDiem(db.Model):
    ma_loai_diem = db.Column(Integer, primary_key=True, autoincrement=True)
    ten_loai_diem = db.Column(String(20))

    # Thiết lập để lấy đối tượng
    Diem = relationship('Diem', backref="LoaiDiem", lazy=True)


class Diem(db.Model):
    ma_diem = Column(db.Integer, primary_key=True, autoincrement=True)
    so_diem = Column(db.Float, nullable=False)
    ma_loai_diem = Column(Integer, ForeignKey(LoaiDiem.ma_loai_diem))
    ma_mon_hoc = Column(Integer, ForeignKey(MonHoc.ma_mon_hoc))
    ma_hs = Column(Integer, ForeignKey(HocSinh.ma))
    ma_hoc_ky = Column(Integer, ForeignKey(HocKy.ma_hoc_ky))


# TẠO DỮ LIỆU MẪU
if __name__ == "__main__":
    from app import app

    with app.app_context():
        db.drop_all()
        db.create_all()

        _newRole1 = ChucVu(ten_chuc_vu='Giáo viên')
        db.session.add(_newRole1)

        _newRole2 = ChucVu(ten_chuc_vu='Admin')
        db.session.add(_newRole2)

        import hashlib

        _newAccount1 = TaiKhoan(ten_dang_nhap='gv1',
                                mat_khau=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
                                ma_chuc_vu=1)
        db.session.add(_newAccount1)

        _newAccount3 = TaiKhoan(ten_dang_nhap='gv2',
                                mat_khau=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
                                ma_chuc_vu=1)
        db.session.add(_newAccount3)

        _newAccount2 = TaiKhoan(ten_dang_nhap='admin1',
                                mat_khau=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
                                ma_chuc_vu=2)
        db.session.add(_newAccount2)
        db.session.commit()

        _newTeacher1 = GiaoVien(ho='Nguyễn',
                               ten='Lê Đăng Khoa',
                               so_dien_thoai='1231231231',
                               luong_co_ban=1000000,
                               he_so_luong=1,
                               ten_dang_nhap='gv1')
        db.session.add(_newTeacher1)
        db.session.commit()

        _newTeacher2 = GiaoVien(ho='Nguyễn',
                               ten='Lê Đa',
                               so_dien_thoai='1231231231',
                               luong_co_ban=1000000,
                               he_so_luong=1,
                               ten_dang_nhap='gv2')
        db.session.add(_newTeacher2)
        db.session.commit()

        _newAdmin = Admin(ho='Nguyễn',
                          ten=' Tuấn Tài',
                          so_dien_thoai='1231231231',
                          ten_dang_nhap='admin1')
        db.session.add(_newAdmin)
        db.session.commit()

        _newSubject = MonHoc(ten_mon_hoc='Toán')
        db.session.add(_newSubject)
        db.session.commit()

        _newGrade = KhoiLop(ma_khoi_lop=10, ten_khoi_lop='Khối 10')
        db.session.add(_newGrade)

        _newGrade = KhoiLop(ma_khoi_lop=11, ten_khoi_lop='Khối 11')
        db.session.add(_newGrade)

        _newGrade = KhoiLop(ma_khoi_lop=12, ten_khoi_lop='Khối 12')
        db.session.add(_newGrade)
        db.session.commit()

        _newNumberOfStudent = QuyDinhSiSo(ten='Sĩ số tối đa là 40', si_so=40)
        db.session.add(_newNumberOfStudent)

        _newStudent = HocSinh(ho='La',
                              ten='Khuê',
                              so_dien_thoai='312321312',
                              gioi_tinh='Nữ',
                              ngay_sinh=datetime(2023, 12, 31),
                              dia_chi='132',
                              email='hs0@gmail.com')
        db.session.add(_newStudent)

        _newStudent1 = HocSinh(ho='Nguyễn',
                               ten='Lê Đăng Khoa',
                               so_dien_thoai='123123123',
                               gioi_tinh='Nam',
                               ngay_sinh=datetime(2003, 1, 1),
                               dia_chi='123 Lê Văn Lương Phường 14 Quận 7',
                               email='hs1@gmail.com')
        db.session.add(_newStudent1)

        _newStudent2 = HocSinh(ho='Nguyễn',
                               ten='Lê Đăng Khoa 2',
                               so_dien_thoai='456456456',
                               gioi_tinh='Nam',
                               ngay_sinh=datetime(2003, 1, 1),
                               dia_chi='124 Lê Văn Lương Phường 14 Quận 7',
                               email='hs2@gmail.com')
        db.session.add(_newStudent2)

        _newStudent3 = HocSinh(ho='Nguyễn',
                               ten='Lê Đăng Khoa 3',
                               so_dien_thoai='789789789',
                               gioi_tinh='Nam',
                               ngay_sinh=datetime(2003, 1, 1),
                               dia_chi='125 Lê Văn Lương Phường 14 Quận 7',
                               email='hs3@gmail.com')
        db.session.add(_newStudent3)

        _newStudent4 = HocSinh(ho='Nguyễn',
                               ten='Lê Đăng Khoa 4',
                               so_dien_thoai='56746545',
                               gioi_tinh='Nữ',
                               ngay_sinh=datetime(2003, 1, 1),
                               dia_chi='300 Lê Văn Lương Phường 14 Quận 7',
                               email='hs4@gmail.com')
        db.session.add(_newStudent4)

        _newStudent4 = HocSinh(ho='Nguyễn',
                               ten='Lê Đăng Khoa 5',
                               so_dien_thoai='56746545',
                               gioi_tinh='Nữ',
                               ngay_sinh=datetime(2003, 1, 1),
                               dia_chi='300 Lê Văn Lương Phường 14 Quận 7',
                               email='hs5@gmail.com')
        db.session.add(_newStudent4)

        _newStudent4 = HocSinh(ho='Nguyễn',
                               ten='Lê Đăng Khoa 6',
                               so_dien_thoai='56746545',
                               gioi_tinh='Nữ',
                               ngay_sinh=datetime(2003, 1, 1),
                               dia_chi='300 Lê Văn Lương Phường 14 Quận 7',
                               email='hs6@gmail.com')
        db.session.add(_newStudent4)

        _newStudent4 = HocSinh(ho='Nguyễn',
                               ten='Lê Đăng Khoa 7',
                               so_dien_thoai='56746545',
                               gioi_tinh='Nữ',
                               ngay_sinh=datetime(2003, 1, 1),
                               dia_chi='300 Lê Văn Lương Phường 14 Quận 7',
                               email='hs7@gmail.com')
        db.session.add(_newStudent4)

        db.session.commit()

        nam_hoc = NamHoc(ma_nam_hoc=2023, ten_nam_hoc='NĂM HỌC 2023-2024')
        db.session.add(nam_hoc)
        db.session.commit()

        hoc_ki1 = HocKy(ten_hoc_ky='HỌC KÌ 1', ma_nam_hoc='2023')
        db.session.add(hoc_ki1)

        hoc_ki2 = HocKy(ten_hoc_ky='HỌC KÌ 2', ma_nam_hoc='2023')
        db.session.add(hoc_ki2)
        db.session.commit()

        lop11 = Lop(ten_lop='10A1', ma_khoi_lop='10', ma_qdss=1, ma_hoc_ky='1')
        db.session.add(lop11)

        lop12 = Lop(ten_lop='10A1', ma_khoi_lop='10', ma_qdss=1, ma_hoc_ky='2')
        db.session.add(lop12)

        lop21 = Lop(ten_lop='10A2', ma_khoi_lop='10', ma_qdss=1, ma_hoc_ky='1')
        db.session.add(lop21)

        lop22 = Lop(ten_lop='10A2', ma_khoi_lop='10', ma_qdss=1, ma_hoc_ky='2')
        db.session.add(lop22)

        lop31 = Lop(ten_lop='10A3', ma_khoi_lop='10', ma_qdss=1, ma_hoc_ky='1')
        db.session.add(lop31)

        lop32 = Lop(ten_lop='10A3', ma_khoi_lop='10', ma_qdss=1, ma_hoc_ky='2')
        db.session.add(lop32)

        lop41 = Lop(ten_lop='10A4', ma_khoi_lop='10', ma_qdss=1, ma_hoc_ky='1')
        db.session.add(lop41)

        lop42 = Lop(ten_lop='10A4', ma_khoi_lop='10', ma_qdss=1, ma_hoc_ky='2')
        db.session.add(lop42)
        db.session.commit()

        for i in range(1, 6):
            _newGradeType = LoaiDiem(ten_loai_diem=f'15p({i})')
            db.session.add(_newGradeType)
            db.session.commit()

        for i in range(1, 4):
            _newGradeType = LoaiDiem(ten_loai_diem=f'1 tiết({i})')
            db.session.add(_newGradeType)
            db.session.commit()

        _newGradeType = LoaiDiem(ten_loai_diem=f'Cuối học kỳ')
        db.session.add(_newGradeType)
        db.session.commit()
        # region Thêm điểm học sinh 1
        _newPoint1 = Diem(so_diem=9, ma_loai_diem=1, ma_mon_hoc=1, ma_hs=1, ma_hoc_ky=1)
        db.session.add(_newPoint1)

        _newPoint1 = Diem(so_diem=9, ma_loai_diem=2, ma_mon_hoc=1, ma_hs=1, ma_hoc_ky=1)
        db.session.add(_newPoint1)

        _newPoint1 = Diem(so_diem=8, ma_loai_diem=3, ma_mon_hoc=1, ma_hs=1, ma_hoc_ky=1)
        db.session.add(_newPoint1)

        _newPoint1 = Diem(so_diem=10, ma_loai_diem=6, ma_mon_hoc=1, ma_hs=1, ma_hoc_ky=1)
        db.session.add(_newPoint1)

        _newPoint1 = Diem(so_diem=5, ma_loai_diem=7, ma_mon_hoc=1, ma_hs=1, ma_hoc_ky=1)
        db.session.add(_newPoint1)

        _newPoint1 = Diem(so_diem=10, ma_loai_diem=9, ma_mon_hoc=1, ma_hs=1, ma_hoc_ky=1)
        db.session.add(_newPoint1)
        # endregion

        # region Thêm điểm học sinh 2
        _newPoint2 = Diem(so_diem=5, ma_loai_diem=1, ma_mon_hoc=1, ma_hs=2, ma_hoc_ky=1)
        db.session.add(_newPoint2)

        _newPoint2 = Diem(so_diem=9, ma_loai_diem=2, ma_mon_hoc=1, ma_hs=2, ma_hoc_ky=1)
        db.session.add(_newPoint2)

        _newPoint2 = Diem(so_diem=8, ma_loai_diem=3, ma_mon_hoc=1, ma_hs=2, ma_hoc_ky=1)
        db.session.add(_newPoint2)

        _newPoint2 = Diem(so_diem=5, ma_loai_diem=7, ma_mon_hoc=1, ma_hs=2, ma_hoc_ky=1)
        db.session.add(_newPoint2)

        _newPoint2 = Diem(so_diem=10, ma_loai_diem=9, ma_mon_hoc=1, ma_hs=2, ma_hoc_ky=1)
        db.session.add(_newPoint2)
        # endregion

        # region Thêm điểm học sinh 3
        _newPoint3 = Diem(so_diem=1, ma_loai_diem=1, ma_mon_hoc=1, ma_hs=3, ma_hoc_ky=1)
        db.session.add(_newPoint3)

        _newPoint3 = Diem(so_diem=5, ma_loai_diem=6, ma_mon_hoc=1, ma_hs=3, ma_hoc_ky=1)
        db.session.add(_newPoint3)

        _newPoint3 = Diem(so_diem=1, ma_loai_diem=9, ma_mon_hoc=1, ma_hs=3, ma_hoc_ky=1)
        db.session.add(_newPoint3)
        # endregion

        # region Thêm điểm học sinh 4
        _newPoint4 = Diem(so_diem=9, ma_loai_diem=1, ma_mon_hoc=1, ma_hs=4, ma_hoc_ky=1)
        db.session.add(_newPoint4)

        _newPoint4 = Diem(so_diem=5, ma_loai_diem=6, ma_mon_hoc=1, ma_hs=4, ma_hoc_ky=1)
        db.session.add(_newPoint4)

        _newPoint4 = Diem(so_diem=1, ma_loai_diem=9, ma_mon_hoc=1, ma_hs=4, ma_hoc_ky=1)
        db.session.add(_newPoint4)
        # endregion

        db.session.commit()

        db.session.execute(text("INSERT INTO DanhSachLop VALUES (1, 1)"))
        db.session.execute(text("INSERT INTO DanhSachLop VALUES (1, 2)"))
        db.session.execute(text("INSERT INTO DanhSachLop VALUES (1, 3)"))
        db.session.execute(text("INSERT INTO DanhSachLop VALUES (2, 1)"))
        db.session.execute(text("INSERT INTO DanhSachLop VALUES (2, 2)"))
        db.session.execute(text("INSERT INTO DanhSachLop VALUES (3, 4)"))
        db.session.execute(text("INSERT INTO DanhSachLop VALUES (3, 5)"))
        db.session.execute(text("INSERT INTO DanhSachLop VALUES (4, 4)"))
        db.session.execute(text("INSERT INTO DanhSachLop VALUES (4, 5)"))
        db.session.execute(text("INSERT INTO DanhSachLop VALUES (5, 6)"))
        db.session.execute(text("INSERT INTO DanhSachLop VALUES (6, 6)"))
        db.session.execute(text("INSERT INTO DanhSachLop VALUES (7, 7)"))
        db.session.execute(text("INSERT INTO DanhSachLop VALUES (8, 7)"))

        _newTeacher1.classes.append(lop11)
        _newTeacher1.classes.append(lop12)
        _newTeacher1.classes.append(lop31)
        _newTeacher1.classes.append(lop32)
        _newTeacher2.classes.append(lop21)
        _newTeacher2.classes.append(lop22)
        _newTeacher2.classes.append(lop41)
        _newTeacher2.classes.append(lop42)

        _newTeacher1.subjects.append(_newSubject)
        _newTeacher2.subjects.append(_newSubject)
        db.session.commit()

        _newAgeLimit = QuyDinhDoTuoi(ten="Độ tuổi nhỏ nhất là 15", min_age=15, max_age=20)
        db.session.add(_newAgeLimit)
        db.session.commit()

# ENDREGION