const addStudent = () => {
    const ho = document.querySelector("#ho");
    const ten = document.querySelector("#ten");
    const ngaySinh = document.querySelector("#ngaysinh");
    const gioiTinhElements = document.getElementsByName("gioitinh");
    let gioiTinh;

    for (const element of gioiTinhElements) {
        if (element.checked) {
            gioiTinh = element;
            break;
        }
    }

    const soDienThoai = document.querySelector("#sodienthoai");
    const email = document.querySelector("#email");
    const diaChi = document.querySelector("#diachi");

    console.log(ho, ten, ngaySinh, gioiTinh, soDienThoai, email, diaChi);

    fetch('/user/tiep_nhan_hoc_sinh_send_request', {
        method: 'post',
        body: JSON.stringify({
            "ho": ho.value,
            "ten": ten.value,
            "ngaysinh": ngaysinh.value,
            "gioitinh": gioiTinh.value,
            "sodienthoai": soDienThoai.value,
            "email": email.value,
            "diachi": diaChi.value,
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => {
        if (!res.ok) {
            Swal.fire({
                icon: "error",
                title: "Vui lòng điền đầy đủ thông tin",
                text: res.statusText,
                timer: 3500

            });
            throw new Error(`HTTP error! Status: ${res.status}`);
        }

        return res.json();
    }).then(data => {
        console.log(data);
        if (data.success) {
            Swal.fire({
                position: "top-end",
                icon: "success",
                title: "Thêm học sinh thành công",
                showConfirmButton: false,
                timer: 3500
            });
            resetValue();

        } else {
            Swal.fire({
                position: "top-end",
                icon: "error",
                title: data.error,
                text: "Lỗi",
                timer: 3500

            });
        }


    }).catch(err => {
        Swal.fire({
            position: "top-end",
            icon: "error",
            title: err.message,
            text: "Lỗi",
            timer: 3500

        });
    });
}

const resetValue = () => {
    const ho = document.querySelector("#ho");
    const ten = document.querySelector("#ten");
    const ngaySinh = document.querySelector("#ngaysinh");
    const gioiTinhElements = document.getElementsByName("gioitinh");


    const soDienThoai = document.querySelector("#sodienthoai");
    const email = document.querySelector("#email");
    const diaChi = document.querySelector("#diachi");

    ho.value = "";
    ten.value = "";
    ngaySinh.value = "";
    for (const element of gioiTinhElements) {
        if (element.id === "nam") {
            element.checked = true;
        } else {
            element.checked = false;
        }
    }
    diachi.value = "";
    soDienThoai.value = "";
    email.value = "";
}