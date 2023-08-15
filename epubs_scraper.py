import sys
import os
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import urllib
import requests
from selenium import webdriver
from argparse import ArgumentParser

"""
Example usage:
python scraping_af_regulations.py --website "https://www.e-publishing.af.mil/Product-Index/#/?view=pubs&orgID=10141&catID=1&series=5&modID=449&tabID=131" --save_loc downloaded_pdfs --driver_loc "C://Users/PA27879/chromium/chromedriver.exe"
"""


WEBSITE_KEY = 'website'
LOC_KEY = 'save_loc'
DRIVER_KEY = 'driver'
DRIVER_LOC_KEY = 'driver_loc'

def _parse_cli(argv):
        parser = ArgumentParser(description='splits the given bitext file into a source and target file')
        parser.add_argument('--%s' % WEBSITE_KEY, required=True, help='the website url from which to download all pdfs')
        parser.add_argument('--%s' % LOC_KEY, required=True, help='the destination in which to save the resulting pdfs')
        parser.add_argument('--%s' % DRIVER_KEY, required=False, help='Which driver to use (defaults to chrome)')
        parser.add_argument('--%s' % DRIVER_LOC_KEY, required=False, help='The location of the driver to use (defaults to path)')
        return vars(parser.parse_args(argv))

def download_pdf(pdf_loc, save_loc):
    pdf_name = os.path.split(pdf_loc)[-1]
    if not os.path.isdir(save_loc):
        os.mkdir(save_loc)
    with urllib.request.urlopen(pdf_loc) as web_file:
        web_pdf = web_file.read()
    with open(os.path.join(save_loc, pdf_name), 'wb+') as f:
        f.write(web_pdf)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    opts = _parse_cli(argv=argv)
    url = opts[WEBSITE_KEY]
    save_loc = opts[LOC_KEY]
    save_loc = 'download_pdf'
    driver = opts[DRIVER_KEY] if DRIVER_KEY in opts and opts[DRIVER_KEY] is not None else 'chrome'
    driver_loc = opts[DRIVER_LOC_KEY] if DRIVER_LOC_KEY in opts else None

    if driver == 'chrome':
        driver_func = webdriver.Chrome
    elif driver == 'firefox':
        driver_func = webdriver.Firefox
    else:
        raise ValueError('{} not currently supported'.format(driver))
    if driver_loc is None:
        driver = driver_func()
    else:
        driver = driver_func(driver_loc)

    try:
        mds = []
        content = driver.page_source
        soup = BeautifulSoup(content)
        for i, obj in enumerate(soup.find_all('table')):
            all_rows = obj.find_all('tr')
            for j, row in enumerate(all_rows):
                all_cols = row.find_all('td')
                for k, col in enumerate(all_cols):
                    for link in col.find_all('a'):
                        title = link.get('title')
                        if title is not None and title == 'View Detail':
                            print(link.getText())
                            driver.find_element_by_link_text(link.getText()).click()
                            time.sleep(1)
                            metadata = {}
                            content = driver.page_source
                            soup = BeautifulSoup(content)
                            for sub_row in soup.find_all('table')[0].find_all('tr'):
                                for sub_col in sub_row.find_all('th'):
                                    feat_name = sub_col.getText()
                                for sub_col in sub_row.find_all('td'):
                                    metadata[feat_name] = sub_col.getText()
                            driver.find_element_by_class_name('close').click()
                            time.sleep(1)
                            mds.append(metadata)
                        elif title is not None and title == 'View Product':
                            download_pdf(pdf_loc, 'saved_op_pdfs')
        driver.quit()
        metadata = pd.DataFrame.from_dict(mds)
        metadata.index = df['Product Title']
        metadata.to_csv(os.path.join(pdf_loc, 'metadata.csv'))
        # driver.get(url)
        # cont = True
        # page = 1
        # while cont:
        #     print(page, end='\r', flush=True)
        #     content = driver.page_source
        #     soup = BeautifulSoup(content, features="html.parser")
        #     for i, obj in enumerate(soup.find_all('table')):
        #         all_links = obj.find_all('a')
        #         for j, link in enumerate(all_links):
        #             pdf_loc = link.get('href')
        #             if pdf_loc != '#':
        #                 download_pdf(pdf_loc, 'saved_op_pdfs')
        #     page += 1
        #     elements = driver.find_elements_by_link_text(str(page))
        #     if len(elements) == 0:
        #         cont = False
        #     else:
        #         elements[0].click()

    except:
        driver.quit()
        raise ValueError('Closing after something broke')



if __name__ == "__main__":
    main()
