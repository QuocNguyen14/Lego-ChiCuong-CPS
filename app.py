import streamlit as st
import time
import random
import pandas as pd
from datetime import datetime
from PIL import Image, ImageDraw

# =========================================================
# 1. CẤU HÌNH TRANG
# =========================================================
st.set_page_config(
    page_title="Dashboard giám sát dây chuyền sản xuất LEGO",
    page_icon="🏭",
    layout="wide"
)

# =========================================================
# 2. THAM CHIẾU VẤN ĐỀ 1
# =========================================================
optimal_inputs = {
    "Nhiệt độ khuôn (°C)": 220.0,
    "Áp suất phun (MPa)": 95.0,
    "Áp suất kẹp khuôn (tấn)": 65.0,
    "Thời gian làm nguội (s)": 18.0
}

optimal_outputs = {
    "Sai lệch chiều dài (mm)": 0.006,
    "Sai lệch chiều rộng (mm)": 0.005,
    "Sai lệch chiều cao (mm)": 0.004,
    "Độ cong vênh (mm)": 0.010
}

safe_limits_v1 = {
    "Nhiệt độ khuôn (°C)": (215.0, 225.0),
    "Áp suất phun (MPa)": (92.0, 98.0),
    "Áp suất kẹp khuôn (tấn)": (63.0, 67.0),
    "Thời gian làm nguội (s)": (17.0, 19.0),
    "Sai lệch chiều dài (mm)": (0.000, 0.050),
    "Sai lệch chiều rộng (mm)": (0.000, 0.050),
    "Sai lệch chiều cao (mm)": (0.000, 0.050),
    "Độ cong vênh (mm)": (0.000, 0.100)
}

safe_random_zone_v1 = {
    "Nhiệt độ khuôn (°C)": (217.0, 223.0),
    "Áp suất phun (MPa)": (93.0, 97.0),
    "Áp suất kẹp khuôn (tấn)": (63.5, 66.5),
    "Thời gian làm nguội (s)": (17.3, 18.7),
    "Sai lệch chiều dài (mm)": (0.003, 0.020),
    "Sai lệch chiều rộng (mm)": (0.003, 0.020),
    "Sai lệch chiều cao (mm)": (0.002, 0.018),
    "Độ cong vênh (mm)": (0.008, 0.040)
}

# =========================================================
# 3. THAM CHIẾU VẤN ĐỀ 2
# =========================================================
problem2_status_map = {
    "cluster_1": "Hoạt động bình thường",
    "cluster_2": "Có dấu hiệu mài mòn",
    "cluster_3": "Cảnh báo hỏng hóc nghiêm trọng"
}

problem2_clusters = {
    "cluster_1": {
        "Độ rung của khuôn (mm/s)": (1.0, 2.2),
        "Độ sụt áp kẹp (%)": (0.5, 1.5),
        "Điện năng tiêu thụ động cơ (kWh)": (16.0, 20.0),
        "Tổng số chu kỳ ép": (1000, 12000)
    },
    "cluster_2": {
        "Độ rung của khuôn (mm/s)": (2.3, 4.5),
        "Độ sụt áp kẹp (%)": (1.6, 3.5),
        "Điện năng tiêu thụ động cơ (kWh)": (20.1, 24.0),
        "Tổng số chu kỳ ép": (12001, 30000)
    },
    "cluster_3": {
        "Độ rung của khuôn (mm/s)": (4.6, 7.5),
        "Độ sụt áp kẹp (%)": (3.6, 6.0),
        "Điện năng tiêu thụ động cơ (kWh)": (24.1, 30.0),
        "Tổng số chu kỳ ép": (30001, 60000)
    }
}

# =========================================================
# 4. THAM CHIẾU VẤN ĐỀ 3
# =========================================================
CLASS_NAMES = ["OK", "Bavia", "Khuyết", "Xước"]

CLASS_COLORS = {
    "OK": "#16a34a",
    "Bavia": "#dc2626",
    "Khuyết": "#f59e0b",
    "Xước": "#2563eb"
}

# =========================================================
# 5. HÀM CHUNG
# =========================================================
def hien_thi_metric(col, title, value, unit="", safe_text="Bình thường", alert_text="Cảnh báo", is_safe=True):
    delta_text = safe_text if is_safe else alert_text
    color_mode = "normal" if is_safe else "inverse"

    if isinstance(value, int):
        display_val = f"{value:,} {unit}".strip()
    elif isinstance(value, float):
        if unit in ["mm", "mm/s", "%"]:
            display_val = f"{value:.2f} {unit}".strip()
        else:
            display_val = f"{value:.1f} {unit}".strip()
    else:
        display_val = str(value)

    col.metric(title, display_val, delta_text, delta_color=color_mode)

# =========================================================
# 6. HÀM VẤN ĐỀ 1
# =========================================================
def generate_safe_data_v1():
    return {
        "Nhiệt độ khuôn (°C)": round(random.uniform(*safe_random_zone_v1["Nhiệt độ khuôn (°C)"]), 1),
        "Áp suất phun (MPa)": round(random.uniform(*safe_random_zone_v1["Áp suất phun (MPa)"]), 1),
        "Áp suất kẹp khuôn (tấn)": round(random.uniform(*safe_random_zone_v1["Áp suất kẹp khuôn (tấn)"]), 1),
        "Thời gian làm nguội (s)": round(random.uniform(*safe_random_zone_v1["Thời gian làm nguội (s)"]), 1),
        "Sai lệch chiều dài (mm)": round(random.uniform(*safe_random_zone_v1["Sai lệch chiều dài (mm)"]), 3),
        "Sai lệch chiều rộng (mm)": round(random.uniform(*safe_random_zone_v1["Sai lệch chiều rộng (mm)"]), 3),
        "Sai lệch chiều cao (mm)": round(random.uniform(*safe_random_zone_v1["Sai lệch chiều cao (mm)"]), 3),
        "Độ cong vênh (mm)": round(random.uniform(*safe_random_zone_v1["Độ cong vênh (mm)"]), 3),
    }

def is_out_of_safe_range_v1(param_name, value):
    min_val, max_val = safe_limits_v1[param_name]
    return value < min_val or value > max_val

def count_warnings_v1(sensor_dict):
    total = 0
    for key, value in sensor_dict.items():
        if is_out_of_safe_range_v1(key, value):
            total += 1
    return total

def apply_optimal_parameters_v1():
    st.session_state.problem1["Nhiệt độ khuôn (°C)"] = optimal_inputs["Nhiệt độ khuôn (°C)"]
    st.session_state.problem1["Áp suất phun (MPa)"] = optimal_inputs["Áp suất phun (MPa)"]
    st.session_state.problem1["Áp suất kẹp khuôn (tấn)"] = optimal_inputs["Áp suất kẹp khuôn (tấn)"]
    st.session_state.problem1["Thời gian làm nguội (s)"] = optimal_inputs["Thời gian làm nguội (s)"]
    st.session_state.problem1["Sai lệch chiều dài (mm)"] = optimal_outputs["Sai lệch chiều dài (mm)"]
    st.session_state.problem1["Sai lệch chiều rộng (mm)"] = optimal_outputs["Sai lệch chiều rộng (mm)"]
    st.session_state.problem1["Sai lệch chiều cao (mm)"] = optimal_outputs["Sai lệch chiều cao (mm)"]
    st.session_state.problem1["Độ cong vênh (mm)"] = optimal_outputs["Độ cong vênh (mm)"]
    st.session_state.show_optimization_result = True
    st.session_state.manual_override_active_v1 = False
    st.session_state.overlay_bi_tat_v1 = False

def restore_safe_operation_v1():
    st.session_state.problem1 = generate_safe_data_v1()
    st.session_state.manual_override_active_v1 = False
    st.session_state.show_optimization_result = False
    st.session_state.overlay_bi_tat_v1 = True

@st.dialog("🚨 CẢNH BÁO HỆ THỐNG - VẤN ĐỀ 1", width="large")
def hien_thi_overlay_nguy_hiem_v1(so_loi):
    st.markdown(
        f"""
        <div style="text-align: center; padding: 10px 20px;">
            <h1 style="color: #FF0000; font-size: 52px;">⚠️</h1>
            <h2 style="color: #FF0000; font-weight: bold;">
                PHÁT HIỆN {so_loi} THÔNG SỐ VƯỢT NGƯỠNG AN TOÀN
            </h2>
            <p style="font-size: 18px; color: #333;">
                Vui lòng kiểm tra hệ thống ép phun ngay lập tức
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Đóng thông báo", use_container_width=True):
        restore_safe_operation_v1()
        st.rerun()

def render_problem1():
    so_canh_bao = count_warnings_v1(st.session_state.problem1)

    if so_canh_bao == 0:
        st.session_state.overlay_bi_tat_v1 = False
        st.session_state.manual_override_active_v1 = False

    if so_canh_bao > st.session_state.last_so_canh_bao_v1:
        st.session_state.overlay_bi_tat_v1 = False

    st.session_state.last_so_canh_bao_v1 = so_canh_bao

    if so_canh_bao > 0 and not st.session_state.overlay_bi_tat_v1:
        hien_thi_overlay_nguy_hiem_v1(so_canh_bao)

    st.markdown("## Vấn đề 1")
    st.markdown("### Tối ưu chất lượng sản phẩm ép phun")

    if st.session_state.show_optimization_result:
        st.success(
            "✅ Bộ thông số tối ưu: Nhiệt độ khuôn = 220°C, Áp suất phun = 95 MPa, "
            "Áp suất kẹp khuôn = 65 tấn, Thời gian làm nguội = 18 s."
        )

    k1, k2, k3 = st.columns(3)
    k1.metric("Sản lượng", f"{st.session_state.san_luong_v1:,} sản phẩm")
    k2.metric("Tỷ lệ đạt", f"{st.session_state.ty_le_dat_v1} %")
    if so_canh_bao == 0:
        k3.metric("Cảnh báo", "0 thông số", delta="AN TOÀN")
    else:
        k3.metric("Cảnh báo", f"{so_canh_bao} thông số", delta="VƯỢT NGƯỠNG", delta_color="inverse")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        hien_thi_metric(st, "Nhiệt độ khuôn", st.session_state.problem1["Nhiệt độ khuôn (°C)"], "°C",
                        "Trong ngưỡng an toàn", "Vượt ngưỡng an toàn",
                        not is_out_of_safe_range_v1("Nhiệt độ khuôn (°C)", st.session_state.problem1["Nhiệt độ khuôn (°C)"]))
        hien_thi_metric(st, "Áp suất phun", st.session_state.problem1["Áp suất phun (MPa)"], "MPa",
                        "Trong ngưỡng an toàn", "Vượt ngưỡng an toàn",
                        not is_out_of_safe_range_v1("Áp suất phun (MPa)", st.session_state.problem1["Áp suất phun (MPa)"]))
        hien_thi_metric(st, "Sai lệch chiều dài", st.session_state.problem1["Sai lệch chiều dài (mm)"], "mm",
                        "Trong ngưỡng an toàn", "Vượt ngưỡng an toàn",
                        not is_out_of_safe_range_v1("Sai lệch chiều dài (mm)", st.session_state.problem1["Sai lệch chiều dài (mm)"]))
        hien_thi_metric(st, "Sai lệch chiều rộng", st.session_state.problem1["Sai lệch chiều rộng (mm)"], "mm",
                        "Trong ngưỡng an toàn", "Vượt ngưỡng an toàn",
                        not is_out_of_safe_range_v1("Sai lệch chiều rộng (mm)", st.session_state.problem1["Sai lệch chiều rộng (mm)"]))

    with col2:
        hien_thi_metric(st, "Áp suất kẹp khuôn", st.session_state.problem1["Áp suất kẹp khuôn (tấn)"], "tấn",
                        "Trong ngưỡng an toàn", "Vượt ngưỡng an toàn",
                        not is_out_of_safe_range_v1("Áp suất kẹp khuôn (tấn)", st.session_state.problem1["Áp suất kẹp khuôn (tấn)"]))
        hien_thi_metric(st, "Thời gian làm nguội", st.session_state.problem1["Thời gian làm nguội (s)"], "s",
                        "Trong ngưỡng an toàn", "Vượt ngưỡng an toàn",
                        not is_out_of_safe_range_v1("Thời gian làm nguội (s)", st.session_state.problem1["Thời gian làm nguội (s)"]))
        hien_thi_metric(st, "Sai lệch chiều cao", st.session_state.problem1["Sai lệch chiều cao (mm)"], "mm",
                        "Trong ngưỡng an toàn", "Vượt ngưỡng an toàn",
                        not is_out_of_safe_range_v1("Sai lệch chiều cao (mm)", st.session_state.problem1["Sai lệch chiều cao (mm)"]))
        hien_thi_metric(st, "Độ cong vênh", st.session_state.problem1["Độ cong vênh (mm)"], "mm",
                        "Trong ngưỡng an toàn", "Vượt ngưỡng an toàn",
                        not is_out_of_safe_range_v1("Độ cong vênh (mm)", st.session_state.problem1["Độ cong vênh (mm)"]))

    st.markdown("---")
    info1, info2 = st.columns(2)
    with info1:
        st.info(
            "Thuật toán mô hình hóa: Random Forest\n\n"
            "Đầu vào: Nhiệt độ khuôn, Áp suất phun, Áp suất kẹp khuôn, Thời gian làm nguội\n\n"
            "Đầu ra: Sai lệch chiều dài, Sai lệch chiều rộng, Sai lệch chiều cao, Độ cong vênh"
        )
    with info2:
        st.info(
            "Grid Search tìm được bộ tối ưu:\n\n"
            "- Nhiệt độ khuôn: 220°C\n"
            "- Áp suất phun: 95 MPa\n"
            "- Áp suất kẹp khuôn: 65 tấn\n"
            "- Thời gian làm nguội: 18 s\n\n"
            "Độ chính xác mô hình: MAE = 0.006 mm | R² = 0.904"
        )

# =========================================================
# 7. HÀM VẤN ĐỀ 2
# =========================================================
def generate_problem2_data():
    cluster_key = random.choice(["cluster_1", "cluster_2", "cluster_3"])
    cluster = problem2_clusters[cluster_key]
    return {
        "Độ rung của khuôn (mm/s)": round(random.uniform(*cluster["Độ rung của khuôn (mm/s)"]), 2),
        "Độ sụt áp kẹp (%)": round(random.uniform(*cluster["Độ sụt áp kẹp (%)"]), 2),
        "Điện năng tiêu thụ động cơ (kWh)": round(random.uniform(*cluster["Điện năng tiêu thụ động cơ (kWh)"]), 2),
        "Tổng số chu kỳ ép": random.randint(*cluster["Tổng số chu kỳ ép"]),
        "Trạng thái máy": problem2_status_map[cluster_key]
    }

def save_problem2_history():
    row = {
        "Thời gian": datetime.now().strftime("%H:%M:%S"),
        "Độ rung khuôn (mm/s)": st.session_state.problem2["Độ rung của khuôn (mm/s)"],
        "Độ sụt áp kẹp (%)": st.session_state.problem2["Độ sụt áp kẹp (%)"],
        "Điện năng động cơ (kWh)": st.session_state.problem2["Điện năng tiêu thụ động cơ (kWh)"],
        "Tổng số chu kỳ ép": st.session_state.problem2["Tổng số chu kỳ ép"],
        "Trạng thái máy": st.session_state.problem2["Trạng thái máy"]
    }
    st.session_state.history_problem2.insert(0, row)
    st.session_state.history_problem2 = st.session_state.history_problem2[:20]

def color_trang_thai_p2(val):
    if val == "Hoạt động bình thường":
        return "background-color: #d4edda; color: #155724; font-weight: 600;"
    elif val == "Có dấu hiệu mài mòn":
        return "background-color: #fff3cd; color: #856404; font-weight: 600;"
    elif val == "Cảnh báo hỏng hóc nghiêm trọng":
        return "background-color: #f8d7da; color: #721c24; font-weight: 600;"
    return ""

def render_problem2():
    st.markdown("## Vấn đề 2")
    st.markdown("### Bảo trì dự đoán cho hệ thống khuôn và trục vít")

    k1, k2, k3 = st.columns(3)
    k1.metric("Độ rung khuôn", f'{st.session_state.problem2["Độ rung của khuôn (mm/s)"]:.2f} mm/s')
    k2.metric("Điện năng động cơ", f'{st.session_state.problem2["Điện năng tiêu thụ động cơ (kWh)"]:.2f} kWh')
    k3.metric("Trạng thái máy", st.session_state.problem2["Trạng thái máy"])

    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        hien_thi_metric(st, "Độ rung của khuôn", st.session_state.problem2["Độ rung của khuôn (mm/s)"], "mm/s",
                        "Theo dõi bình thường", "Biến động cao",
                        st.session_state.problem2["Trạng thái máy"] == "Hoạt động bình thường")
        hien_thi_metric(st, "Độ sụt áp kẹp", st.session_state.problem2["Độ sụt áp kẹp (%)"], "%",
                        "Theo dõi bình thường", "Sụt áp tăng",
                        st.session_state.problem2["Trạng thái máy"] == "Hoạt động bình thường")
    with c2:
        hien_thi_metric(st, "Điện năng tiêu thụ động cơ", st.session_state.problem2["Điện năng tiêu thụ động cơ (kWh)"], "kWh",
                        "Theo dõi bình thường", "Tiêu thụ tăng",
                        st.session_state.problem2["Trạng thái máy"] == "Hoạt động bình thường")
        hien_thi_metric(st, "Tổng số chu kỳ ép", st.session_state.problem2["Tổng số chu kỳ ép"], "",
                        "Theo dõi bình thường", "Chu kỳ cao",
                        st.session_state.problem2["Trạng thái máy"] == "Hoạt động bình thường")

    st.markdown("---")
    trang_thai = st.session_state.problem2["Trạng thái máy"]
    if trang_thai == "Hoạt động bình thường":
        st.success("Mức 1 - Hoạt động bình thường: Hệ thống đang vận hành ổn định.")
    elif trang_thai == "Có dấu hiệu mài mòn":
        st.warning("Mức 2 - Có dấu hiệu mài mòn: Nên kiểm tra và lên kế hoạch bảo trì.")
    else:
        st.error("Mức 3 - Cảnh báo hỏng hóc nghiêm trọng: Cần dừng máy để kiểm tra khẩn cấp.")

    info1, info2 = st.columns(2)
    with info1:
        st.info(
            "Thuật toán sử dụng: K-means Clustering\n\n"
            "Số cụm: 3\n\n"
            "Đầu vào: Độ rung khuôn, Độ sụt áp kẹp, Điện năng tiêu thụ động cơ, Tổng số chu kỳ ép\n\n"
            "Đầu ra: 3 mức trạng thái thiết bị"
        )
    with info2:
        st.info(
            "3 mức phân loại:\n\n"
            "- Mức 1: Hoạt động bình thường\n"
            "- Mức 2: Có dấu hiệu mài mòn\n"
            "- Mức 3: Cảnh báo hỏng hóc nghiêm trọng\n\n"
            "Yếu tố nổi bật: Độ rung và tổng số chu kỳ ép có ảnh hưởng mạnh đến chuyển dịch trạng thái"
        )

    st.markdown("---")
    st.subheader("📜 Lịch sử trạng thái - Vấn đề 2")
    if len(st.session_state.history_problem2) > 0:
        df_history_p2 = pd.DataFrame(st.session_state.history_problem2)
        styled_history_p2 = df_history_p2.style.map(
            color_trang_thai_p2,
            subset=["Trạng thái máy"]
        )
        st.dataframe(styled_history_p2, use_container_width=True, hide_index=True)

# =========================================================
# 8. HÀM VẤN ĐỀ 3
# =========================================================
def create_lego_base_image(width=640, height=420):
    img = Image.new("RGB", (width, height), "#f3f4f6")
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle((30, 280, 610, 370), radius=20, fill="#4b5563")
    draw.line((40, 300, 600, 300), fill="#9ca3af", width=3)
    draw.line((40, 330, 600, 330), fill="#9ca3af", width=3)
    draw.line((40, 360, 600, 360), fill="#9ca3af", width=3)

    lego_x1, lego_y1, lego_x2, lego_y2 = 220, 130, 430, 270
    draw.rounded_rectangle((lego_x1, lego_y1, lego_x2, lego_y2), radius=18, fill="#ef4444", outline="#991b1b", width=4)

    studs = [
        (255, 150, 295, 185),
        (320, 150, 360, 185),
        (385, 150, 425, 185)
    ]
    for s in studs:
        draw.ellipse(s, fill="#f87171", outline="#991b1b", width=3)

    draw.text((35, 25), "Camera Vision - Vung kiem tra san pham", fill="#111827")
    return img

def simulate_yolo_detection():
    scenario = random.choices(
        population=["OK", "Bavia", "Khuyết", "Xước", "Mixed"],
        weights=[35, 20, 20, 15, 10],
        k=1
    )[0]

    detections = []

    if scenario == "OK":
        detections.append({
            "label": "OK",
            "confidence": round(random.uniform(0.95, 0.99), 2),
            "bbox": (220, 130, 430, 270)
        })
    elif scenario == "Bavia":
        detections.append({
            "label": "Bavia",
            "confidence": round(random.uniform(0.86, 0.96), 2),
            "bbox": (415, 205, 455, 248)
        })
    elif scenario == "Khuyết":
        detections.append({
            "label": "Khuyết",
            "confidence": round(random.uniform(0.84, 0.95), 2),
            "bbox": (285, 205, 335, 245)
        })
    elif scenario == "Xước":
        detections.append({
            "label": "Xước",
            "confidence": round(random.uniform(0.82, 0.94), 2),
            "bbox": (245, 215, 405, 235)
        })
    else:
        possible = [
            {"label": "Bavia", "confidence": round(random.uniform(0.83, 0.95), 2), "bbox": (415, 205, 455, 248)},
            {"label": "Khuyết", "confidence": round(random.uniform(0.82, 0.93), 2), "bbox": (285, 205, 335, 245)},
            {"label": "Xước", "confidence": round(random.uniform(0.80, 0.91), 2), "bbox": (245, 215, 405, 235)},
        ]
        detections = random.sample(possible, random.randint(2, 3))

    return detections

def draw_detection_on_image(base_img, detections):
    img = base_img.copy()
    draw = ImageDraw.Draw(img)

    for det in detections:
        label = det["label"]
        conf = det["confidence"]
        x1, y1, x2, y2 = det["bbox"]
        color = CLASS_COLORS.get(label, "#000000")

        draw.rectangle((x1, y1, x2, y2), outline=color, width=4)

        text = f"{label} ({conf:.2f})"
        tx1, ty1 = x1, max(5, y1 - 28)
        tx2, ty2 = x1 + 125, y1 - 2 if y1 - 2 > 25 else y1 + 26
        draw.rounded_rectangle((tx1, ty1, tx2, ty2), radius=6, fill=color)
        draw.text((tx1 + 8, ty1 + 6), text, fill="white")

    return img

def summarize_detections(detections):
    counts = {"OK": 0, "Bavia": 0, "Khuyết": 0, "Xước": 0}
    for det in detections:
        counts[det["label"]] += 1

    if counts["Bavia"] == 0 and counts["Khuyết"] == 0 and counts["Xước"] == 0 and counts["OK"] > 0:
        result = "ĐẠT"
        result_color = "success"
        result_text = "Sản phẩm đạt chuẩn ngoại quan."
    else:
        result = "KHÔNG ĐẠT"
        result_color = "error"
        result_text = "Phát hiện lỗi ngoại quan trên sản phẩm."

    return counts, result, result_color, result_text

def save_history_problem3():
    detections = st.session_state.problem3_detections
    counts, result, _, _ = summarize_detections(detections)
    labels = [d["label"] for d in detections]
    row = {
        "Thời gian": datetime.now().strftime("%H:%M:%S"),
        "Số vùng phát hiện": len(detections),
        "Nhãn phát hiện": ", ".join(labels),
        "Kết luận": result
    }
    st.session_state.history_problem3.insert(0, row)
    st.session_state.history_problem3 = st.session_state.history_problem3[:15]

def render_problem3():
    st.markdown("## Vấn đề 3")
    st.markdown("### Phân loại lỗi ngoại quan bằng hình ảnh")

    base_img = create_lego_base_image()
    detections = st.session_state.problem3_detections
    annotated_img = draw_detection_on_image(base_img, detections)
    counts, result, result_color, result_text = summarize_detections(detections)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Số vùng phát hiện", len(detections))
    k2.metric("OK", counts["OK"])
    k3.metric("Tổng số lỗi", counts["Bavia"] + counts["Khuyết"] + counts["Xước"])
    k4.metric("Kết luận", result)

    st.markdown("---")

    left, right = st.columns([1.35, 1])
    with left:
        st.subheader("🖼️ Ảnh kiểm tra ngoại quan")
        st.image(annotated_img, use_container_width=True)

    with right:
        st.subheader("📦 Kết quả phát hiện")
        df = pd.DataFrame([
            {
                "Nhãn lỗi": d["label"],
                "Độ tin cậy": d["confidence"],
                "Tọa độ bbox": str(d["bbox"])
            }
            for d in detections
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("📊 Thống kê theo lớp")
        stats_df = pd.DataFrame([
            {"Lớp": "OK", "Số lượng": counts["OK"]},
            {"Lớp": "Bavia", "Số lượng": counts["Bavia"]},
            {"Lớp": "Khuyết", "Số lượng": counts["Khuyết"]},
            {"Lớp": "Xước", "Số lượng": counts["Xước"]},
        ])
        st.dataframe(stats_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    if result_color == "success":
        st.success(f"{result} - {result_text}")
    else:
        st.error(f"{result} - {result_text}")

    info1, info2 = st.columns(2)
    with info1:
        st.info(
            "Mô hình dự đoán: YOLOv8 dựa trên CNN\n\n"
            "Dữ liệu huấn luyện gán nhãn theo định dạng YOLO gồm 4 lớp:\n"
            "- OK\n"
            "- Bavia\n"
            "- Khuyết\n"
            "- Xước"
        )
    with info2:
        st.info(
            "Cơ chế thực hiện:\n\n"
            "1. Camera Vision thu nhận hình ảnh\n"
            "2. Trích xuất đặc trưng ảnh\n"
            "3. Phát hiện vùng lỗi trên sản phẩm\n"
            "4. Xác định tọa độ lỗi bằng bounding box\n"
            "5. Phân loại loại lỗi tương ứng"
        )

    st.markdown("---")
    st.subheader("📜 Lịch sử kiểm tra ngoại quan")
    if len(st.session_state.history_problem3) > 0:
        df_history = pd.DataFrame(st.session_state.history_problem3)
        st.dataframe(df_history, use_container_width=True, hide_index=True)

# =========================================================
# 9. KHỞI TẠO SESSION STATE RIÊNG TỪNG VẤN ĐỀ
# =========================================================
if "selected_problem" not in st.session_state:
    st.session_state.selected_problem = "Vấn đề 1: Tối ưu chất lượng sản phẩm ép phun"

# Problem 1
if "san_luong_v1" not in st.session_state:
    st.session_state.san_luong_v1 = 5048
if "ty_le_dat_v1" not in st.session_state:
    st.session_state.ty_le_dat_v1 = 98.5
if "overlay_bi_tat_v1" not in st.session_state:
    st.session_state.overlay_bi_tat_v1 = False
if "last_so_canh_bao_v1" not in st.session_state:
    st.session_state.last_so_canh_bao_v1 = 0
if "manual_override_active_v1" not in st.session_state:
    st.session_state.manual_override_active_v1 = False
if "show_optimization_result" not in st.session_state:
    st.session_state.show_optimization_result = False
if "problem1" not in st.session_state:
    st.session_state.problem1 = generate_safe_data_v1()

# Problem 2
if "problem2" not in st.session_state:
    st.session_state.problem2 = generate_problem2_data()
if "history_problem2" not in st.session_state:
    st.session_state.history_problem2 = []
    save_problem2_history()

# Problem 3
if "problem3_detections" not in st.session_state:
    st.session_state.problem3_detections = simulate_yolo_detection()
if "history_problem3" not in st.session_state:
    st.session_state.history_problem3 = []
    save_history_problem3()

# =========================================================
# 10. SIDEBAR ĐIỀU HƯỚNG
# =========================================================
st.sidebar.header("📂 Chọn vấn đề")
selected_problem = st.sidebar.radio(
    "Nội dung hiển thị",
    [
        "Vấn đề 1: Tối ưu chất lượng sản phẩm ép phun",
        "Vấn đề 2: Bảo trì dự đoán cho hệ thống khuôn và trục vít",
        "Vấn đề 3: Phân loại lỗi ngoại quan bằng hình ảnh"
    ],
    index=[
        "Vấn đề 1: Tối ưu chất lượng sản phẩm ép phun",
        "Vấn đề 2: Bảo trì dự đoán cho hệ thống khuôn và trục vít",
        "Vấn đề 3: Phân loại lỗi ngoại quan bằng hình ảnh"
    ].index(st.session_state.selected_problem)
)
st.session_state.selected_problem = selected_problem

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Điều khiển theo vấn đề")

# =========================================================
# 11. SIDEBAR RIÊNG CHO VẤN ĐỀ 1
# =========================================================
if selected_problem == "Vấn đề 1: Tối ưu chất lượng sản phẩm ép phun":
    auto_check_v1 = st.sidebar.checkbox("Tự động cập nhật Vấn đề 1", value=True)

    if st.sidebar.button("Cập nhật 1 chu kỳ - Vấn đề 1"):
        st.session_state.san_luong_v1 += 1
        if not st.session_state.manual_override_active_v1:
            st.session_state.problem1 = generate_safe_data_v1()
        st.rerun()

    if st.sidebar.button("Tìm bộ thông số tối ưu"):
        apply_optimal_parameters_v1()
        st.sidebar.success("Đã áp dụng bộ thông số tối ưu.")
        st.rerun()

    if st.sidebar.button("Reset dữ liệu Vấn đề 1"):
        st.session_state.san_luong_v1 = 5048
        st.session_state.ty_le_dat_v1 = 98.5
        st.session_state.overlay_bi_tat_v1 = False
        st.session_state.last_so_canh_bao_v1 = 0
        st.session_state.manual_override_active_v1 = False
        st.session_state.show_optimization_result = False
        st.session_state.problem1 = generate_safe_data_v1()
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("Điều khiển bằng tay - Vấn đề 1")
    all_params_v1 = list(st.session_state.problem1.keys())
    param_to_change = st.sidebar.selectbox("Thông số Vấn đề 1", all_params_v1)
    new_value = st.sidebar.number_input(
        "Giá trị mới",
        value=float(st.session_state.problem1[param_to_change]),
        step=0.01
    )

    if st.sidebar.button("Ghi giá trị Vấn đề 1"):
        st.session_state.problem1[param_to_change] = round(new_value, 3)
        st.session_state.manual_override_active_v1 = True
        st.session_state.overlay_bi_tat_v1 = False
        st.sidebar.success(f"Đã cập nhật {param_to_change}!")
        st.rerun()

# =========================================================
# 12. SIDEBAR RIÊNG CHO VẤN ĐỀ 2
# =========================================================
elif selected_problem == "Vấn đề 2: Bảo trì dự đoán cho hệ thống khuôn và trục vít":
    auto_check_v2 = st.sidebar.checkbox("Tự động cập nhật Vấn đề 2", value=True)

    if st.sidebar.button("Cập nhật 1 chu kỳ - Vấn đề 2"):
        st.session_state.problem2 = generate_problem2_data()
        save_problem2_history()
        st.rerun()

    if st.sidebar.button("Reset lịch sử Vấn đề 2"):
        st.session_state.problem2 = generate_problem2_data()
        st.session_state.history_problem2 = []
        save_problem2_history()
        st.rerun()

# =========================================================
# 13. SIDEBAR RIÊNG CHO VẤN ĐỀ 3
# =========================================================
else:
    auto_check_v3 = st.sidebar.checkbox("Tự động cập nhật Vấn đề 3", value=False)

    if st.sidebar.button("Cập nhật 1 chu kỳ - Vấn đề 3"):
        st.session_state.problem3_detections = simulate_yolo_detection()
        save_history_problem3()
        st.rerun()

    if st.sidebar.button("Reset lịch sử Vấn đề 3"):
        st.session_state.problem3_detections = simulate_yolo_detection()
        st.session_state.history_problem3 = []
        save_history_problem3()
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("Chọn chế độ lỗi mẫu")
    manual_mode = st.sidebar.selectbox(
        "Tình huống mô phỏng",
        ["Ngẫu nhiên", "OK", "Bavia", "Khuyết", "Xước"]
    )

    if st.sidebar.button("Áp dụng tình huống Vấn đề 3"):
        if manual_mode == "Ngẫu nhiên":
            st.session_state.problem3_detections = simulate_yolo_detection()
        elif manual_mode == "OK":
            st.session_state.problem3_detections = [{
                "label": "OK",
                "confidence": 0.98,
                "bbox": (220, 130, 430, 270)
            }]
        elif manual_mode == "Bavia":
            st.session_state.problem3_detections = [{
                "label": "Bavia",
                "confidence": 0.93,
                "bbox": (415, 205, 455, 248)
            }]
        elif manual_mode == "Khuyết":
            st.session_state.problem3_detections = [{
                "label": "Khuyết",
                "confidence": 0.91,
                "bbox": (285, 205, 335, 245)
            }]
        else:
            st.session_state.problem3_detections = [{
                "label": "Xước",
                "confidence": 0.89,
                "bbox": (245, 215, 405, 235)
            }]
        save_history_problem3()
        st.rerun()

# =========================================================
# 14. GIAO DIỆN CHÍNH
# =========================================================
st.markdown(
    '# <p style="text-align: center;">🏭 Dashboard giám sát dây chuyền sản xuất LEGO</p>',
    unsafe_allow_html=True
)
st.caption("Ứng dụng tích hợp 3 vấn đề độc lập; mỗi lần chỉ hiển thị dữ liệu thuộc đúng vấn đề đang chọn.")

st.markdown("---")

if selected_problem == "Vấn đề 1: Tối ưu chất lượng sản phẩm ép phun":
    render_problem1()
elif selected_problem == "Vấn đề 2: Bảo trì dự đoán cho hệ thống khuôn và trục vít":
    render_problem2()
else:
    render_problem3()

# =========================================================
# 15. REALTIME THEO ĐÚNG VẤN ĐỀ ĐANG CHỌN
# =========================================================
if selected_problem == "Vấn đề 1: Tối ưu chất lượng sản phẩm ép phun":
    if 'auto_check_v1' in locals() and auto_check_v1:
        if not st.session_state.manual_override_active_v1:
            st.session_state.san_luong_v1 += 1
            st.session_state.problem1 = generate_safe_data_v1()
        time.sleep(2.5)
        st.rerun()

elif selected_problem == "Vấn đề 2: Bảo trì dự đoán cho hệ thống khuôn và trục vít":
    if 'auto_check_v2' in locals() and auto_check_v2:
        st.session_state.problem2 = generate_problem2_data()
        save_problem2_history()
        time.sleep(2.5)
        st.rerun()

else:
    if 'auto_check_v3' in locals() and auto_check_v3:
        st.session_state.problem3_detections = simulate_yolo_detection()
        save_history_problem3()
        time.sleep(2.5)
        st.rerun()