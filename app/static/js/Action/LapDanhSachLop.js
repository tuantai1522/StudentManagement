let info_classes;
const sizeElement = document.querySelector('.size');
let size;

const chonHocKy = () => {
    const hocKyDropdown = document.getElementById('hoc_ky_dropdown');
    const lopDropdown = document.getElementById('lop_dropdown');

    // Lấy giá trị được chọn
    const semesterValue = hocKyDropdown.value;

    if (semesterValue == -1) {
        lopDropdown.disabled = true;
        return;
    }

    //Gửi học kỳ hiện tại lên server để lấy danh sách lớp
    fetch('/user/get_class', {
        method: 'post',
        body: JSON.stringify({
            "semester": semesterValue,
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
        if (data.success) {
            sizeElement.textContent = "";

            Swal.fire({
                position: "top-end",
                icon: "success",
                title: "Lấy dữ liệu lớp thành công",
                showConfirmButton: false,
                timer: 1000
            });


            //Render ra dropdown
            lopDropdown.disabled = false;

            //Clear mọi option có trước đó
            // Xóa tất cả các option
            while (lopDropdown.options.length > 1) {
                lopDropdown.remove(1);
            }

            info_classes = data.classes;
            data.classes.forEach(data => {
                const newOption = document.createElement('option');
                newOption.value = data.ma_lop;
                newOption.text = data.ten_lop;
                lopDropdown.appendChild(newOption);
            });


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
        throw new Error(err.message);
    });

}

const Luu = (event) => {
    event.preventDefault();

    const hocKyDropdown = document.getElementById('hoc_ky_dropdown');
    const lopDropdown = document.getElementById('lop_dropdown');


    const lopValue = lopDropdown.value;
    const hocKyValue = hocKyDropdown.value;
    if (lopValue != -1 && hocKyValue != -1) {
        const selectedStudents = [];

        // Lặp qua tất cả các checkbox mà được check
        const checkboxes = document.querySelectorAll('input[name="selected_students"]:checked');
        checkboxes.forEach(function (checkbox) {
            // Lấy giá trị của checkbox
            const ma = checkbox.value;

            selectedStudents.push(ma);
        });

        if (selectedStudents.length <= 0) {
            Swal.fire({
                position: 'top-end',
                icon: "error",
                title: "Không có học sinh nào được chọn",
                text: "Không thể thực hiện",
                timer: 3500

            });
            return;
        }

        //gửi dữ liệu lên server ở đây
        const separator = '_';
        const list_id = selectedStudents.join(separator);

        console.log(list_id, lopValue)
        fetch('/user/lap_danh_sach_lop_send_request', {
            method: 'post',
            body: JSON.stringify({
                "list_id": list_id,
                "lop_id": parseInt(lopValue),
            }),
            headers: {
                'Content-Type': 'application/json'
            },
        }).then(res => {
            if (!res.ok) {
                Swal.fire({
                    position: 'top-end',
                    icon: "error",
                    title: "Lỗi",
                    text: res.statusText,
                    timer: 3500

                });
                throw new Error(`HTTP error! Status: ${res.status}`);
            }
            return res.clone().json();
        }).then(data => {
            console.log(data);
            if (data.success) {
                Swal.fire({
                    position: "top-end",
                    icon: "success",
                    title: data.success,
                    showConfirmButton: false,
                    timer: 3500
                });

                // Xóa hết các checkbox được chọn
                checkboxes.forEach(function (checkbox) {
                    const tr = checkbox.closest('tr');
                    if (tr) {
                        tr.remove();
                    }
                });

                // Cập nhât sỉ số cho người dùng xem
                size = data.si_so;
                sizeElement.textContent = `Sỉ số hiện tại của lớp ${data.lop} là ${size}`;


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


    } else {
        Swal.fire({
            icon: "error",
            title: "Vui lòng chọn học kỳ hoặc lớp tương ứng",
            text: "Lỗi",
            timer: 3500

        });
    }


}

const chonLop = () => {
    console.log(info_classes);

    //Lấy giá trị đang được chon của lop_dropdown
    const selectElement = document.getElementById("lop_dropdown");

    // Lấy giá trị được chọn
    const val = selectElement.value;

    //Duyệt qua info_classes xem lớp nào được chọn

    let currentClass;
    for (const cur of info_classes) {
        if (cur.ma_lop == val) {
            currentClass = cur;
        }
    }

    sizeElement.textContent = `Sỉ số hiện tại của lớp ${currentClass.ten_lop} là ${currentClass.si_so || size}`;


}
