
import json
from pathlib import Path
from datetime import datetime


# Xác định thư mục gốc của dự án
THU_MUC_DU_AN = Path(__file__).resolve().parents[2]

# Đường dẫn file cấu hình nghiên cứu
DUONG_DAN_CAU_HINH = (
    THU_MUC_DU_AN / "config" / "research_config.json"
)


def doc_cau_hinh():
    """Đọc cấu hình nghiên cứu từ file JSON."""

    if not DUONG_DAN_CAU_HINH.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file cấu hình: {DUONG_DAN_CAU_HINH}"
        )

    try:
        with open(
            DUONG_DAN_CAU_HINH,
            "r",
            encoding="utf-8"
        ) as tep:
            return json.load(tep)

    except json.JSONDecodeError as loi:
        raise ValueError(
            f"File JSON không đúng định dạng: {loi}"
        ) from loi


def kiem_tra_cau_hinh(cau_hinh):
    """Kiểm tra cấu trúc và tính nhất quán của cấu hình nghiên cứu."""

    # 1. Kiểm tra các mục bắt buộc
    cac_muc_bat_buoc = [
        "de_tai",
        "tai_san_nghien_cuu",
        "bien_nghien_cuu",
        "cau_hoi_nghien_cuu",
        "cau_hinh_du_lieu",
        "trang_thai_thi_truong",
        "du_bao_rui_ro",
        "mo_hinh",
        "danh_gia",
        "kiem_soat_chat_luong_du_lieu",
    ]

    for muc in cac_muc_bat_buoc:
        if muc not in cau_hinh:
            raise ValueError(f"Cấu hình còn thiếu mục: {muc}")

    # 2. Kiểm tra thời gian nghiên cứu
    de_tai = cau_hinh["de_tai"]

    try:
        ngay_bat_dau = datetime.strptime(
            de_tai["ngay_bat_dau"], "%Y-%m-%d"
        )
        ngay_ket_thuc = datetime.strptime(
            de_tai["ngay_ket_thuc"], "%Y-%m-%d"
        )
    except (KeyError, TypeError, ValueError) as loi:
        raise ValueError(
            "Ngày nghiên cứu phải đúng định dạng YYYY-MM-DD "
            "và là ngày hợp lệ."
        ) from loi

    if ngay_bat_dau >= ngay_ket_thuc:
        raise ValueError("Ngày bắt đầu phải trước ngày kết thúc.")

    # 3. Kiểm tra tài sản nghiên cứu
    tai_san = cau_hinh["tai_san_nghien_cuu"]

    if not all(
        ma in tai_san.get("ma_tien_ma_hoa", [])
        for ma in ["BTC", "ETH"]
    ):
        raise ValueError("Nghiên cứu phải có cả BTC và ETH.")

    # 4. Kiểm tra câu hỏi nghiên cứu
    cau_hoi = cau_hinh["cau_hoi_nghien_cuu"]

    for ma_cau_hoi in ["RQ1", "RQ2", "RQ3", "RQ4", "RQ5"]:
        if ma_cau_hoi not in cau_hoi:
            raise ValueError(
                f"Cấu hình còn thiếu câu hỏi: {ma_cau_hoi}"
            )

    # 5. Kiểm tra các bộ dữ liệu theo JSON mới nhất
    cau_hinh_du_lieu = cau_hinh["cau_hinh_du_lieu"]

    cac_bo_du_lieu = [
        "bo_du_lieu_truyen_dan",
        "bo_du_lieu_hoc_may",
    ]

    for ten_bo in cac_bo_du_lieu:
        if ten_bo not in cau_hinh_du_lieu:
            raise ValueError(
                f"Cấu hình còn thiếu bộ dữ liệu: {ten_bo}"
            )

        bo_du_lieu = cau_hinh_du_lieu[ten_bo]

        for truong in [
            "ten",
            "muc_dich",
            "tan_suat",
            "lich_du_lieu",
            "tai_san",
            "quy_tac",
        ]:
            if truong not in bo_du_lieu:
                raise ValueError(
                    f"Bộ dữ liệu {ten_bo} còn thiếu: {truong}"
                )

    # 6. Kiểm tra đường dẫn và lịch của model_dataset
    bo_truyen_dan = cau_hinh_du_lieu["bo_du_lieu_truyen_dan"]

    if bo_truyen_dan.get("ten") != "model_dataset":
        raise ValueError("Tên bộ dữ liệu chuẩn phải là model_dataset.")

    if bo_truyen_dan.get("duong_dan") != (
        "data/processed/model_dataset.csv"
    ):
        raise ValueError(
            "Đường dẫn model_dataset phải là "
            "data/processed/model_dataset.csv."
        )

    if bo_truyen_dan.get("lich_du_lieu") != "tat_ca_cac_ngay_UTC":
        raise ValueError(
            "model_dataset phải giữ lịch BTC/ETH tất cả các ngày UTC."
        )
    
    bo_hoc_may = cau_hinh_du_lieu["bo_du_lieu_hoc_may"]

    if bo_hoc_may.get("ten") != "ml_dataset":
        raise ValueError("Tên bộ dữ liệu học máy phải là ml_dataset.")

    if bo_hoc_may.get("duong_dan") != "data/processed/ml_dataset.csv":
        raise ValueError(
        "Đường dẫn ML dataset phải là data/processed/ml_dataset.csv."
        )


    # 7. Kiểm tra phân công thành viên nếu được khai báo
    thanh_vien = cau_hinh_du_lieu.get("thanh_vien_su_dung", {})

    for ten_tv, thong_tin in thanh_vien.items():
        if not isinstance(thong_tin, dict):
            raise ValueError(
                f"Thông tin phân công của {ten_tv} không hợp lệ."
            )

        if not thong_tin.get("file_dau_vao"):
            raise ValueError(
                f"Phân công của {ten_tv} chưa có file đầu vào."
            )

        if "quy_tac" not in thong_tin:
            raise ValueError(
                f"Phân công của {ten_tv} chưa có quy tắc."
            )

    # 8. Kiểm tra mô hình nghiên cứu
    mo_hinh = cau_hinh["mo_hinh"]

    cac_mo_hinh_bat_buoc = [
        "kinh_te_luong_co_so",
        "kinh_te_luong_mo_rong",
        "hoc_may_co_so",
        "hoc_may_phi_tuyen",
    ]

    for ten_mo_hinh in cac_mo_hinh_bat_buoc:
        if ten_mo_hinh not in mo_hinh:
            raise ValueError(
                f"Cấu hình còn thiếu mô hình: {ten_mo_hinh}"
            )

    # 9. Kiểm tra chân trời dự báo
    du_bao = cau_hinh["du_bao_rui_ro"]
    chan_du_bao = du_bao.get("chan_du_bao_ngay", [])

    if not chan_du_bao or any(
        type(ngay) is not int or ngay <= 0
        for ngay in chan_du_bao
    ):
        raise ValueError(
            "Các chân trời dự báo phải là số nguyên dương."
        )

    if chan_du_bao != [1]:
        raise ValueError(
            "Cấu hình hiện tại yêu cầu chân trời dự báo một ngày: [1]."
        )

    # 10. Kiểm tra phương pháp đánh giá
    danh_gia = cau_hinh["danh_gia"]

    if danh_gia.get("phuong_phap_kiem_dinh") != "rolling_origin":
        raise ValueError(
            "Phương pháp kiểm định phải là rolling_origin."
        )

    if not danh_gia.get("bat_buoc_kiem_dinh_ngoai_mau", False):
        raise ValueError(
            "Nghiên cứu phải bật kiểm định ngoài mẫu."
        )

    return True


def main():
    """Đọc, kiểm tra và in thông tin nghiên cứu."""

    cau_hinh = doc_cau_hinh()
    kiem_tra_cau_hinh(cau_hinh)

    print("Đọc và kiểm tra cấu hình thành công!")
    print("Tên đề tài:", cau_hinh["de_tai"]["ten"])

    print(
        "Giai đoạn:",
        cau_hinh["de_tai"]["ngay_bat_dau"],
        "đến",
        cau_hinh["de_tai"]["ngay_ket_thuc"],
    )

    print(
        "Tài sản:",
        ", ".join(
            cau_hinh["tai_san_nghien_cuu"]["ma_tien_ma_hoa"]
        ),
    )

    print(
        "Số câu hỏi nghiên cứu:",
        len(cau_hinh["cau_hoi_nghien_cuu"]),
    )

    cau_hinh_du_lieu = cau_hinh["cau_hinh_du_lieu"]

    print(
        "Bộ dữ liệu chuẩn:",
        cau_hinh_du_lieu["bo_du_lieu_truyen_dan"]["ten"],
    )

    print(
        "Đường dẫn dữ liệu chuẩn:",
        cau_hinh_du_lieu["bo_du_lieu_truyen_dan"]["duong_dan"],
    )

    print(
        "Bộ dữ liệu học máy:",
        cau_hinh_du_lieu["bo_du_lieu_hoc_may"]["ten"],
    )

    print(
        "Mô hình kinh tế lượng:",
        cau_hinh["mo_hinh"]["kinh_te_luong_co_so"],
        "và",
        cau_hinh["mo_hinh"]["kinh_te_luong_mo_rong"],
    )

    print(
        "Mô hình học máy:",
        cau_hinh["mo_hinh"]["hoc_may_co_so"],
        "và",
        cau_hinh["mo_hinh"]["hoc_may_phi_tuyen"],
    )

    print(
        "Chân trời dự báo:",
        ", ".join(
            f"{ngay} ngày"
            for ngay in cau_hinh["du_bao_rui_ro"]["chan_du_bao_ngay"]
        ),
    )


if __name__ == "__main__":
    main()
