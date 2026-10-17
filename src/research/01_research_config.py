
import json
from pathlib import Path
from datetime import datetime


# Xác định thư mục gốc của dự án
THU_MUC_DU_AN = Path(__file__).resolve().parents[2]

# Đường dẫn đến file cấu hình nghiên cứu
DUONG_DAN_CAU_HINH = (
    THU_MUC_DU_AN / "config" / "research_config.json"
)


def doc_cau_hinh():
    """Đọc cấu hình nghiên cứu từ file JSON."""

    if not DUONG_DAN_CAU_HINH.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file cấu hình: {DUONG_DAN_CAU_HINH}"
        )

    with open(DUONG_DAN_CAU_HINH, "r", encoding="utf-8") as tep:
        return json.load(tep)


def kiem_tra_cau_hinh(cau_hinh):
    """Kiểm tra các thông tin quan trọng của nghiên cứu."""

    cac_muc_bat_buoc = [
        "de_tai",
        "tai_san_nghien_cuu",
        "bien_nghien_cuu",
        "cau_hoi_nghien_cuu",
        "mo_hinh",
        "danh_gia",
    ]

    for muc in cac_muc_bat_buoc:
        if muc not in cau_hinh:
            raise ValueError(f"Cấu hình còn thiếu mục: {muc}")

    cau_hoi = cau_hinh["cau_hoi_nghien_cuu"]

    for ma_cau_hoi in ["RQ1", "RQ2", "RQ3", "RQ4", "RQ5"]:
        if ma_cau_hoi not in cau_hoi:
            raise ValueError(
                f"Cấu hình còn thiếu câu hỏi: {ma_cau_hoi}"
            )

    tai_san = cau_hinh["tai_san_nghien_cuu"]["ma_tien_ma_hoa"]

    for ma_yeu_cau in ["BTC", "ETH"]:
        if not any(
            ma.startswith(ma_yeu_cau) for ma in tai_san
        ):
            raise ValueError(
                f"Nghiên cứu phải có mã tiền mã hóa {ma_yeu_cau}."
            )

    try:
        ngay_bat_dau = datetime.strptime(
            cau_hinh["de_tai"]["ngay_bat_dau"], "%Y-%m-%d"
        )
        ngay_ket_thuc = datetime.strptime(
            cau_hinh["de_tai"]["ngay_ket_thuc"], "%Y-%m-%d"
        )
    except (KeyError, TypeError, ValueError) as loi:
        raise ValueError(
            "Ngày nghiên cứu phải đúng định dạng YYYY-MM-DD "
            "và là ngày hợp lệ."
        ) from loi

    if ngay_bat_dau >= ngay_ket_thuc:
        raise ValueError(
            "Ngày bắt đầu phải trước ngày kết thúc."
        )

    return True


def main():
    """Đọc, kiểm tra và in thông tin nghiên cứu."""

    cau_hinh = doc_cau_hinh()
    kiem_tra_cau_hinh(cau_hinh)

    print("Đọc cấu hình thành công!")
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


if __name__ == "__main__":
    main()
