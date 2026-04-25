import os
from tkinter import messagebox
from typing import Dict, List

# =========================
# GLOBAL STATE
# =========================
state: Dict = {
    "rect_id": None,
    # "img_size": None,
    "draw_mode": False,
    "start_x": None,
    "start_y": None,
    "points": [],
    "predict_result": " ",
    "count_NG": 0,
    "press_keyboard": False,
    "barcode_locked": False,
    "last_index": None,
    "jig_sn": None,
    "insp_sn": None,
}

LABEL = {0: "OK", 1: "NG"}

COORDINATE_FILE = "coordinate.txt"

def show_messagebox(type, title, message, parent):
    if type == "error":
        messagebox.showerror(title, message, parent=parent)
        return
    elif type == "info":
        messagebox.showinfo(title, message, parent=parent)
        return
    elif type == "warning":
        messagebox.showwarning(title, message, parent=parent)
        return
    elif type == "yesno":
        return messagebox.askyesno(title, message, parent=parent)

# =========================
# UI UTIL
# =========================
def show_messagebox(
    msg_type: str,
    title: str,
    message: str,
    parent=None
):
    """Wrapper for messagebox"""
    mapping = {
        "error": messagebox.showerror,
        "info": messagebox.showinfo,
        "warning": messagebox.showwarning,
        "yesno": messagebox.askyesno,
    }

    func = mapping.get(msg_type)
    if func:
        return func(title, message, parent=parent)


def crop_img(frame, x1, y1, x2, y2):
    return frame[y1:y2, x1:x2]

# =========================
# FILE HANDLING
# =========================
def load_box_from_file(canvas, state: Dict, parent) -> bool:
    """Load bounding box from file"""
    try:
        if not os.path.exists(COORDINATE_FILE):
            return False

        with open(COORDINATE_FILE, "r") as f:
            content = f.read().strip()

        if not content:
            show_messagebox("error", "Lỗi", "File rỗng!", parent)

        data = content.split(",")
        if len(data) != 4:
            show_messagebox("error", "Lỗi", "File có định dạng sai!", parent)

        x1, y1, x2, y2 = map(int, data)
        state["points"] = [x1, y1, x2, y2]

        if state["rect_id"]:
            canvas.delete(state["rect_id"])

        state["rect_id"] = canvas.create_rectangle(
            x1, y1, x2, y2,
            outline="blue",
            width=2
        )

        return True

    except Exception as e:
        show_messagebox("error", "Lỗi", f"Không thể load file: {e}", parent)
        return False
   
def save_box_to_file(points: List[int], parent) -> bool:
    """save bounding box"""
    try:
        with open(COORDINATE_FILE, "w") as f:
            f.write(",".join(map(str, points)))

        show_messagebox("info", "Thông báo", "Lưu tọa độ thành công!", parent)
        return True

    except Exception as e:
        show_messagebox("error", "Lỗi", f"Lỗi khi lưu file: {e}", parent)
        return False

# =========================
# DRAW EVENTS
# =========================
def on_mouse_down(event, canvas, state: Dict):
    state["start_x"], state["start_y"] = event.x, event.y

    if state["rect_id"]:
        canvas.delete(state["rect_id"])

    state["rect_id"] = canvas.create_rectangle(
        event.x, event.y,
        event.x, event.y,
        outline="red",
        width=2
    )

def on_mouse_drag(event, canvas, state: Dict):
    if state["rect_id"]:
        canvas.coords(
            state["rect_id"],
            state["start_x"], state["start_y"],
            event.x, event.y
        )

def on_mouse_up(event, canvas, state: Dict, parent):
    x1, y1 = state["start_x"], state["start_y"]
    x2, y2 = event.x, event.y

    # normalize the coordination
    x1, x2 = sorted([x1, x2])
    y1, y2 = sorted([y1, y2])

    state["points"] = [x1, y1, x2, y2]
    print("state after: ",state["points"])

    save_box_to_file(state["points"], parent)

    # reset
    state["start_x"] = None
    state["start_y"] = None

    # disable draw mode
    canvas.unbind("<Button-1>")
    canvas.unbind("<B1-Motion>")
    canvas.unbind("<ButtonRelease-1>")
    state["draw_mode"] = False

    print("Draw mode OFF")


def toggle_draw(canvas, state: Dict, parent):
    """turn on/turn off draw mode bounding box"""
    if os.path.exists(COORDINATE_FILE):
        result = show_messagebox(
            "yesno",
            "Thông báo",
            "Đã có bounding box.\nBạn muốn vẽ lại?",
            parent
        )

        if not result:
            if load_box_from_file(canvas, state, parent):
                show_messagebox("info", "Thông báo", "Đã load box cũ", parent)
                return
            else:
                os.remove(COORDINATE_FILE)
        else:
            os.remove(COORDINATE_FILE)

    state["draw_mode"] = True

    canvas.bind("<Button-1>", lambda e: on_mouse_down(e, canvas, state))
    canvas.bind("<B1-Motion>", lambda e: on_mouse_drag(e, canvas, state))
    canvas.bind("<ButtonRelease-1>", lambda e: on_mouse_up(e, canvas, state, parent))

    print("Draw mode ON")

# =========================
# IMAGE PROCESSING
# =========================
def crop_image(frame, x_min: int, y_min: int, x_max: int, y_max: int):
    """Crop ảnh an toàn (không out-of-bound)"""
    h, w = frame.shape[:2]

    x_min, y_min = max(0, x_min), max(0, y_min)
    x_max, y_max = min(w, x_max), min(h, y_max)

    return frame[y_min:y_max, x_min:x_max]

