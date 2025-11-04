from htmltools import tags, Tag
import polars as pl
import math
from i18n import i18n

def render_pagination(id: str, current: int, total: int) -> Tag:
    def page_btn(label, page, active=False):
        return tags.button(
            label,
            onclick=f'Shiny.setInputValue("{id}_page", {page}, {{priority: "event"}})',
            class_="page-btn" + (" active-page" if active else ""),
        )

    buttons = []

    # 首页 / 上一页
    buttons.append(page_btn(i18n("首页"), 1))
    buttons.append(page_btn(i18n("上一页"), max(1, current - 1)))

    # Page numbers
    # Page range: max 5 buttons, centered on current page
    start = max(1, current - 2)
    end = min(total, start + 4)
    # Adjust start again if we're near the end
    start = max(1, end - 4)

    for i in range(start, end + 1):
        buttons.append(page_btn(str(i), i, active=(i == current)))

    # 下一页 / 末页
    buttons.append(page_btn(i18n("下一页"), min(total, current + 1)))
    buttons.append(page_btn(i18n("末页"), total))

    # Optional dropdown
    dropdown = tags.select(
        *[tags.option(str(i), selected=(i == current)) for i in range(1, total + 1)],
        onchange=f'Shiny.setInputValue("{id}_page", parseInt(this.value), {{priority: "event"}})',
        style="margin-left: 1em;",
    )
    return tags.div(
        tags.style("""
            .page-btn {
                border: 1px solid #ccc;
                background: white;
                padding: 4px 10px;
                margin: 0 2px;
                cursor: pointer;
            }
            .page-btn:hover {
                background-color: rgb(22, 171, 127);
                color: white;
            }
            .active-page {
                background-color: rgb(13, 97, 72);
                color: white;
                font-weight: bold;
            }
        """),
        tags.div(
            *buttons,
            dropdown,
            tags.span("页", style="margin-left: 4px;"),
            style=(
                "display: flex; "
                "align-items: center; "
                "flex-wrap: wrap; "
                "gap: 4px; "
                "justify-content: center;"
                "margin: 1em; "
            ),
        ),
    )


def output_paginated_table(
    id: str, df: pl.DataFrame, page: int = 1, per_page: int = 10
) -> Tag:
    # Extract page slice
    total_rows = df.shape[0]
    total_pages = max(math.ceil(total_rows / per_page), 1)
    start = (page - 1) * per_page
    end = start + per_page
    slice_df = df[start:end, :6]  # first 6 columns only

    # Header
    thead = tags.thead(tags.tr(*(tags.th(col) for col in slice_df.columns)))

    # Rows
    tbody = tags.tbody()
    for row in slice_df.iter_rows():
        policy_id = str(row[1])  # Assume column index 1 is “政策动态”

        # Build each cell with a column-specific class
        row_cells = [
            tags.td(
                str(cell),
                class_=f"col-{col_name}"
            )
            for col_name, cell in zip(slice_df.columns, row)
        ]

        # Wrap the row with onclick handler
        row_tag = tags.tr(
            *row_cells,
            onclick=f'Shiny.setInputValue("{id}", "{policy_id}", {{priority: "event"}});',
            class_="clickable-row"
        )
        tbody.append(row_tag)

    # Pagination controls
    pagination = render_pagination(id, page, total_pages)

    table = tags.table(thead, tbody, class_="custom-table")
    return tags.div(
        tags.style("""
            .custom-table {
                border-collapse: collapse;
                width: 100%;
                table-layout: auto;
            }
            .custom-table th {
                text-align: left;
                font-weight: bold;
                padding: 16px 8px;
                border-bottom: 2px solid #ddd; /* Thick bottom border for header */
                white-space: nowrap;
            }
            .custom-table td {
                border: 1px solid #eee;
                padding: 14px 8px;
                white-space: nowrap;
            }

            /* Remove vertical borders */
            .custom-table th,
            .custom-table td {
                border-left: none;
                border-right: none;
            }

            /* Allow wrapping only for the 发布主体 column */
            .custom-table .col-发布主体 {
                white-space: normal;
                word-break: break-word;
            }

            .clickable-row {
                cursor: pointer;
                transition: background-color 0.2s;
            }

            .clickable-row:hover {
                background-color: rgba(13, 97, 72, 0.1);
            }

            .clickable-row td {
                /* Ensures no text underlines or color overrides interfere */
                color: black;
                text-decoration: none;
}
        """),
        table,
        pagination,
    )


if __name__ == "__main__":
    # Example usage
    df = pl.DataFrame(
        {
            "经济体": ["A", "B", "C"] * 5,
            "政策动态": ["Policy 1", "Policy 2", "Policy 3"] * 5,
            "政策类型": ["Type 1", "Type 2", "Type 3"] * 5,
            "发布主体": ["Agency A", "Agency B", "Agency C"] * 5,
            "时间": ["2021-01-01", "2021-02-01", "2021-03-01"] * 5,
        }
    )

    print(output_paginated_table("test_table", df, page=1))
