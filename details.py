import polars as pl
from shiny import ui
from htmltools._core import Tag, HTML

from i18n import i18n


def render_detail(row: pl.DataFrame) -> Tag | HTML:
    if row.is_empty():
        return ui.markdown("### ⚠️ Policy not found")

    r = row.row(0, named=True)

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
                font-size: 1rem;
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
                font-size: 1.25rem;
                line-height: 1.8;
                white-space: pre-wrap;
                margin-bottom: 2em;
            }
        """),
        ui.div(r[i18n("政策动态")], class_="detail-title"),
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
                        (i18n("经济体"), r[i18n("经济体")]),
                        (i18n("时间"), r[i18n("时间")]),
                        (i18n("政策类型"), r[i18n("政策类型")]),
                        (i18n("发布主体"), r[i18n("发布主体")]),
                        (i18n("关键词"), r.get(i18n("关键词")) or ""),
                    ]
                )
            ],
            class_="detail-meta",
        ),
        ui.div(r.get(i18n("内容简介")) or i18n("暂无详细描述内容。"), class_="detail-text"),
        ui.div(
            ui.input_action_button("back", i18n("返回列表"), class_="btn"),
            ui.a(i18n("详情链接"), href=r.get(i18n("原文链接"), ""), target="_blank", class_="btn"),
            class_="detail-buttons",
        ),
    )
