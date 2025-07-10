# app/utils/document.py

import os
import json
import jdatetime
import requests
from pathlib import Path
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright
from .date_utils import get_shamsi_date, get_future_shamsi_date
from .pricing import find_exact_match, estimate_price
from .invoice import generate_invoice_number
from config import (
    Melipayamak_API,
    PHONE_MELIPAYAMAK,
    DOMAIN,
    SMS_REPORT
)
from src.logger_config import logger, PATH

# Load pricing data
with open(os.path.join(PATH, "static", "Pricing.json"), 'r', encoding='utf-8') as f:
    pricing_data = json.load(f)

async def generate_invoice_pdf_from_html(invoice_data: dict, output_pdf_path: str):
    """
    Generate PDF invoice using HTML template rendered by Jinja2 and Playwright.
    """
    try:
        template_dir = os.path.join(PATH, 'templates')

        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template('invoice_template.html')
        html_content = template.render(invoice_data)

        # Save rendered HTML to a temporary file
        temp_html_path = Path("temp_invoice.html")
        temp_html_path.write_text(html_content, encoding="utf-8")

        async def render_pdf():
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                await page.goto(f"file://{temp_html_path.resolve()}", wait_until='networkidle')
                await page.pdf(path=output_pdf_path, format="A4", print_background=True)
                await browser.close()

        await render_pdf()

        temp_html_path.unlink(missing_ok=True)
        logger.info(f"PDF invoice generated with Playwright: {output_pdf_path}")
        return output_pdf_path

    except Exception as e:
        logger.error(f"Failed to generate PDF with Playwright: {e}")
        raise


def save_invoice_log(invoice_data: Dict[str, Any]):
    """
    Save invoice information to JSON file.
    """
    log_file = os.path.join(PATH, "static", 'invoices.json')

    existing_logs = []
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                existing_logs = json.load(f)
        except:
            existing_logs = []

    invoice_data['timestamp'] = jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    existing_logs.append(invoice_data)

    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(existing_logs, f, ensure_ascii=False, indent=2)


async def generate_invoice(
        name: str,
        phone: str,
        storage_type_both: str,
        tonnage: float,
        send_via_sms: bool = True
) -> Dict[str, Any]:
    """
    Generate invoice and send via Telegram or SMS.
    """
    try:

        if not phone.startswith('+'):
            phone = '+' + phone.lstrip('0')

        if storage_type_both == 'both':
            storage_type = 'below_zero'
            storage_type_text = "زیر صفر و بالای صفر"
        else:
            storage_type = storage_type_both
            storage_type_text = "زیر صفر" if storage_type == "below_zero" else "بالای صفر"


                        
        invoice_number = generate_invoice_number(phone)
        matched = find_exact_match(storage_type, tonnage)
        details = matched if matched else estimate_price(storage_type, tonnage)

        price_avg = round(sum(details['price_million_toman']) / 2, 2)
        price_number = int(price_avg * 1_000_000)
        if storage_type_both == 'both':
            price_number = price_number * 1.25
            
        price_formatted = "{:,}".format(price_number)

        tonnage_clean = int(tonnage) if tonnage == int(tonnage) else tonnage
        formatted_dims = [f"{d:.2f}".rstrip("0").rstrip(".") for d in details['dimensions_m']]
        dimensions_str = "×".join(formatted_dims)
        compressor_power = int(details['compressor_power_hp'])

        issue_date = get_shamsi_date()
        delivery_date = get_future_shamsi_date(30)

        invoice_data = {
            "name": name,
            "phone": phone,
            "invoice_number": invoice_number,
            "issue_date": issue_date,
            "due_date": delivery_date,
            "storage_type": storage_type_text,
            "tonnage": tonnage_clean,
            "dimensions": dimensions_str,
            "compressor_power": compressor_power,
            "price": price_formatted,
            "domain": DOMAIN
        }
        formatted_to = f"0{phone.lstrip('+')}"

        # Define the path for the static directory
        pdf_filename = os.path.join(PATH, 'static', 'pdf', f"{formatted_to}_{invoice_number}.pdf")

        await generate_invoice_pdf_from_html(invoice_data, str(pdf_filename))

        sent_sms = False
        # Send via SMS if requested
        if send_via_sms:
            sms_data = {
                "from": PHONE_MELIPAYAMAK,
                "to":  [formatted_to] + SMS_REPORT,  
                "text": (
                    f"سلام {name} \n"
                    "پیش فاکتور درخواستی شما از طریق لینک قابل مشاهده میباشد \n"
                    f"{DOMAIN}/static/pdf/{formatted_to}_{invoice_number}.pdf \n"
                    "لغو11"
                )
            }

            response = requests.post(f'https://console.melipayamak.com/api/send/advanced/{Melipayamak_API}', json=sms_data)
            if response.status_code == 200:
                logger.info("SMS sent successfully.")
                sent_sms = True
            else:
                logger.error(f"Failed to send SMS: {response.text}")

        result = {
            'success': True,
            'pdf_path': str(pdf_filename),
            'sent_to_sms': sent_sms,
            'invoice_number': invoice_number,
            'price_range': details['price_million_toman'],
            'issue_date': invoice_data['issue_date'],
            'due_date': invoice_data['due_date'],
            'customer': {'name': name, 'phone': phone},
            'storage': {
                'type': storage_type,
                'tonnage': tonnage,
                'details': details
            }
        }

        save_invoice_log(result)
        return result

    except Exception as e:
        try:
            if pdf_filename and os.path.exists(pdf_filename):
                os.remove(pdf_filename)
        except:
            pass

        error_result = {
            'success': False,
            'error': str(e),
            'customer': {'name': name, 'phone': phone},
            'storage': {'type': storage_type, 'tonnage': tonnage}
        }
        save_invoice_log(error_result)
        return error_result