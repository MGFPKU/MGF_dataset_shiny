
from shiny import ui
import os

GOOGLE_SCRIPT_URL: str | None = os.getenv("GOOGLE_SCRIPT_URL")

download_tab = ui.nav_panel(
                    "download_panel",
                    ui.output_text(id="nrow"),
                    ui.input_text("user_inst", "机构名称", placeholder="请输入机构名称"),
                    ui.input_text("user_email", "邮箱", placeholder="请输入邮箱"),
                    ui.div(
                        ui.layout_columns(
                            ui.download_button(id="download_csv", label="下载 CSV"),
                            ui.download_button(id="download_excel", label="下载 Excel"),
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