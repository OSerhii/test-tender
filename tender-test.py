#!/usr/bin/env python
# -*- coding: utf-8 -*-


from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import time
from time import sleep
from datetime import datetime, timedelta
import random
import sys
import argparse

provider_users = {'buyer3@ustudio.com.ua': '123456',
                  'buyer4@ustudio.com.ua': '123456',
                  'buyer5@ustudio.com.ua': '123456',
                  'seller@ustudio.com.ua': '123456'}

locators = {'opentender': {
    'url': 'https://open-tender.com.ua',
},
    'brizol': {
        'url': 'https://brizol.net',
    },
    '25h8': {
        'url': 'http://25h8.byustudio.in.ua',
    },
}

number_of_features = 2
create_new_tender = True
tender_uaid = False
keep_browser_open = False


def createParser():
    parser = argparse.ArgumentParser(
        prog='tender-test',
        description='This script allows you to create tender with different parameters and bid it.',
        epilog='Version 0.1'
    )
    parser.add_argument('-m', '--method', default='open_aboveThresholdUA',
                        help='sets tender method according to VALUE attribute in GUI | DEFAULT: open_competitiveDialogueUA',
                        metavar='tender method')
    parser.add_argument('-l', '--lots', default=0, type=int,
                        help='sets number of lots to create in tender | DEFAULT: 0 LOTS',
                        metavar='number of lots')
    parser.add_argument('-i', '--items', default=1, type=int,
                        help='sets number of items in each lot | DEFAULT: 1 ITEM',
                        metavar='number of items')
    parser.add_argument('-e', '--enquiry', default=10, type=int,
                        help='sets enquiry period in minutes | DEFAULT: 10 MIN',
                        metavar='enquiry period')
    parser.add_argument('-t', '--tender', default=40, type=int,
                        help='sets tender period in minutes | DEFAULT: 40 MIN',
                        metavar='tender period')
    parser.add_argument('-p', '--platform', default='brizol',
                        help='sets locators for platform | DEFAULT: brizol',
                        metavar='platform locators')
    parser.add_argument('-n', '--iterations', default=1, type=int,
                        help='sets number of iterations| DEFAULT: 1',
                        metavar='iterations')

    return parser


def create_lot(driver):
    lot_amount = round(random.uniform(3000, 9999.99), 2)
    lot_minimal_step_amount = round(random.uniform(0.01, 0.03) * lot_amount, 2)
    select = Select(driver.find_element_by_name('tender_type'))
    select.select_by_value('2')
    for lot_index_int in range(number_of_lots):
        if lot_index_int != 0:
            driver.find_element_by_class_name('add_lot').click()
        lot_index_real = \
            driver.find_element_by_xpath("(//input[contains(@class,'lot_title')])[last()]").get_attribute('id').split('-')[1]
        lot_index = str(lot_index_int + 1)
        driver.find_element_by_id('tender-title').send_keys('test tender')
        driver.find_element_by_name('Tender[description]').send_keys(
            'test tender description (tender method = {})'.format(tender_method))
        if 'EU' in tender_method:
            driver.find_element_by_id('tender-title_en').send_keys('test tender EN')
            driver.find_element_by_name('Tender[description_en]').send_keys(
                'test tender desc EN (tender method = {})'.format(tender_method))
            driver.find_element_by_name('Tender[lots][' + lot_index_real + '][title_en]').send_keys(
                'test lot EN' + lot_index)
            driver.find_element_by_name('Tender[lots][' + lot_index_real + '][description_en]').send_keys(
                'test lot EN' + lot_index + ' desc')
        driver.find_element_by_name('Tender[lots][' + lot_index_real + '][title]').send_keys('test lot ' + lot_index)
        driver.find_element_by_name('Tender[lots][' + lot_index_real + '][description]').send_keys(
            'test lot ' + lot_index + ' desc')
        driver.find_element_by_name('Tender[lots][' + lot_index_real + '][value][amount]').send_keys(lot_amount)
        driver.find_element_by_name('Tender[lots][' + lot_index_real + '][minimalStep][amount]').send_keys(
            lot_minimal_step_amount)
        add_items(driver, lot_index)
        add_feature(driver, lot_index)


def add_items(driver, lot_index):
    for item_index_int in range(number_of_items):
        if item_index_int != 0:
            driver.find_element_by_xpath("(//button[contains(@class, 'add_item')])[last()]").click()
        item_index = \
            driver.find_element_by_xpath("(//textarea[contains(@class,'item-description')])[last()]").get_attribute(
                'id').split('-')[1]
        item_index_view = str(item_index_int + 1)
        driver.find_element_by_name('Tender[items][' + item_index + '][description]').send_keys(
            'test item ' + item_index_view + ' lot ' + lot_index)
        if 'EU' in tender_method:
            driver.find_element_by_name('Tender[items][' + item_index + '][description_en]').send_keys(
                'test item EN' + item_index_view + ' lot ' + lot_index)
        driver.find_element_by_name('Tender[items][' + item_index + '][quantity]').send_keys('10')
        select = Select(
            driver.find_element_by_name('Tender[items][' + item_index + '][additionalClassifications][0][dkType]'))
        select.select_by_value('000')
        driver.find_element_by_name('Tender[items][' + item_index + '][classification][description]').click()
        wait_until_element_is_visible(driver, '//*[@id="search_code"]', 20)
        driver.find_element_by_id('search_code').clear()
        driver.find_element_by_id('search_code').send_keys('03111100-3')
        driver.find_element_by_xpath('//span[contains(text(), "03111100-3")]/../..').click()
        driver.find_element_by_id('btn-ok').click()
        wait_until_element_is_not_visible(driver, "//*[@id='classificator-modal']", 20)
        select = Select(
            driver.find_element_by_name('Tender[items][' + item_index + '][additionalClassifications][0][dkType]'))
        select.select_by_value('000')
        driver.find_element_by_name('Tender[items][' + item_index + '][deliveryAddress][countryName]').send_keys(
            'test countryName')
        driver.find_element_by_name('Tender[items][' + item_index + '][deliveryAddress][region]').send_keys(
            'test region')
        driver.find_element_by_name('Tender[items][' + item_index + '][deliveryAddress][locality]').send_keys(
            'test locality')
        driver.find_element_by_name('Tender[items][' + item_index + '][deliveryAddress][streetAddress]').send_keys(
            'test streetAddress')
        driver.find_element_by_name('Tender[items][' + item_index + '][deliveryAddress][postalCode]').clear()
        driver.find_element_by_name('Tender[items][' + item_index + '][deliveryAddress][postalCode]').send_keys('11111')
        driver.find_element_by_name('Tender[items][' + item_index + '][deliveryDate][startDate]').clear()
        driver.find_element_by_name('Tender[items][' + item_index + '][deliveryDate][startDate]').send_keys(
            (datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y %H:%M"))
        driver.find_element_by_name('Tender[items][' + item_index + '][deliveryDate][endDate]').clear()
        driver.find_element_by_name('Tender[items][' + item_index + '][deliveryDate][endDate]').send_keys(
            (datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y %H:%M"))


def add_feature(driver, lot_index):
    for feature_index in range(number_of_features):
        driver.find_element_by_xpath("(//button[contains(@class, 'add_feature')])[last()-2]").click()
        feature_index_real = driver.find_element_by_xpath("(//div[contains(@class,'lots_block')]/descendant::input[contains(@name,'Tender[features][')])[last()]").get_attribute('feature_count')
        driver.find_element_by_name('Tender[features][' + feature_index_real + '][title]').send_keys('test feature title lot' + lot_index)
        driver.find_element_by_name('Tender[features][' + feature_index_real + '][description]').send_keys('hint')
        driver.find_element_by_xpath('//select[@name="Tender[features][' + feature_index_real + '][relatedItem]"]/optgroup[3]/option[1]').click()
        for enum in range(2):
            if enum != 0:
                driver.find_element_by_xpath("(//button[contains(@class,'add_feature_enum')])[last()-1]").click()
            driver.find_element_by_name("Tender[features][" + feature_index_real + "][enum][" + str(enum) + "][title]").send_keys('test ' + str(enum))
            driver.find_element_by_name("Tender[features][" + feature_index_real + "][enum][" + str(enum) + "][value]").send_keys(0 + enum)


def create_tender(tender_method):
    print('STEP 1:  Creating tender ...')
    amount = round(random.uniform(3000, 9999.99), 2)
    minimal_step_amount = round(random.uniform(0.01, 0.03) * amount, 2)
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    driver.get(locators[platform]['url'])
    driver.maximize_window()
    sign_in(driver, 'buyer@ustudio.com.ua', '123456')
    driver.get('{}/buyer/tender/create'.format(locators[platform]['url']))
    sleep(2)
    if driver.find_element_by_xpath('//button[@data-dismiss="modal"]').is_displayed():
        driver.find_element_by_xpath('//button[@data-dismiss="modal"]').click()
    select = Select(driver.find_element_by_name('tender_method'))
    select.select_by_value(tender_method)
    if number_of_lots:
        create_lot(driver)
    else:
        add_items(driver, "not created")
        driver.find_element_by_id('value-amount').send_keys(amount)
        driver.find_element_by_id('minimalstepvalue-amount').send_keys(minimal_step_amount)
        driver.find_element_by_id('tender-title').send_keys('test tender without lots {}'.format(datetime.now()))
        driver.find_element_by_id('tender-description').send_keys(
            'test tender description (tender method = {})'.format(tender_method))
        if 'EU' in tender_method:
            driver.find_element_by_id('tender-title_en').send_keys('test tender without lots EN')
            driver.find_element_by_id('tender-description_en').send_keys(
                'test tender desc EN (tender method = {})'.format(tender_method))
    for feature_index in range(number_of_features):
        driver.find_element_by_xpath("(//button[contains(@class, 'add_feature')])[last()]").click()
        feature_index_real = driver.find_element_by_xpath("(//input[contains(@class,'feature_title')])[last()]").get_attribute('id').split('-')[1]
        driver.find_element_by_name('Tender[features][' + feature_index_real + '][title]').send_keys('test feature title tender')
        driver.find_element_by_name('Tender[features][' + feature_index_real + '][description]').send_keys('hint')
        driver.find_element_by_xpath('//select[@name="Tender[features][' + feature_index_real + '][relatedItem]"]/optgroup[1]/option[1]').click()
        for enum in range(2):
            if enum != 0:
                driver.find_element_by_xpath("(//button[contains(@class,'add_feature_enum')])[last()]").click()
            driver.find_element_by_name("Tender[features][" + feature_index_real + "][enum][" + str(enum) + "][title]").send_keys('test ' + str(enum))
            driver.find_element_by_name("Tender[features][" + feature_index_real + "][enum][" + str(enum) + "][value]").send_keys(0 + enum)
    driver.find_element_by_name('Tender[tenderPeriod][endDate]').clear()
    driver.find_element_by_name('Tender[tenderPeriod][endDate]').send_keys(
        (datetime.now() + timedelta(minutes=add_min_endOfTenderPeriod)).strftime("%d/%m/%Y %H:%M"))
    if driver.find_element_by_name('Tender[enquiryPeriod][endDate]').is_displayed():
        driver.find_element_by_name('Tender[enquiryPeriod][endDate]').clear()
        driver.find_element_by_name('Tender[enquiryPeriod][endDate]').send_keys(
            (datetime.now() + timedelta(minutes=add_min_endOfEnquiryPeriod)).strftime("%d/%m/%Y %H:%M"))
    if driver.find_element_by_name('Tender[tenderPeriod][startDate]').is_displayed():
        driver.find_element_by_name('Tender[tenderPeriod][startDate]').clear()
        driver.find_element_by_name('Tender[tenderPeriod][startDate]').send_keys(
            (datetime.now() + timedelta(minutes=add_min_endOfEnquiryPeriod)).strftime("%d/%m/%Y %H:%M"))
    select = Select(driver.find_element_by_name('Tender[procuringEntity][contactPoint][fio]'))
    select.select_by_index('1')
    driver.find_element_by_xpath("//button[contains(@class,'btn_submit_form')]").click()
    wait_until_element_is_visible(driver, "//*[@tid='title']", 20)
    tender_uaid = driver.find_element_by_xpath('//*[@tid="tenderID"]').text
    print('FINISHED STEP 1')
    print('Tender uaid: {}'.format(tender_uaid))
    if not keep_browser_open:
        driver.close()
    return tender_uaid


def sign_in(driver, login, password):
    driver.find_element_by_id('loginform-username').send_keys(login)
    driver.find_element_by_id('loginform-password').send_keys(password)
    driver.find_element_by_name('login-button').click()
    sleep(2)


def make_new_bid(tender_uaid, user, password):
    print('...    placing bid by {}'.format(user))
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    driver.get(locators[platform]['url'])
    driver.maximize_window()
    sign_in(driver, user, password)
    driver.get('{}/tenders/index'.format(locators[platform]['url']))
    driver.find_element_by_name('TendersSearch[tender_cbd_id]').send_keys(tender_uaid)
    driver.find_element_by_xpath("//button[contains(text(),'Шукати')]").click()
    while tender_uaid not in driver.current_url:
        sleep(0.02)
    if platform == 'brizol':
        driver.find_element_by_xpath(
            "//*[contains(text(),'{tender_uaid}') and contains('{tender_uaid}',text())]/ancestor::div[@class='panel panel-default']/descendant::a".format(
                tender_uaid=tender_uaid)).click()
    else:
        driver.find_element_by_xpath(
            "//span[contains(text(),'{tender_uaid}') and contains('{tender_uaid}',text())]/ancestor::div[@class='thumbnail']/descendant::a".format(
                tender_uaid=tender_uaid)).click()
    if "bid_value" in driver.page_source:
        bid_amount = driver.find_elements_by_xpath("//input[contains(@class,'bid_value')]")
        for field in bid_amount:
            field.send_keys('100')
            driver.find_element_by_id('bid-selfeligible').send_keys(Keys.NULL)
            wait_until_element_is_not_visible(driver, "//div[@class='spinner']", 20)
    if 'bid_feature_select' in driver.page_source:
        list_of_features = driver.find_elements_by_xpath('//select[contains(@name,"parameter")]')
        for feature in list_of_features:
            select = Select(feature)
            select.select_by_index(1)
    checkbox_list = driver.find_elements_by_xpath("//label[contains(text(), 'Приймаю участь')]/input")
    for elem in checkbox_list:
        elem.click()
    driver.find_element_by_id('bid-selfeligible').click()
    driver.find_element_by_id('bid-selfqualified').click()
    driver.find_element_by_id('submit_bid').click()
    wait_until_element_is_visible(driver, "//div[contains(@class, 'alert-success')]", 20)
    driver.close()


def make_bids(tender_uaid):
    print('STEP 2:  Placing bids ...')
    for user in provider_users:
        make_new_bid(tender_uaid, user, provider_users[user])
    print('FINISHED STEP 2')


def wait_until_element_is_visible(driver, locator, timeout):
    maxtime = time.time() + timeout

    def check_visibility():
        visible = driver.find_element_by_xpath(locator).is_displayed()
        if visible:
            return
        elif visible is None:
            return "Element locator {} didn`t match any elements after {} seconds".format(locator, timeout)
        else:
            return "Element locator {} was not visible after {} seconds".format(locator, timeout)

    while True:
        error = check_visibility()
        if not error:
            return
        if time.time() > maxtime:
            raise AssertionError(error)
        sleep(0.02)


def wait_until_element_is_not_visible(driver, locator, timeout):
    maxtime = time.time() + timeout

    def check_hidden():
        visible = driver.find_element_by_xpath(locator).is_displayed()
        if not visible:
            return
        elif visible is None:
            return "Element locator {} didn`t match any elements after {} seconds".format(locator, timeout)
        else:
            return "Element locator {} was still visible after {} seconds".format(locator, timeout)

    while True:
        error = check_hidden()
        if not error: return
        if time.time() > maxtime:
            raise AssertionError(error)
        sleep(0.02)


parser = createParser()
namespace = parser.parse_args(sys.argv[1:])
tender_method = namespace.method
number_of_lots = namespace.lots
number_of_items = namespace.items
number_of_tenders = namespace.iterations
platform = namespace.platform
add_min_endOfEnquiryPeriod = namespace.enquiry
add_min_endOfTenderPeriod = namespace.tender

for i in range(number_of_tenders):
    tender_uaid = create_tender(tender_method)
    make_bids(tender_uaid)

print (tender_uaid)
