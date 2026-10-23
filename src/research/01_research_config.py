
import json
from pathlib import Path
from datetime import datetime


# ============================================================
# 1. XÁC ĐỊNH ĐƯỜNG DẪN
# ============================================================

# Xác định thư mục gốc của dự án
THU_MUC_DU_AN = Path(__file__).resolve().parents[2]

# Đường dẫn file cấu hình nghiên cứu
DUONG_DAN_CAU_HINH = (
    THU_MUC_DU_AN / "config" / "research_config.json"
)


# ============================================================
# 2. ĐỌC FILE JSON
# ============================================================

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
            cau_hinh = json.load(tep)

    except json.JSONDecodeError as loi:
        raise ValueError(
            f"File JSON không đúng định dạng: {loi}"
        ) from loi

    if not isinstance(cau_hinh, dict):
        raise ValueError(
            "Nội dung file JSON phải là một đối tượng."
        )

    return cau_hinh


# ============================================================
# 3. HÀM HỖ TRỢ KIỂM TRA CẤU HÌNH
# ============================================================

def yeu_cau_muc(cau_hinh, duong_dan):
    """
    Lấy một mục trong cấu hình theo đường dẫn khóa.
    Ví dụ: ['de_tai', 'ngay_bat_dau'].
    """

    gia_tri = cau_hinh

    for khoa in duong_dan:
        if not isinstance(gia_tri, dict) or khoa not in gia_tri:
            ten_muc = ".".join(duong_dan)
            raise ValueError(
                f"Cấu hình còn thiếu mục: {ten_muc}"
            )

        gia_tri = gia_tri[khoa]

    return gia_tri


def kiem_tra_gia_tri(cau_hinh, duong_dan, gia_tri_mong_doi):
    """Kiểm tra một khóa có đúng giá trị yêu cầu hay không."""

    gia_tri_thuc_te = yeu_cau_muc(cau_hinh, duong_dan)

    if gia_tri_thuc_te != gia_tri_mong_doi:
        ten_muc = ".".join(duong_dan)
        raise ValueError(
            f"{ten_muc} không đúng. "
            f"Yêu cầu: {gia_tri_mong_doi}; "
            f"thực tế: {gia_tri_thuc_te}"
        )


# ============================================================
# 4. KIỂM TRA TOÀN BỘ CẤU HÌNH
# ============================================================

def kiem_tra_cau_hinh(cau_hinh):
    """Kiểm tra cấu trúc và tính nhất quán của cấu hình."""

    # --------------------------------------------------------
    # 4.1. Các mục cấp cao bắt buộc
    # --------------------------------------------------------

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
            raise ValueError(
                f"Cấu hình còn thiếu mục: {muc}"
            )

    # --------------------------------------------------------
    # 4.2. Kiểm tra thời gian nghiên cứu
    # --------------------------------------------------------

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
        raise ValueError(
            "Ngày bắt đầu phải trước ngày kết thúc."
        )

    if de_tai["ngay_bat_dau"] != "2018-01-01":
        raise ValueError(
            "Ngày bắt đầu phải là 2018-01-01."
        )

    if de_tai["ngay_ket_thuc"] != "2025-12-31":
        raise ValueError(
            "Ngày kết thúc phải là 2025-12-31."
        )

    if de_tai.get("mui_gio") != "UTC":
        raise ValueError(
            "Múi giờ nghiên cứu phải là UTC."
        )

    if de_tai.get("tan_suat_du_lieu") != "hang_ngay":
        raise ValueError(
            "Tần suất dữ liệu nghiên cứu phải là hàng ngày."
        )

    # --------------------------------------------------------
    # 4.3. Kiểm tra tài sản nghiên cứu
    # --------------------------------------------------------

    tai_san = cau_hinh["tai_san_nghien_cuu"]

    if not all(
        ma in tai_san.get("ma_tien_ma_hoa", [])
        for ma in ["BTC", "ETH"]
    ):
        raise ValueError(
            "Nghiên cứu phải có cả BTC và ETH."
        )

    if not all(
        ma in tai_san.get("ma_gia", [])
        for ma in ["BTC-USD", "ETH-USD"]
    ):
        raise ValueError(
            "Mã giá phải có BTC-USD và ETH-USD."
        )

    # --------------------------------------------------------
    # 4.4. Kiểm tra câu hỏi nghiên cứu
    # --------------------------------------------------------

    cau_hoi = cau_hinh["cau_hoi_nghien_cuu"]

    for ma_cau_hoi in [
        "RQ1", "RQ2", "RQ3", "RQ4", "RQ5"
    ]:
        if ma_cau_hoi not in cau_hoi:
            raise ValueError(
                f"Cấu hình còn thiếu câu hỏi: {ma_cau_hoi}"
            )

    # --------------------------------------------------------
    # 4.5. Kiểm tra các biến và công thức biến đổi
    # --------------------------------------------------------

    bien = cau_hinh["bien_nghien_cuu"]

    cac_bien_bat_buoc = [
        "gia_tien_ma_hoa",
        "loi_suat_trai_phieu_2_nam_my",
        "chi_so_dong_usd",
        "chi_so_bien_dong_vix",
    ]

    for ten_bien in cac_bien_bat_buoc:
        if ten_bien not in bien:
            raise ValueError(
                f"Cấu hình còn thiếu biến nghiên cứu: {ten_bien}"
            )

    kiem_tra_gia_tri(
        cau_hinh,
        ["bien_nghien_cuu", "gia_tien_ma_hoa",
         "cong_thuc_loi_suat"],
        "100 * ln(P_t / P_t_1)"
    )

    kiem_tra_gia_tri(
        cau_hinh,
        ["bien_nghien_cuu", "loi_suat_trai_phieu_2_nam_my",
         "cach_bien_doi"],
        "sai_phan_bac_mot"
    )

    kiem_tra_gia_tri(
        cau_hinh,
        ["bien_nghien_cuu", "loi_suat_trai_phieu_2_nam_my",
         "cong_thuc"],
        "US2Y_t - US2Y_t_1"
    )

    kiem_tra_gia_tri(
        cau_hinh,
        ["bien_nghien_cuu", "chi_so_dong_usd",
         "cach_bien_doi"],
        "sai_phan_logarit"
    )

    kiem_tra_gia_tri(
        cau_hinh,
        ["bien_nghien_cuu", "chi_so_dong_usd",
         "cong_thuc"],
        "100 * ln(DXY_t / DXY_t_1)"
    )

    kiem_tra_gia_tri(
        cau_hinh,
        ["bien_nghien_cuu", "chi_so_bien_dong_vix",
         "cach_bien_doi"],
        "sai_phan_bac_mot"
    )

    kiem_tra_gia_tri(
        cau_hinh,
        ["bien_nghien_cuu", "chi_so_bien_dong_vix",
         "cong_thuc"],
        "VIX_t - VIX_t_1"
    )

    # --------------------------------------------------------
    # 4.6. Kiểm tra hai bộ dữ liệu
    # --------------------------------------------------------

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
            "duong_dan",
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

        if not isinstance(bo_du_lieu["quy_tac"], list):
            raise ValueError(
                f"Quy tắc của {ten_bo} phải là danh sách."
            )

        if not bo_du_lieu["quy_tac"]:
            raise ValueError(
                f"Bộ dữ liệu {ten_bo} chưa có quy tắc."
            )

    # Kiểm tra model_dataset
    bo_truyen_dan = cau_hinh_du_lieu["bo_du_lieu_truyen_dan"]

    kiem_tra_gia_tri(
        cau_hinh,
        ["cau_hinh_du_lieu", "bo_du_lieu_truyen_dan", "ten"],
        "model_dataset"
    )

    kiem_tra_gia_tri(
        cau_hinh,
        ["cau_hinh_du_lieu", "bo_du_lieu_truyen_dan",
         "duong_dan"],
        "data/processed/model_dataset.csv"
    )

    kiem_tra_gia_tri(
        cau_hinh,
        ["cau_hinh_du_lieu", "bo_du_lieu_truyen_dan",
         "lich_du_lieu"],
        "tat_ca_cac_ngay_UTC"
    )

    for ma in ["BTC", "ETH", "US2Y", "DXY", "VIX"]:
        if ma not in bo_truyen_dan.get("tai_san", []):
            raise ValueError(
                f"model_dataset còn thiếu biến: {ma}"
            )

    # Kiểm tra ml_dataset
    bo_hoc_may = cau_hinh_du_lieu["bo_du_lieu_hoc_may"]

    kiem_tra_gia_tri(
        cau_hinh,
        ["cau_hinh_du_lieu", "bo_du_lieu_hoc_may", "ten"],
        "ml_dataset"
    )

    kiem_tra_gia_tri(
        cau_hinh,
        ["cau_hinh_du_lieu", "bo_du_lieu_hoc_may",
         "duong_dan"],
        "data/processed/ml_dataset.csv"
    )

    kiem_tra_gia_tri(
        cau_hinh,
        ["cau_hinh_du_lieu", "bo_du_lieu_hoc_may",
         "lich_du_lieu"],
        "tat_ca_cac_ngay_UTC"
    )

    for ma in ["BTC", "ETH"]:
        if ma not in bo_hoc_may.get("tai_san", []):
            raise ValueError(
                f"ml_dataset còn thiếu tài sản: {ma}"
            )

    # --------------------------------------------------------
    # 4.7. Kiểm tra phân công thành viên
    # --------------------------------------------------------

    thanh_vien = cau_hinh_du_lieu.get(
        "thanh_vien_su_dung", {}
    )

    for ten_tv, thong_tin in thanh_vien.items():
        if not isinstance(thong_tin, dict):
            raise ValueError(
                f"Thông tin phân công của {ten_tv} không hợp lệ."
            )

        if not thong_tin.get("file_dau_vao"):
            raise ValueError(
                f"Phân công của {ten_tv} chưa có file đầu vào."
            )

        if not isinstance(thong_tin.get("quy_tac"), list):
            raise ValueError(
                f"Quy tắc phân công của {ten_tv} phải là danh sách."
            )

    # --------------------------------------------------------
    # 4.8. Kiểm tra trạng thái thị trường
    # --------------------------------------------------------

    trang_thai = cau_hinh["trang_thai_thi_truong"]

    if trang_thai.get("cach_xac_dinh_trang_thai") != "nguong_co_dinh":
        raise ValueError(
            "Cách xác định trạng thái phải là nguong_co_dinh."
        )

    if trang_thai.get("bien_dai_dien_cang_thang") != "VIX":
        raise ValueError(
            "Biến đại diện trạng thái căng thẳng phải là VIX."
        )

    if trang_thai.get("nguong_stress_co_so") != 30:
        raise ValueError(
            "Ngưỡng Stress cơ sở phải bằng 30 điểm VIX."
        )

    if trang_thai.get("nguong_stress_kiem_tra_do_nhay") != [25, 35]:
        raise ValueError(
            "Ngưỡng kiểm tra độ nhạy phải là [25, 35]."
        )

    if trang_thai.get("do_tre_vix") != 1:
        raise ValueError(
            "Cấu hình hiện tại yêu cầu do_tre_vix = 1."
        )

    if trang_thai.get("don_vi_do_tre") != "phien_quan_sat_vix":
        raise ValueError(
            "Đơn vị độ trễ VIX phải là phien_quan_sat_vix."
        )

    if trang_thai.get("moc_thay_doi_co_cau") != "2020-01-01":
        raise ValueError(
            "Mốc phân chia trước/sau năm 2020 không đúng."
        )

    # --------------------------------------------------------
    # 4.9. Kiểm tra mục tiêu dự báo rủi ro
    # --------------------------------------------------------

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
            "Chân trời dự báo hiện tại phải là [1]."
        )

    kiem_tra_gia_tri(
        cau_hinh,
        ["du_bao_rui_ro", "bien_muc_tieu"],
        "gia_tri_tuyet_doi_loi_suat_log_ngay_tiep_theo"
    )

    kiem_tra_gia_tri(
        cau_hinh,
        ["du_bao_rui_ro", "cach_tinh"],
        "abs(100 * ln(P_t_cong_1 / P_t))"
    )

    if du_bao.get("don_vi") != "phan_tram":
        raise ValueError(
            "Đơn vị biến mục tiêu phải là phần trăm."
        )

    # --------------------------------------------------------
    # 4.10. Kiểm tra mô hình nghiên cứu
    # --------------------------------------------------------

    mo_hinh = cau_hinh["mo_hinh"]

    cac_mo_hinh_bat_buoc = [
        "kinh_te_luong_co_so",
        "kinh_te_luong_mo_rong",
        "hoc_may_co_so",
        "hoc_may_phi_tuyen",
        "phan_tach_muc_tieu",
        "luu_y",
    ]

    for ten_mo_hinh in cac_mo_hinh_bat_buoc:
        if ten_mo_hinh not in mo_hinh:
            raise ValueError(
                f"Cấu hình còn thiếu mục mô hình: {ten_mo_hinh}"
            )

    if not isinstance(mo_hinh["phan_tach_muc_tieu"], dict):
        raise ValueError(
            "phan_tach_muc_tieu phải là một đối tượng."
        )

    if not isinstance(mo_hinh["luu_y"], list):
        raise ValueError(
            "Các lưu ý mô hình phải được khai báo dưới dạng danh sách."
        )

    # --------------------------------------------------------
    # 4.11. Kiểm tra đánh giá ngoài mẫu
    # --------------------------------------------------------

    danh_gia = cau_hinh["danh_gia"]

    if danh_gia.get("phuong_phap_kiem_dinh") != "rolling_origin":
        raise ValueError(
            "Phương pháp kiểm định phải là rolling_origin."
        )

    if not danh_gia.get("bat_buoc_kiem_dinh_ngoai_mau", False):
        raise ValueError(
            "Nghiên cứu phải bật kiểm định ngoài mẫu."
        )

    if not danh_gia.get("chia_du_lieu_theo_thoi_gian", False):
        raise ValueError(
            "Phải chia dữ liệu theo thứ tự thời gian."
        )

    if not danh_gia.get("tranh_ro_ri_du_lieu", False):
        raise ValueError(
            "Phải bật kiểm soát rò rỉ dữ liệu."
        )

    if danh_gia.get("thuoc_do_du_bao") != ["MAE", "RMSE"]:
        raise ValueError(
            "Thước đo dự báo phải gồm MAE và RMSE."
        )

    if not danh_gia.get(
        "so_sanh_mo_hinh_co_so_va_mo_hinh_bo_sung_bien_vi_mo",
        False
    ):
        raise ValueError(
            "Phải bật so sánh mô hình cơ sở và mô hình bổ sung biến vĩ mô."
        )

    cac_quy_tac_danh_gia = danh_gia.get("quy_tac", [])

    if not isinstance(cac_quy_tac_danh_gia, list):
        raise ValueError(
            "Quy tắc đánh giá phải là một danh sách."
        )

    # --------------------------------------------------------
    # 4.12. Kiểm tra các cờ kiểm soát chất lượng
    # --------------------------------------------------------

    kiem_soat = cau_hinh["kiem_soat_chat_luong_du_lieu"]

    cac_co_bat_buoc = [
        "kiem_tra_trung_ngay",
        "kiem_tra_gia_tri_thieu",
        "kiem_tra_gia_tri_khong_hop_le",
        "kiem_tra_mui_gio",
        "kiem_tra_thu_tu_thoi_gian",
        "khong_dien_du_lieu_tuong_lai",
        "ghi_nhan_so_quan_sat_bi_loai",
        "ghi_nhan_nguon_va_thoi_diem_tai_du_lieu",
    ]

    for ten_co in cac_co_bat_buoc:
        if kiem_soat.get(ten_co) is not True:
            raise ValueError(
                f"Cờ kiểm soát chất lượng phải được bật: {ten_co}"
            )

    return True


# ============================================================
# 5. CHẠY CHƯƠNG TRÌNH
# ============================================================

def main():
    """Đọc, kiểm tra và in thông tin nghiên cứu."""

    cau_hinh = doc_cau_hinh()
    kiem_tra_cau_hinh(cau_hinh)

    print("=" * 60)
    print("ĐỌC VÀ KIỂM TRA CẤU HÌNH THÀNH CÔNG")
    print("=" * 60)

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
        "Đường dẫn dữ liệu học máy:",
        cau_hinh_du_lieu["bo_du_lieu_hoc_may"]["duong_dan"],
    )

    print(
        "Ngưỡng Stress VIX:",
        cau_hinh["trang_thai_thi_truong"]["nguong_stress_co_so"],
    )

    print(
        "Ngưỡng kiểm tra độ nhạy:",
        cau_hinh["trang_thai_thi_truong"][
            "nguong_stress_kiem_tra_do_nhay"
        ],
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

    print(
        "Thước đo đánh giá:",
        ", ".join(cau_hinh["danh_gia"]["thuoc_do_du_bao"]),
    )

    print("=" * 60)
    print("Tất cả kiểm tra cấu hình đều đạt.")
    print("Lưu ý: đây chưa phải kiểm định chất lượng dữ liệu thực tế.")


if __name__ == "__main__":
    main()
