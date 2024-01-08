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

const chonLop = () => {
    const hocKyDropdown = document.getElementById('hoc_ky_dropdown');
    const lopDropdown = document.getElementById('lop_dropdown');


    const lopValue = lopDropdown.value;
    const hocKyValue = hocKyDropdown.value;
    if (lopValue != -1 && hocKyValue != -1) {

        fetch('/user/xem_danh_sach_lop_send_request', {
            method: 'post',
            body: JSON.stringify({
                "lop_id": lopValue,
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

                //Xóa toàn bộ dữ liệu cũ
                const table = document.getElementById("table_hoc_sinh");
                table.innerHTML = "";

                //Thêm dữ liệu mới
                const thead = table.createTHead().insertRow();
                const c1 = thead.insertCell(0);
                const c2 = thead.insertCell(1);
                const c3 = thead.insertCell(2);
                const c4 = thead.insertCell(3);
                const c5 = thead.insertCell(4);

                // Đặt giá trị cho từng ô
                c1.innerHTML = "STT";
                c2.innerHTML = "Họ tên";
                c3.innerHTML = "Giới tính";
                c4.innerHTML = "Năm sinh";
                c5.innerHTML = "Địa chỉ";

                data.list_hoc_sinh.forEach(function (element, idx) {
                    // Thêm hàng mới vào tbody
                    const row = table.insertRow();

                    // Thêm các ô (cell) mới vào hàng
                    const cell1 = row.insertCell(0);
                    const cell2 = row.insertCell(1);
                    const cell3 = row.insertCell(2);
                    const cell4 = row.insertCell(3);
                    const cell5 = row.insertCell(4);

                    // Đặt giá trị cho từng ô
                    cell1.innerHTML = idx + 1;
                    cell2.innerHTML = element.ho + " " + element.ten;
                    cell3.innerHTML = element.gioitinh;
                    cell4.innerHTML = element.namsinh;
                    cell5.innerHTML = element.diachi;
                });

                // Cập nhật sỉ số và lớp
                const lopElement = document.querySelector('.lop_info');
                const sizeElement = document.querySelector('.size');


                lopElement.textContent = data.ten_lop
                sizeElement.textContent = data.siso;

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

