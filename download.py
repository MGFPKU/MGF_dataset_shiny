
from httpx._models import Response


from shiny import ui
import os
import httpx
import base64

GOOGLE_SCRIPT_URL: str | None = os.getenv("GOOGLE_SCRIPT_URL")

download_tab = ui.nav_panel(
                    "download_panel",
                    ui.output_text(id="nrow"),
                    ui.input_text("user_inst", "机构名称", placeholder="请输入机构名称"),
                    ui.input_text("user_email", "邮箱", placeholder="请输入邮箱"),
                    ui.div(
                        ui.layout_columns(
                            ui.input_action_button(id="send_csv", label="发送 CSV"),
                            ui.input_action_button(id="send_excel", label="发送 Excel"),
                            ui.input_action_button("back1", "返回列表")
                        ),
                        class_="detail-buttons",
                    ),
                    ui.tags.script("""
                    document.addEventListener("DOMContentLoaded", function() {
                        const email = localStorage.getItem("user_email");
                        const inst = localStorage.getItem("user_inst");
                        if (email) {
                            const emailInput = document.getElementById("user_email");
                            if (emailInput) {
                                emailInput.value = email; // update UI
                                //Shiny.setInputValue("user_email", email); // update server input
                            }
                        }

                        if (inst) {
                            const instInput = document.getElementById("user_inst");
                            if (instInput) {
                                instInput.value = inst;
                                //Shiny.setInputValue("user_inst", inst);
                            }
                        }
                    });
                    Shiny.addCustomMessageHandler("storeUserInfo", function(message) {
                        localStorage.setItem("user_email", message.email);
                        localStorage.setItem("user_inst", message.inst);
                    });
                    """)
                )

async def send_to_email(email: str, inst: str, fmt: str, data: bytes | str) -> Response:
    if fmt == "xlsx":
        if not isinstance(data, bytes):
            raise ValueError("Excel format requires binary data")
        content_b64 = base64.b64encode(data).decode("utf-8")
    else:
        if not isinstance(data, str):
            raise ValueError("CSV format requires string data")
        content_b64 = base64.b64encode(data.encode("utf-8")).decode("utf-8")

    payload = {
        "email": email,
        "inst": inst,
        "format": fmt,
        "content": content_b64,
    }
    async with httpx.AsyncClient() as client:
        if not GOOGLE_SCRIPT_URL:
            raise ValueError("GOOGLE_SCRIPT_URL environment variable is not set.")
        return await client.post(GOOGLE_SCRIPT_URL, json=payload)