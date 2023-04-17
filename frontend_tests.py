
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import alert_is_present
import pytest

TEST_URL = 'https://demoqa.com/'
PROFILE_URL = TEST_URL + 'profile'
BOOKS_URL = TEST_URL + 'books'
LOGIN_URL = TEST_URL + 'login'

browser: webdriver.Chrome = webdriver.Chrome()


@pytest.fixture(scope='class')
def browser_connection():
    global browser
    browser = webdriver.Chrome()
    browser.get(TEST_URL)
    yield
    browser.quit()


@pytest.mark.usefixtures('browser_connection')
class TestUnauthorised:

    def test_01(self):
        header = browser.find_element(By.TAG_NAME, "header")
        link = header.find_element(By.TAG_NAME, "a")
        link.click()
        assert browser.current_url == TEST_URL

    def test_02(self):
        pass

    def test_03(self):
        pass

    def test_04(self):
        pass

    def test_06(self):
        browser.get(LOGIN_URL)
        username = 'vshakhrai'
        password = 'qwerty12'
        username_textinput = browser.find_element(By.ID, 'userName')
        password_textinput = browser.find_element(By.ID, 'password')
        login_btn = browser.find_element(By.ID, 'login')
        username_textinput.send_keys(username)
        password_textinput.send_keys(password)
        login_btn.click()
        output = WebDriverWait(browser, timeout=3).until(lambda d: d.find_element(By.ID, 'output'))
        assert output.text == 'Invalid username or password!'

        username_textinput = browser.find_element(By.ID, 'userName')
        password_textinput = browser.find_element(By.ID, 'password')
        login_btn = browser.find_element(By.ID, 'login')

        username_textinput.send_keys(Keys.CONTROL + "a" + Keys.DELETE)
        password_textinput.send_keys(Keys.CONTROL + "a" + Keys.DELETE)
        login_btn.click()
        assert "is-invalid" in username_textinput.get_attribute("class")


@pytest.mark.usefixtures('browser_connection')
class TestAuthorised:

    def test_06(self):
        username = 'vshakhrai'
        password = 'Qwerty1!'
        browser.get(LOGIN_URL)
        username_textinput = browser.find_element(By.ID, 'userName')
        password_textinput = browser.find_element(By.ID, 'password')
        login_btn = browser.find_element(By.ID, 'login')
        username_textinput.send_keys(username)
        password_textinput.send_keys(password)
        login_btn.click()
        WebDriverWait(browser, timeout=3).until(lambda d: browser.current_url == PROFILE_URL)
        assert browser.current_url == PROFILE_URL

    def test_08(self):
        browser.get(BOOKS_URL)
        table = browser.find_element(By.CLASS_NAME, 'ReactTable')
        select = table.find_element(By.CLASS_NAME, '-pageSizeOptions').find_element(By.TAG_NAME, 'select')
        prev_button = table.find_element(By.CLASS_NAME, '-previous').find_element(By.TAG_NAME, 'button')
        next_button = table.find_element(By.CLASS_NAME, '-next').find_element(By.TAG_NAME, 'button')
        page_jump = table.find_element(By.CLASS_NAME, '-pageJump').find_element(By.TAG_NAME, 'input')
        total_pages = table.find_element(By.CLASS_NAME, '-totalPages')
        assert select.get_attribute('value') == '10'
        assert not prev_button.is_enabled()
        assert not next_button.is_enabled()
        assert page_jump.get_attribute('value') == '1'
        assert total_pages.text == '1'
        rows = select.find_elements(By.TAG_NAME, 'option')
        rows5, rows10, rows20 = rows[:3]
        rows5.click()
        assert select.get_attribute('value') == '5'
        assert not prev_button.is_enabled()
        assert next_button.is_enabled()
        assert page_jump.get_attribute('value') == '1'
        assert total_pages.text == '2'

        next_button.click()
        assert prev_button.is_enabled()
        assert not next_button.is_enabled()
        assert page_jump.get_attribute('value') == '2'
        assert total_pages.text == '2'

        prev_button.click()
        assert not prev_button.is_enabled()
        assert next_button.is_enabled()
        assert page_jump.get_attribute('value') == '1'
        assert total_pages.text == '2'
        rows20.click()
        assert not prev_button.is_enabled()
        assert not next_button.is_enabled()
        assert page_jump.get_attribute('value') == '1'
        assert total_pages.text == '1'

    def test_09(self):
        browser.get(BOOKS_URL)
        table = browser.find_element(By.CLASS_NAME, 'ReactTable')
        search_box = browser.find_element(By.ID, 'searchBox')
        all_books = [x.text for x in table.find_elements(By.CLASS_NAME, 'action-buttons')]
        assert len(all_books) == 8
        search_text = 'Java'
        search_box.send_keys(search_text)

        result = [x.text for x in table.find_elements(By.CLASS_NAME, 'action-buttons')]
        assert len(result) == 4
        for res in result:
            assert search_text in res

    def test_11(self):
        browser.get(BOOKS_URL)
        table = browser.find_element(By.CLASS_NAME, 'ReactTable')
        all_books = table.find_elements(By.CLASS_NAME, 'action-buttons')
        assert len(all_books) == 8
        expected_url = all_books[0].find_element(By.TAG_NAME, 'a').get_attribute('href')
        all_books[0].click()
        assert browser.current_url == expected_url

        profile_wrapper = browser.find_element(By.CLASS_NAME, 'profile-wrapper')
        isbm_wrapper = profile_wrapper.find_element(By.ID, 'ISBN-wrapper')
        label = isbm_wrapper.find_element(By.ID, 'ISBN-label')
        assert label.text == 'ISBN :'

        back_button = browser.find_element(By.ID, 'addNewRecordButton')
        back_button.click()
        table = browser.find_element(By.CLASS_NAME, 'ReactTable')
        all_books = table.find_elements(By.CLASS_NAME, 'action-buttons')
        assert len(all_books) == 8

    def test_12(self):
        browser.get(BOOKS_URL)
        table = browser.find_element(By.CLASS_NAME, 'ReactTable')
        all_books = table.find_elements(By.CLASS_NAME, 'action-buttons')
        first_book = all_books[0]
        expected_url = first_book.find_element(By.TAG_NAME, 'a').get_attribute('href')
        first_book.click()
        assert browser.current_url == expected_url
        buttons = browser.find_elements(By.ID, 'addNewRecordButton')
        assert len(buttons) == 2
        add_to_collection_button = buttons[1]
        add_to_collection_button.click()
        wait = WebDriverWait(browser, timeout=3)
        alert = wait.until(alert_is_present())
        assert alert.text == 'Book added to your collection.'
        browser.switch_to.alert.accept()
        add_to_collection_button.click()
        alert = wait.until(alert_is_present())
        assert alert.text == 'Book already present in the your collection!'
        browser.switch_to.alert.accept()

    def test_17(self):
        browser.get(PROFILE_URL)
        buttons_wrap = browser.find_element(By.CLASS_NAME, 'buttonWrap')
        delete_all_button = buttons_wrap.find_elements(By.TAG_NAME, 'button')[2]
        delete_all_button.click()
        modal = browser.find_element(By.CLASS_NAME, 'modal-dialog')

        cancel_button = modal.find_element(By.ID, 'closeSmallModal-cancel')
        cancel_button.click()
        delete_all_button.click()
        modal = browser.find_element(By.CLASS_NAME, 'modal-dialog')
        ok_button = modal.find_element(By.ID, 'closeSmallModal-ok')
        ok_button.click()
        wait = WebDriverWait(browser, timeout=3)
        wait.until(alert_is_present())
        browser.switch_to.alert.accept()

