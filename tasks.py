from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    #browser.configure(slowmo = 500)
    open_robot_order_website()
    orders = get_orders()
    
    for order in orders:
        close_annoying_modal()
        fill_the_form(order)
    
    archive_receipts()

def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def close_annoying_modal():
    page = browser.page()
    page.click("button:text('OK')")

def get_orders():
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv",overwrite= True)

    library = Tables()
    orders = library.read_table_from_csv("orders.csv")
    return orders

def store_receipt_as_pdf(order_number):
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html(timeout=500)

    pdf = PDF()
    output_path = f"./output/robot_receipt_{order_number}.pdf"
    pdf.html_to_pdf(receipt_html, output_path)

    return output_path

def screenshot_robot(order_number):
    page = browser.page()
    output_path = f"./output/robot_preview_{order_number}.png"
    page.screenshot(path=output_path)

    return output_path

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()

    list_of_files = [str(screenshot)]
    pdf.add_files_to_pdf(files=list_of_files, append = True, target_document = pdf_file)

    return

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip("./output", "./output/receipts.zip", include="*.pdf")

def fill_the_form(order):
    page = browser.page()
    page.select_option("#head", value=order["Head"])
    page.click(f"#id-body-{int(order['Body'])}")
    page.fill("xpath=html/body/div/div/div[1]/div/div[1]/form/div[3]/input", str(order['Legs']))
    page.fill("#address", str(order['Address']))
    page.click("button:text('PREVIEW')")
    screenshot_path = screenshot_robot(order['Order number'])
    page.click("button:text('ORDER')")
    try:
        pdf_path = store_receipt_as_pdf(order['Order number'])
        embed_screenshot_to_receipt(screenshot_path, pdf_path)
        page.click("button:text('ORDER ANOTHER ROBOT')", timeout=500)
    except:
        print(f"Timed Out. Retrying")
        fill_the_form(order)
    
    