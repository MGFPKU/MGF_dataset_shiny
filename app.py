from htmltools._core import Tag
from shiny import App, ui, reactive, render
import os
import polars as pl
import io
import requests

from table import output_paginated_table
from details import render_detail
from download import download_tab, send_to_email

# Dataset info
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "MGFPKU/MGF_dataset_scraping"
FILE_PATH = "data/data.csv"
BRANCH = "main"


def fetch_data():
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.raw",
    }

    api_url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}?ref={BRANCH}"
    res = requests.get(api_url, headers=headers)
    if res.status_code != 200:
        raise RuntimeError(f"Failed to fetch file: {res.status_code}\n{res.text}")
    return pl.read_csv(io.StringIO(res.text))


raw_df = fetch_data()
df = (
    raw_df.with_columns(
        pl.col("时间").str.strptime(pl.Date, "%m/%Y", strict=False).alias("parsed_time")
    )
    .sort("parsed_time", descending=True)
    .drop(["parsed_time", "序号", "新闻链接","备注"])
)

# fix region tags
regions: list[str] = df["经济体"].drop_nulls().to_list()
# Split by '；', strip whitespace, flatten
all_regions = sorted(set(r.strip() for entry in regions for r in entry.split("；")))

# compile ui
app_ui = ui.page_fluid(
    ui.navset_hidden(
        ui.nav_panel(
            "tabview",
            ui.layout_columns(
                ui.input_select(
                    "region",
                    "经济体",
                    choices=["全部"] + all_regions,
                ),
                ui.input_select(
                    "type",
                    "政策类型",
                    choices=["全部"] + sorted(df["政策类型"].unique().to_list()),
                ),
                ui.input_select(
                    "year",
                    "年份",
                    choices=["全部"]
                    + sorted(df["时间"].str.slice(3, 4).unique().to_list(), reverse=True),
                ),
                ui.input_text(id="keyword", label="关键词", placeholder="请输入关键词"),
                ui.div(
                    ui.div(
                        "下载",
                        class_="form-label",
                        style="visibility: hidden; height: 1em;",
                    ),
                    ui.input_action_button(
                        "download",
                        "",
                        class_="download-icon",
                        icon=ui.tags.svg(
                            {
                                "xmlns": "http://www.w3.org/2000/svg",
                                "viewBox": "0 0 24 24",
                                "fill": "currentColor",
                                "height": "20",
                                "width": "20",
                            },
                            Tag(
                                "path",
                                d="M5 20h14v-2H5v2zm7-18v12l5-5h-3V4h-4v5H7l5 5V2z",
                            ),
                        ),
                    ),
                    class_="col-sm-2",  # mimic layout_columns spacing
                    style="display: flex; flex-direction: column; align-items: start; justify-content: end; padding-top: 0.6em;",
                ),
            ),
            ui.tags.style("""
                th, td {
                    text-align: left;
                }
                .download-icon {
                    background-color: white;
                    border: 1px solid #ccc;
                    padding: 6px 12px;
                    border-radius: 8px;
                    cursor: pointer;
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    transition: background-color 0.2s;
                    position: relative;
                }
                .download-icon:hover {
                    background-color: #f0f0f0;
                }
                .download-icon:hover::after {
                    content: '下载结果';
                    position: absolute;
                    bottom: -2em;
                    background-color: #bbb;
                    color: black;
                    font-size: 12px;
                    padding: 4px 8px;
                    border-radius: 4px;
                    white-space: nowrap;
                }

                .download-icon svg {
                    width: 20px;
                    height: 20px;
                    fill: #333;
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
            ui.navset_hidden(
                ui.nav_panel(
                    "table_panel",
                    ui.output_ui(id="table_ui"),
                ),
                download_tab,
                id = "table_download",
            ),
        ),
        ui.nav_panel("detail_view", ui.output_ui("detail_ui")),
        id="view",
    )
)


def server(input, output, session):
    current_page = reactive.value(1)
    focused_policy = reactive.value(None)

    @reactive.Calc
    def filtered():
        current_page.set(1)
        data = df
        if input.region() != "全部":
            data = data.filter(pl.col("经济体").str.contains(input.region()))
        if input.type() != "全部":
            data = data.filter(pl.col("政策类型") == input.type())
        if input.year() != "全部":
            data = data.filter(pl.col("时间").cast(str).str.slice(3, 4) == input.year())
        if input.keyword():
            keyword: str = input.keyword().lower().strip()
            if keyword:
                string_cols = [
                    col for col, dtype in data.schema.items() if dtype == pl.String
                ]

                if string_cols:
                    filter_expr = pl.fold(
                        acc=pl.lit(False),
                        exprs=[
                            pl.col(col).str.to_lowercase().str.contains(keyword)
                            for col in string_cols
                        ],
                        function=lambda acc, expr: acc | expr,
                    )
                    data = data.filter(filter_expr)

        return data

    @output
    @render.ui  # table
    def table_ui() -> Tag:
        # Rearrange and format data
        data: pl.DataFrame = (
            filtered()
            .select((["经济体", "政策动态", "政策类型", "发布主体", "时间"]))
            .with_columns(
                pl.col("时间")
                .str.strptime(pl.Date, "%m/%Y", strict=False)
                .dt.strftime("%Y-%m")
            )
        )
        try:
            table: Tag = output_paginated_table("mytable", data, page=current_page())
            return table
        except Exception as e:
            print("⚠️ Error rendering table:", e)
            return ui.markdown(f"**Error rendering table:** `{e}`")

    @output
    @render.ui
    def detail_ui():
        if not focused_policy():
            return ui.markdown("⚠️ 未找到政策详情。")
        row = df.filter(pl.col("政策动态") == focused_policy())
        return render_detail(row)

    @reactive.effect
    @reactive.event(input.download)
    async def _():
        ui.update_navs("table_download", selected="download_panel")

    @render.text
    def nrow():
        return f"当前筛选结果：{filtered().shape[0]} 条记录"

    @reactive.effect
    @reactive.event(input.send_csv)
    async def _():
        email = input.user_email()
        inst = input.user_inst()

        ## ✅ Save info in browser localStorage
        await session.send_custom_message("storeUserInfo", {
            "email": email,
            "inst": inst
        })
        data_csv: str = filtered().write_csv(
            include_bom=True,
            separator=",",
            quote_char='"',
            quote_style="non_numeric",
            null_value="",
        )  # Returns as string
        response = await send_to_email(email, inst, "csv", data_csv)
        ui.notification_show(f"📬 文件已发送至邮箱: {response}", type="message")

    @reactive.effect
    @reactive.event(input.send_excel)
    async def _():
        # Step 1: Get user email and institution
        email = input.user_email()
        inst = input.user_inst()

        ## ✅ Save info in browser localStorage
        await session.send_custom_message("storeUserInfo", {
            "email": email,
            "inst": inst
        })

        # Step 2: Write Excel to in-memory buffer
        buffer = io.BytesIO()
        filtered().write_excel(buffer)
        buffer.seek(0)

        # Step 3: Send Excel to email
        response = await send_to_email(email, inst, "xlsx", buffer.getvalue())
        ui.notification_show(f"📬 文件已发送至邮箱: {response}", type="message")

    @reactive.Effect
    def on_click():
        if input.mytable():
            focused_policy.set(input.mytable())
            ui.update_navs("view", selected="detail_view")

    @reactive.effect
    @reactive.event(input.mytable_page)
    async def _():
        current_page.set(input.mytable_page())

    @reactive.effect
    @reactive.event(input.back)
    async def _():
        ui.update_navs("view", selected="tabview")

    @reactive.effect
    @reactive.event(input.back1)
    async def _():
        ui.update_navs("table_download", selected="table_panel")

app = App(app_ui, server, debug=True)
