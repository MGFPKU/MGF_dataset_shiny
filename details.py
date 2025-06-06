import polars as pl
from shiny import ui
from htmltools._core import Tag


def render_detail(row: pl.DataFrame) -> Tag:
    if row.is_empty():
        return ui.markdown("### ⚠️ Policy not found")

    r = row.row(0)

    return ui.div(
        ui.tags.style("""
            .detail-title {
                font-size: 2rem;
                font-weight: bold;
                margin-bottom: 1em;
            }

            .detail-meta {
                display: flex;
                background-color: #f9f9f9;
                padding: 1em;
                border-radius: 0.5em;
                margin-bottom: 1.5em;
                font-size: 0.95rem;
            }

            .meta-item {
                flex: 1;
                padding: 0 1em;
            }

            .meta-label {
                font-weight: bold;
                color: #333;
                margin-bottom: 0.2em;
            }

            .detail-text {
                font-size: 1rem;
                line-height: 1.8;
                white-space: pre-wrap;
                margin-bottom: 2em;
            }

            .detail-buttons {
                display: flex;
                gap: 1em;
                margin-top: 1em;
            }

            .detail-buttons a,
            .detail-buttons button {
                padding: 0.75em 2em;
                font-size: 1em;
                border: none;
                border-radius: 999px;
                cursor: pointer;
                text-decoration: none;
                color: white;
                background-color: rgb(13, 97, 72);
                transition: background-color 0.3s;
            }

            .detail-buttons a:hover,
            .detail-buttons button:hover {
                color: white;
                background-color: rgb(11, 82, 61);
            }
        """),
        ui.div(r[1], class_="detail-title"),
        ui.div(
            *[
                ui.div(
                    ui.div(label, class_="meta-label"),
                    value,
                    class_="meta-item",
                    style=("border-right: 1px solid #aaa;" if i < 4 else ""),
                )
                for i, (label, value) in enumerate(
                    [
                        ("经济体", r[4]),
                        ("时间", r[2]),
                        ("政策类型", r[3]),
                        ("发布主体", r[4]),
                        ("关键词", r[6] if r[6] else ""),
                    ]
                )
            ],
            class_="detail-meta",
        ),
        ui.div(r[8] if len(r) > 8 else "暂无详细描述内容。", class_="detail-text"),
        ui.div(
            ui.input_action_button("back", "返回列表", class_="btn"),
            ui.a("详情链接", href=r[7], target="_blank", class_="btn"),
            class_="detail-buttons",
        ),
    )
