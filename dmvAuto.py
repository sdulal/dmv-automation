#! python3
"""
This program allows the user to quickly get the next closest appointment time
for written permit tests from the Department of Motor Vehicles. The user inputs
his/her name and phone number, then the program will find the next available
appointment time.

This program requires Python 3. The user must have a Firefox browser.
"""

import sys
from selenium import webdriver
from selenium.webdriver.support.ui import Select

__author__ = "Shafqat Dulal"
__version__ = "1.0.0"

"""This is the starting URL from which the browser will begin its automation."""
url = "https://www.dmv.ca.gov/foa/clear.do?goTo=officeVisit"

"""The browser. This will control Firefox during the course of the program."""
browser = None

"""Text to check for when deciding an appointment time's availability."""
available = "An appointment for the date and/or time selected is available"

"""The date/time parameters that will be used in figuring out the closest
available time.
"""
month = day = year = time = None


"""Mappings from the position of a month in a year to name of a month
and vice versa.
"""
numMonths = { 1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 
            6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 
            11: "November", 12: "December" }
monthNums = {v: k for k, v in numMonths.items()}

"""Mappings from the numerical hour under the 24-hour system (sort of)
to military time and vice versa.
"""
hourVals = { 8: "0800", 8.5: "0830", 9: "0900", 9.5: "0930", 10: "1000", 
            10.5: "1030", 11: "1100", 11.5: "1130", 12: "1200", 12.5: "1230", 
            13: "1300", 13.5: "1330", 14: "1400", 14.5: "1430", 15: "1500", 
            15.5: "1530", 16: "1600", 16.5: "1630" }
valHours = {v: k for k, v in hourVals.items()}

def click_by_id(id_name):
    """Convenience method for clicking an element on the browser the element's
    id tag.
    """
    try:
        browser.find_element_by_id(id_name).click()
    except:
        print("Failed to click on the element with id: " + id_name)
        sys.exit()

def click_by_name(name):
    """Convenience method for clicking an element on the browser the element's
    name information.
    """
    try:
        browser.find_element_by_name(name).click()
    except:
        print("Failed to click on the element with name: " + name)
        sys.exit()


def click_by_xpath(xpath):
    """Convenience method for clicking an element on the browser the element's
    xpath.
    """
    try:
        browser.find_element_by_xpath(xpath).click()
    except:
        print("Failed to click on the element with xpath: " + xpath)
        sys.exit()

def type_into_form(form_name, text):
    """Convenience method for typing information into some form.
    """
    try:
        browser.find_element_by_name(form_name).send_keys(text)
    except:
        print("Could not find a form with name: " + form_name)
        sys.exit()


def increment_month():
    """Increments the month, changing the year when necessary.
    """
    global months
    global numMonths
    global monthNums
    if month == "December":
        month = "January"
        year += 1
    else:
        month = numMonths[monthNums[month] + 1]


def increment_day():
    """Increments the day, changing the month when necessary.
    """
    global day
    if day == 31:
        day = 1
        increment_month()
    else:
        day += 1
    return day


def increment_time():
    """Increments the time, changing the day when necessary.
    """
    global time
    global hourVals
    global valHours
    if time == "1630":
        time = "0800"
        increment_day()
    else:
        time = hourVals[valHours[time] + 0.5]

def get_starting_time():
    """When the appointment system first loads up, the user is presented with
    the first available time. This function reports the datetime information
    to the terminal and takes into account the earliest time when finding
    next closest times.
    """
    global month, day, year, time
    try:
        first_date_text = browser.find_elements_by_class_name("alert")[1].text
        split = first_date_text.split()
        month = split[1]
        day = int(split[2][:-1])
        year = int(split[3])
        time = "0800"
        print("The first available time is:\n" + first_date_text)
    except Exception as e:
        print(e)
        sys.exit()

def find_next_closest():
    """Finds the next closest time that the DMV website reports.
    """
    global month, day, year, time
    global available
    page_text = ""
    try:
        while page_text != available:
            increment_time()
            dateField = browser.find_element_by_class_name("ng_cal_input_field")
            dateField.send_keys(month + " " + str(day) + " " + str(year))
            timeSelect = Select(browser.find_element_by_id("requestedTime"))
            timeSelect.select_by_value(time)
            click_by_name("checkAvail")
            page_text = browser.find_element_by_class_name("alert").text
        next_date_text = browser.find_elements_by_class_name("alert")[1].text
        print("The next available time is:\n" + next_date_text)
    except:
        print("An error occurred while finding the next closest time.")
        sys.exit()


def login(first_name, last_name, phone):
    """Logs into the DMV appointment system for written permit tests.
    This function makes use of the user's name and phone number.
    """
    global url, browser
    try:
        area, prefix, suffix = phone[:3], phone[3:6], phone[6:10]
        browser = webdriver.Firefox()
        browser.get(url)

        select = Select(browser.find_element_by_name('officeId'))
        select.select_by_visible_text("SANTA CLARA")

        click_by_id("one_task")
        click_by_id("taskRWT")
        form_names = ["firstName", "lastName", "telArea", "telPrefix", "telSuffix"]
        inputs = [first_name, last_name, area, prefix, suffix]
        for form, text in zip(form_names, inputs):
            type_into_form(form, text)
        click_by_xpath("//input[@type='submit']")
    except Exception as e:
        print("An error occurred while trying to log in.")
        sys.exit()

def request_input():
    """Requests input from the user regarding getting the next time
    and returns the result.
    """
    user_input = input("Do you wish to get the next closest time?\n"
                        "Type 'Y' to continue. \n").upper()
    return user_input

def main(info):
    """Starts the program. Allows the user to continuously ask for the next
    closest time.
    """
    try:
        if sys.version_info[0] < 3:
            print("Please use Python 3.0 or above.")
            return 0
        first_name = info[1]
        last_name = info[2]
        phone = info[3]
    except:
        print("You must provide information in this format:")
        print("(first) (last) (phone number, no formatting)")
        return 1
    try:
        login(first_name, last_name, phone)
        get_starting_time()
        get_next = request_input()
        while get_next == "Y":
            print("Getting the next closest time...")
            find_next_closest()
            get_next = request_input()
        print("Exiting.")
    except:
        return 2

"""Calls the main function to start the program. Exits when the user quits
or an error occurs.
"""
if __name__ == "__main__":
    sys.exit(main(sys.argv))