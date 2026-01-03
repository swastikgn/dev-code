import json
import tempfile
from pathlib import Path
from time import perf_counter

import typst
from faker import Faker
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright
from weasyprint import HTML

DATA_COUNT = 1000
ITERATIONS = 3
faker = Faker()

# ----------------------------------------
# PDF functions now take `html_content`
# ----------------------------------------


def playwright_pdf(html_content: str):
    """
    Use Playwright to generate a PDF from pre-rendered HTML.
    """
    # Save HTML to a temp file
    temp_file = Path(tempfile.gettempdir()) / "playwright_temp.html"
    temp_file.write_text(html_content, encoding="utf-8")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        page.goto(f"file://{temp_file.resolve()}")

        page.pdf(path="playwright_output.pdf", format="A4")

        browser.close()


def weasyprint_pdf(html_content: str):
    HTML(string=html_content).write_pdf("weasyprint_output.pdf")


def typst_pdf(html_content: str):
    """
    For Typst, we need to feed the raw data still,
    because Typst template works with data JSON in sys_inputs.
    """
    # Write temporary JSON
    tmp_json = Path(tempfile.gettempdir()) / "typst_data.json"
    tmp_json.write_text(json.dumps(html_content, default=str))

    sys_inputs = {"data": json.dumps(html_content, default=str)}
    typst.compile(
        input="templates/typst.typ",
        output="typst_output.pdf",
        sys_inputs=sys_inputs,
    )


# ----------------------------------------
# Benchmark function
# ----------------------------------------


def benchmark(func, arg):
    times = []
    for i in range(ITERATIONS):
        start = perf_counter()
        func(arg)
        times.append(perf_counter() - start)
    return times


def format_table(results):
    header = f"{'Tool':<15} | {'Run 1':>7} | {'Run 2':>7} | {'Run 3':>7} | {'Avg':>7}"
    sep = "-" * len(header)
    print(header)
    print(sep)
    for name, times in results.items():
        avg = sum(times) / len(times)
        print(
            f"{name:<15} | {times[0]:>7.4f} | {times[1]:>7.4f} | {times[2]:>7.4f} | {avg:>7.4f}"
        )
    print(sep)


# ----------------------------------------
# Main
# ----------------------------------------


def main():
    data = []
    for i in range(DATA_COUNT):
        item = {
            "id": i + 1,
            "name": faker.name(),
            "dob": faker.date_of_birth(),
            "mobile_number": faker.phone_number(),
        }
        data.append(item)

    # ------------------------------------
    # 1) Render HTML ONCE outside
    # ------------------------------------
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("html_template.html")

    start = perf_counter()
    html_content = template.render(data=data)
    render_time = perf_counter() - start

    print(f"HTML render time: {render_time:.4f} seconds\n")

    print(f"Benchmarking with {DATA_COUNT} records (each run x{ITERATIONS}):\n")

    results = {}

    # ------------------------------------
    # 2) Benchmark PDF creation only
    # ------------------------------------
    results["WeasyPrint"] = benchmark(weasyprint_pdf, html_content)
    results["Playwright"] = benchmark(playwright_pdf, html_content)

    # For Typst, we still pass data list
    results["Typst"] = benchmark(typst_pdf, data)

    # ------------------------------------
    # 3) Output Table
    # ------------------------------------
    print("\nRESULTS (seconds):")
    format_table(results)


if __name__ == "__main__":
    main()

