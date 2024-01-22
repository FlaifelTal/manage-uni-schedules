import json
import os
from datetime import datetime, timedelta

# variables
filename = "CEStudyPlan.txt"
study_plan_dict = {}
courses_R = []  # create an empty list to store the course code and score pairs
scores_R = []  # create an empty list to store the scores
courses_codes_R = []  # create an empty list to store the course codes
passed_courses_R = []  # create an empty list to store the passed course codes
# create a new dictionary to hold the updated study plan
updated_study_plan = {}
CourseBrowser_1 = {}
CourseBrowser_2 = {}
CourseBrowser_3 = {}
next_semester_schedule = {}
course_codes_hour = {}
course_codes_pre={}
course_list = []

with open('CourseBrowser_1.json') as file:
    CourseBrowser_1 = json.load(file)
with open('CourseBrowser_2.json') as file:
    CourseBrowser_2 = json.load(file)
with open('CourseBrowser_3.json') as file:
    CourseBrowser_3 = json.load(file)

# **********************************************************************
def read_file():
    with open(filename) as file:

        header = file.readline().strip().split(",")
        year_index = header.index("Year")
        sem_index = header.index("Semster")
        code_index = header.index("CourseCode")
        prereq_index = header.index("Prerequisists")

        for line in file:
            values = line.strip().split(",")
            year = values[year_index]
            sem = values[sem_index]
            code = values[code_index]
            prereq = ", ".join(values[prereq_index:]) if len(values) > prereq_index else ""
            if year not in study_plan_dict:  # checks if the year has a dictionary
                study_plan_dict[year] = {}  # if not it creates one

            if sem not in study_plan_dict[year]:  # checks if the semester has a dictionary
                study_plan_dict[year][sem] = {}  # if not it creates one
            if code not in study_plan_dict[year][sem]:
                study_plan_dict[year][sem][code] = {}  # adds all the course codes and the Prerequisists of exists

            # add code and prereq to course_codes_dict if not already present
            if code not in course_codes_hour:
                # Extract the credit hours from the second number of the course code
                code_no_whitespace = code.strip()  # remove any whitespace characters
                if len(code_no_whitespace) >= 6:  # check that the code has at least 6 characters
                    credit_hours = int(code_no_whitespace[5])
                else:
                    credit_hours = 0  # set to 0 if the code doesn't have a second number

                #course_codes_hour[code] = credit_hours
                course_codes_hour[code] =  credit_hours
                course_codes_pre[code] =  prereq




# **********************************************************************
def print_plan():
    global courses, sem
    print("year\tSemester\tCourses")
    print("----\t---------\t-------")
    for year in sorted(study_plan_dict):
        for sem in sorted(study_plan_dict[year]):
            courses = []
            for code in study_plan_dict[year][sem]:
                courses.append(code)
                if study_plan_dict[year][sem][code]:
                    courses.append(study_plan_dict[year][sem][code])
            print(f" {year}\t\t\t{sem}\t\t{','.join(courses)},")


# **********************************************************************
def passed_courses():
    while True:
        # check/open student record
        file_R = input("Please enter the name of the input file : ")
        if os.path.exists(file_R):
            print(file_R, "exists")

            with open(file_R) as fileR:
                next(fileR)  # skip the header row
                for i in fileR:
                    values_R = i.strip().split(",")
                    codes = values_R[2:]  # select all elements from index 2 to the end
                    for code_R in codes:
                        course_code_R, scores = code_R.split(":")
                        courses_R.append((course_code_R, scores))
                        courses_codes_R.append(course_code_R)
                        scores_R.append(scores)
                        if int(scores) >= 60:  # check for passes courses courses
                            passed_courses_R.append(course_code_R)


            for year in study_plan_dict:
                for sem in study_plan_dict[year]:
                    courses = []
                    for code in study_plan_dict[year][sem]:
                        course_str = code
                        if code in passed_courses_R:  # check if the courses in the dict(original recored) exists in the passes courses
                            course_str = f"\033[32m{code}\033[0m"  # set color to green it true ANSI escape codes to modify the text color of the course codes
                        courses.append(course_str)
                    print(
                        f"{year + '         '} {sem + '      '}     {', '.join(courses)}")  # print the edited recored while considering the passes courses


            create_plan()


        else:
            print(file_R, "does not exist. Please try again.")


# **********************************************************************
def update_study_plan():  # creating a new dictionary with the updated courses ( excludo=ing the passed courses)
    # iterate over the keys and values in study_plan_dict
    for year in study_plan_dict:
        updated_study_plan[year] = {}
        for sem in study_plan_dict[year]:
            updated_study_plan[year][sem] = []

            # iterate over the courses in the current semester and add them to the updated study plan
            for code in study_plan_dict[year][sem]:
                if code not in passed_courses_R:
                    if code not in course_list:

                        updated_study_plan[year][sem].append(code)


# **********************************************************************


def create_plan():
    global max_credits

    update_study_plan()
    num_sems = input("for how many semesters u want a schedule: ")

    # Take input for minimum number of free days per week for each semester

    for sem_i in range(1, int(num_sems) + 1):

        if (int(sem_i) % 3 != 0):
            min_free_days = input(f"Enter the minimum number of free days per week for semester {sem_i}: ")


            max_credits = input(f"Enter the maximum number of credits for semester {sem_i}: ")


            #insert schedule

        elif (int(sem_i) % 3 == 0):
            # Take input for maximum number of credits for the summer semester
            max_credits = input("Enter the maximum number of credits for the summer semester: ")

        get_courses_within_hour_limit(course_codes_hour, max_credits,course_codes_pre)
        make_schedule()


    output_file = input("Do you want to save the schedules to a text file? (yes / no)")
    if output_file.lower() == "yes":
        with open("SuggestedCourses.txt", 'w') as output_file_obj:
            output_file_obj.write(str(course_list))
            print("Schedules saved to file.")

    else:
        choice = input("Do you want to continue?(yes/no)")
        if choice.lower() == "yes":
            print("continue")
        else:
            exit(0)



def get_courses_within_hour_limit(course_codes_hour , max_hours=None, prerequisites={}):
    total_hours = 0
    #course_list = []
    for course in course_codes_hour:
        if prerequisites_met(course, prerequisites):
                if course not in passed_courses_R:
                    total_hours += course_codes_hour[course]
                    if int(total_hours) >= int(max_hours):
                        break
                    course_list.append(course)
    print_incolor()
    update_study_plan()
    update()

####################################
def prerequisites_met(course_code, prerequisites): #checking if the prerequests are met for the coursee
    if prerequisites[course_code] == '':
        return True

    for prereq_code in prerequisites[course_code].split(', '):
        if prereq_code not in passed_courses_R:
                return False

    return True
####################################
def print_incolor():


    for year in study_plan_dict:
        for sem in study_plan_dict[year]:
            courses = []
            for code in study_plan_dict[year][sem]:
                course_str = code
                course_st = code
                if course_str in passed_courses_R: # check if the courses in the dict(original recored) exists in the passes courses
                    course_str = f"\033[32m{code}\033[0m"  # set color to green it true ANSI escape codes to modify the text color of the course codes
                if course_str in course_list:
                    course_str = f"\033[91m{code}\033[0m"  # set color to green it true ANSI escape codes to modify the text color of the course codes

                courses.append(course_str)


            print(
                f"{year + '         '} {sem + '      '}     {', '.join(courses)}")  # print the edited recored while considering the passes courses

#****************************************************

def update():
    global passed_courses_R

    passed_courses_R += course_list

#*************************************************************************
def make_schedule():
    # call make schedule in createplan
    with open('CourseBrowser_1.json') as file:
        CourseBrowser_1 = json.load(file)
    with open('CourseBrowser_2.json') as file:
        CourseBrowser_2 = json.load(file)
    with open('CourseBrowser_3.json') as file:
        CourseBrowser_3 = json.load(file)

    browser = CourseBrowser_1
    course_schedule = {}
    for key, value in browser.items():
        if 'Lecture' in key or 'Lab' in key:
            code = key.split('-')[0]
            if code not in course_schedule:
                course_schedule[code] = {}
            if 'Lab' in key:
                course_schedule[code]['Lab'] = value
            else:
                day = key.split('-')[1]
                course_schedule[code][day] = value

    create_schedule1(course_list, course_schedule)


# def create_schedule1(course_list, course_schedule):
#     # create an empty schedule
#     schedule = []

#     # iterate over the course list
#     for code in course_list:
#         # get the lecture and lab times for the course
#         browser = course_schedule.get(code, {})
#         monday = browser.get('M', '')
#         tuesday = browser.get('T', '')
#         wednesday = browser.get('W', '')
#         thursday = browser.get('R', '')
#         friday = browser.get('F', '')
#         lab = browser.get('Lab', {})
#         lab_time = list(lab.values())[0] if lab else ''

#         # append the course and its times to the schedule
#         schedule.append((code, monday, tuesday, wednesday, thursday, friday, lab_time))

#     # print the schedule
#     print(
#         f"{'Course':<10} {'Monday':<20} {'Tuesday':<20} {'Wednesday':<20} {'Thursday':<20} {'Friday':<20} {'Time':<20}")
#     for course in schedule:
#         print(
#             f"{course[0]:<10} {course[1]:<20} {course[2]:<20} {course[3]:<20} {course[4]:<20} {course[5]:<20} {course[6]:<20}")


# ************************************************



#***************************************************************
##### MAIN
read_file()
print_plan()
passed_courses()
