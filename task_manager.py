"""
Task Manager

A program to manage tasks for a group of users.
Users can create, edit and mark complete their tasks.

Changelog:

- Original code fixed and refactored. e.g. datetime errors and ";" being used in the program not ","
- reg_user, add_task, view_all and view_min functions created to simplify the main program loop.
- The original program only read from the *.txt files once after the program had been started and then never again, relying on
task_list, but the program is for multiple users all of whom can make changes. This has real potential for users overwriting 
one another's changes and means that users would have to restart the program in order to see any updates from other users. 
The refactored code uses the .txt file as the single source of truth meaning reports and views will reflect changes as soon as 
they're made and the program won't write changes if the .txt file has been altered since it was last read.
- Created User class to manage handling of users as well as .tasks() & .stats() methods to handle logic for report generation
- Added a sorting function to prioritise urgent tasks i.e. user will start with most urgent on screen and scroll up 
towards less urgent pending tasks and then completed tasks.
"""

import os
from datetime import datetime, date

DATETIME_STRING_FORMAT = "%d %b %Y"  # Date format incorrect, the order should be date, month, year - month should be %b and there should be spaces, not '-'

#########################
# Task and User Classes
#########################


class Task:
    """
    A class to represent a task that is assigned to a user.


    Attributes
    ----------
    username: String
    title: String
    description: String
    due_date: DateTime
    assigned_date: DateTime
    completed: Boolean

    Methods
    -------
    from_string(task_str):
        Creates a task object from a correctly formatted string
    to_string():
        Creates a correctly formatted string from the task object
    display():
        Generates a string summary of the task that can be displayed on screen in a nice format
    mark_complete():
        Updates a pending task to be a completed task.
    update_assignee(new_assignee):
        Updates the task assignee to new_assignee
    update_due_date(new_due_date):
        Updates the task due date to new_due_date
    update(original_task_string=""):
        Creates a new task, or update an exisitng record if an original_task_string is passed.
    """
    def __init__(self, username = None, title = None, description = None, due_date = None, assigned_date = None, completed = None):
        """
        Constructs all the necessary attributes for the user object

        Inputs:
        username: String
        title: String
        description: String
        due_date: DateTime
        assigned_date: DateTime
        completed: Boolean
        """
        self.username = username
        self.title = title
        self.description = description
        self.due_date = due_date
        self.assigned_date = assigned_date
        self.completed = completed

    def from_string(self, task_str):
        """
        Convert from string in tasks.txt to object

        Inputs:
        task_str: String
        """
        tasks = task_str.split(", ")  # task_str needs to be split by ", " rather than by ";" to match tasks.txt
        username = tasks[0]
        title = tasks[1]
        description = tasks[2]
        due_date = datetime.strptime(tasks[3], DATETIME_STRING_FORMAT)  # Convert the date string into a datetime object
        assigned_date = datetime.strptime(tasks[4], DATETIME_STRING_FORMAT)  # Convert the date string into a datetime object
        completed = True if tasks[5] == "Yes" else False  # Convert the Yes/No into a boolean value
        self.__init__(username, title, description, due_date, assigned_date, completed)  # Create the new Task object

    def to_string(self):
        """
        Convert to string for storage in tasks.txt

        Return:
        task_string: String - Task object details formatted into a string format for writing to tasks.txt 
        """
        str_attrs = [
            self.username,
            self.title,
            self.description,
            self.due_date.strftime(DATETIME_STRING_FORMAT),  # Convert the datetime object into a string
            self.assigned_date.strftime(DATETIME_STRING_FORMAT),  # Convert the datetime object into a string
            "Yes" if self.completed else "No"  # Convert the boolean value back into Yes/No
        ]
        task_string = ", ".join(str_attrs)  # Changed from ";" to ", " to match tasks.txt
        return task_string

    def display(self):
        """
        Display object in readable format

        Return:
        disp_str: String - A nicely formatted summary of the task that can be displayed on screen
        """
        disp_str = f"Task: \t\t {self.title}\n"
        disp_str += f"Description: \t {self.description}\n"
        disp_str += f"Assigned to: \t {self.username}\n"
        disp_str += f"Date Assigned: \t {self.assigned_date.strftime(DATETIME_STRING_FORMAT)}\n"  # Convert datetime object into a readable string
        disp_str += f"Due Date: \t {self.due_date.strftime(DATETIME_STRING_FORMAT)}\n"  # Convert datetime object into a readable string
        # Calculate the completion status of each task using the due date and display the appropriate context
        disp_str += "Status: \t " + ("COMPLETED" if self.completed else "PENDING") + (" & OVERDUE" if self.due_date < datetime.now() and not self.completed else "")
        return disp_str

    def mark_complete(self):
        """
        Mark a task complete and write this change to tasks.txt
        """
        original_task = self.to_string()  # Convert the original task into a string to use as a unique identifier to update tasks.txt
        self.completed = True  # Change the completion status to True
        self.update(original_task)  # Call the update() function to make the changes to tasks.txt

    def update_assignee(self, new_username):
        """
        Update the user assigned to a task and write this change to tasks.txt

        Input:
        new_username: String
        """
        # Call the get_all_user+data function and check that the username entered by the user already exists in the system.
        if new_username in [user.username for user in get_all_user_data()]:
            original_task = self.to_string()  # Convert the original task into a string to use as a unique identifier to update tasks.txt
            self.username = new_username  # Update the task assignee 
            self.update(original_task)  # Call the update() function to make the changes to tasks.txt
        else:
            input("That user does not exist in our system.\n\nPress ENTER to return to the list of tasks.")

    def update_due_date(self, new_due_date):
        """
        Update the due date and write this change to tasks.txt

        Input:
        new_due_date: datetime
        """
        original_task = self.to_string()  # Convert the original task into a string to use as a unique identifier to update tasks.txt
        self.due_date = new_due_date  # Update the due date to the new value
        self.update(original_task)  # Call the update() function to make the changes to tasks.txt

    def update(self, original_task_string=""):
        """
        Take a new or updated Task object and write it to the tasks.txt file
        If the function is passed an 'original_task_string' this is used as a unique identifier to find and replace the exisitng task
        If no 'origial_task_string' is passed, a new task is created.

        Input:
            optional_task_string: String, optional
        """
        if original_task_string:  # If the original task is passed as a string, we're applying updates to that task (as opposed to creating a new one)
            task_list = get_all_task_data()  # Retrieve the full list of tasks
            # Find the original task in the task list and replace it with the new task ready to write to tasks.txt
            new_task_list = [self.to_string() if original_task_string == task.to_string() else task.to_string() for task in task_list]
            if task_list != new_task_list:  # If changes have been made to the original task list we write them to tasks.txt
                with open("tasks.txt", 'w') as task_file:
                    task_file.write("\n".join(new_task_list))
            # If no changes were made to the original task list above, it means that changes have been made to that task in tasks.txt
            # in the time that we've been making changes so the user needs to refresh the task list before they can make their changes.
            else: 
                input("There was a problem trying to update your task. Please try again./n/nPress ENTER to return to the main menu.")
        else:
            # If no task string is passed it means we are simply creating a new task, appending a string to tasks.txt
            with open("tasks.txt", "a") as task_file:
                task_file.write("\n"+self.to_string())
        # Confirmation screen showing the changes have been made
        input(f"""\033cSuccess. Your new/updated task:
-----------------------------------
{self.display()}
-----------------------------------
Press ENTER to return to the main menu.""")


class User:
    """
    A class to represent users.


    Attributes
    ----------
    username: String
    password: String

    Methods
    -------
    from_string(task_str):
        Creates a user object from a correctly formatted string
    to_string():
        Creates a correctly formatted string from the user object
    new():
        Adds a new user to the user.txt file
    tasks():
        Returns a list of tasks that have been assigned to that user
    stats():
        Returns a string of nicely formatted statistics about that user's task completion rate
    validate(username,password):
        Used to log users in, checks that the username and password match an exisitng user in user.txt
    """
    def __init__(self, username=None, password=None):
        """
        Constructs all the necessary attributes for the user object

        Inputs:
        username: String
        password: String
        """
        self.username = username
        self.password = password
        
    def from_string(self, user_str):
        """
        Convert user entries in users.txt from string to object
        """
        user = user_str.split(", ")  # task_str needs to be split by ", " rather than by ";" to match users.txt
        username = user[0]
        password = user[1]
        self.__init__(username, password)

    def to_string(self):
        """
        Convert user objects to strings for storage in tasks.txt

        Return: 
            user_str: String - The user object converted to a string format to be stored in user.txt
        """
        str_attrs = [
            self.username,
            self.password
        ]
        user_str = ", ".join(str_attrs)  # Changing from ";" to ", " to match users.txt
        return user_str
    
    def new(self):
        """
        Save a new user to users.txt, appending to the existing file
        """
        with open("user.txt", "a") as out_file:  # Append the new user to the users.txt file
            out_file.write("\n"+self.to_string())
        # Confirmation message summarising the new user data
        input(f"""\033cYou have successfully added the following user to the system:
        
        username: {self.username}
        password: {self.password}
        
Please share their login details with them so that they can begin to use the system.

Press ENTER to return to the home screen.""")

    def tasks(self): 
        """
        Returns a list of a user's tasks

        Returns:
        user_tasks: List(Tasks)
        """
        task_list = get_all_task_data()  # Retrieve the full task list
        user_tasks = [t for t in task_list if t.username == self.username]  # Make a new list of tasks assigned to the selected user
        return user_tasks  # return the list of tasks that belong to this user

    def stats(self):
        """
        Returns a breakdown of the users task stats

        Returns:
        stats_dict: Dict - a dictionary of statistics about a users task status
        """
        total_tasks = get_all_task_data()  # Get the full task list
        total_user_tasks = self.tasks()  # Get the list of tasks assigned to this user
        stats_dict = {}  # Create an empty dict to return with data
        stats_dict['total_tasks'] = len(total_tasks)  # Count the total number of tasks
        stats_dict['total_user_tasks'] = len(total_user_tasks)  # Count the number of tasks assigned to this user
        # Calculate the percentage of tasks assigned to this user
        stats_dict['percentage_of_total_tasks'] = round(( len(total_user_tasks) / len(total_tasks) ) * 100,2)
        if stats_dict['total_user_tasks'] > 0:  # If the user has at least one task (to avoid dividing by 0)
            # Calculate the percentage of tasks that the user has completed
            stats_dict['percentage_tasks_completed'] = (len([t for t in total_user_tasks if t.completed == True])/len(total_user_tasks))*100
            # Calculate the percentage of tasks that are incomplete
            stats_dict['percentage_pending_tasks'] = (len([t for t in total_user_tasks if t.completed == False])/len(total_user_tasks))*100
            # Calculate the number of incomplete tasks that are also overdue
            stats_dict['percentage_overdue_tasks'] = (len([t for t in total_user_tasks if t.completed == False and t.due_date < datetime.now()])/len(total_user_tasks))*100
        return stats_dict  # Return the dict of user stats

    def validate(username,password):
        """
        Check that a username and password match what's in users.txt when a user logs in

        Returns:
        user: User - returns the user object for the successfully validated user
        """
        for user in get_all_user_data():  # iterate over each user in user.txt
            # If the username and password match an entry, return the user object
            if username == user.username and password == user.password:
                return user

#########################
# Program Functions
#########################


def sort_tasks(task_list):
    """
    Take a list of tasks and sort them to show completed tasks first, 
    then pending, with the most overdue tasks at the end of the list.

    Input:
    task_list: List[Tasks] 

    Returns:
    task_list: List[Tasks] 
    """
    task_list = sorted(task_list, key=lambda x: x.due_date, reverse=True)  # Sort tasks by due date
    task_list = sorted(task_list, key=lambda x: x.completed, reverse=True)  # Sort tasks by completion status
    return task_list  # Return the sorted task list


def get_all_task_data():
    """
    Retrieve all tasks from tasks.txt and return them as a list.

    Returns:
    all_tasks: List[Tasks]
    """
    all_tasks = []  # Create an empty list to store tasks objects in
    with open("tasks.txt", 'r') as task_file:  # Open tasks.txt
        task_data = task_file.read().split('\n')  # Split the text file into a list with each line as an item
        for task in task_data:  # For each task string
            new_task = Task()  # Create a new Task object
            new_task.from_string(task)  # Map the task string to the task object
            all_tasks.append(new_task)  # Add the task object to the new list
    return all_tasks  # return the new list of task objects


def get_all_user_data():
    """
    Retrieve the full list of users from users.txt and return it as a list

    Returns:
    all_users: List[Users]
    """
    all_users = []  # Create an empty list to store user objects in
    with open("user.txt", 'r') as user_file:  # Open user.txt
        user_data = user_file.read().split('\n')  # Create a list of each user string by splitting on newlines
        for user in user_data:  # For each user string
            new_user = User()  # Create a new User object
            new_user.from_string(user)  # Map the user string to the user object
            all_users.append(new_user)  # Add the user object to the new list
    return all_users  # Return the new list


def validate_string(input_str):
    """
    Checks that strings don't contain characters that will break the functionality of the program, returns True if string is safe, False otherwise

    Returns:
    boolean
    """
    if ", " in input_str:  # Changed from ";" to ", " to work with the .txt files
        print("Your input cannot contain ', ' characters, please enter something different.")  # Changing from ";" to ", " to work with the .txt files
        return False
    return True

#########################
# View Functions
#########################


def reg_user():
    """
    Allow the admin account to add new users to the system. Promt user for:
        - Username
        - Password
    """
    user_data = get_all_user_data()  # Retrieve the full list of users from the user.txt file
    if logged_in_user.username == 'admin':  # Confirm that the current user is the admin
        while True:
            new_username = input("New Username: ")  # Ask the user to input a username
            if new_username in [user.username for user in user_data]:  # Confirm if the username already exists
                print("That username already exists, please choose another.")  # If it already exists promt the user to try again.
                continue
            if not validate_string(new_username):  # If the name doesn't already exist, check that it doesn't contain problematic characters e.g. ", "
                continue
            break

        while True:
            # Request input of a new password
            new_password = input("New Password: ")
            # If password is not safe for storage the validate_string() method will return an error message
            if not validate_string(new_password):
                continue  # send user back to start of while loop

            # If password passes validation, request the user to enter it again as confirmation.
            confirm_password = input("Confirm Password: ")

            # Check if the new password and confirmed password are the same.
            if new_password == confirm_password:
                # If they are the same create the new User in the user.txt file,
                new_user = User(new_username,new_password)
                new_user.new()   
                break  # End the loop
            else:  # If passwords dont match, prompt the user to try again
                print("Passwords do not match, please try again.")
                continue
    else:  # If the user is not the admin, let them know
        input("\nYou do not have permission to register users, please contact an administrator.\nPress enter to return to the main menu")
       

def add_task():
    """
    Prompt a user for the following: 
        -A username of the person whom the task is assigned to,
        -A title of a task,
        -A description of the task and 
        -the due date of the task.
    """
    while True:
        # Prompt the user to input the name of the person that the task will be assigned to
        task_username = input("Name of person assigned to task: ")
        # If the user exists, accept the entry, break the loop and move to the next question
        if task_username in [user.username for user in get_all_user_data()]: 
            break
        else:  # If the user doesn't exist, prompt them to input another name
            print("\nThat user does not exist. Please enter a valid username\n")

    while True:
        # Prompt the user to input a title for the task
        task_title = input("\nTitle of Task: ")
        # Check that the string meets the requitements for storage in tasks.txt, if it doesn't prompt the user again
        if validate_string(task_title):
            break

    while True:
        # Prompt the user to input a description for the task
        task_description = input("\nDescription of Task: ")
        # Check that the string meets the requitements for storage in tasks.txt, if it doesn't prompt the user again
        if validate_string(task_description):
            break

    while True:
        # Prompt the user to enter a due date, check that the date entered is a valid format and doesn't produce an error
        try:
            task_due_date = input("\nDue date of task (DD MMM YYYY): ")
            due_date_time = datetime.strptime(task_due_date, DATETIME_STRING_FORMAT)  # If format doesn't produce an error, loop will break
            break
        except ValueError:  # If an error is produced as a result of the date format, print an error message and prompt user again
            print("\n!! Invalid datetime format. Please try again with the correct format - e.g. 24 Dec 2022")

    # Obtain and parse current date
    curr_date = date.today()
    
    # Create a new Task object and save to tasks.txt
    new_task = Task(task_username, task_title, task_description, due_date_time, curr_date, False)
    new_task.update()  # Save to the tasks.txt file


def view_all():
    """
    Retrieve all tasks from tasks.txt and print them to screen
    """
    task_list = sort_tasks(get_all_task_data())  # Retreive the full task list and sort it using sort_tasks()

    print("-----------------------------------\nALL TASKS\n-----------------------------------") # Print a title

    if len(task_list) == 0:  # If there are no tasks print a simple message
        print("There are no tasks.")
        print("-----------------------------------")

    for t in task_list:  # Iterate over the full list of tasks and call the display() method to print each one
        print(t.display()+"\n-----------------------------------")


def view_mine():
    """
    Retrieve all the tasks for the logged in user.
    Prompt user to:
        - Select a task.
            - Mark task as complete (if not already complete)
            - Edit task including who it's assigned to and the due date (if not already complete)
    """
    while True:
        # Call the user.tasks() method to return all tasks assigned to that user.
        my_tasks = sort_tasks(logged_in_user.tasks())  # Sort to show highest priority tasks at bottom of list
        if my_tasks:  # Check that the number of tasks isn't zero.
            # Print out all the tasks for the logged in user
            print(f"\033cAll {logged_in_user.username}'s tasks:\n")  # Print a title
            # Use enumerate to assign each task a number that the user can use to select it with
            for idx,task in enumerate(my_tasks):
                print("TASK " + str(idx + 1))  # Print the task number
                print(task.display())  # Display each task
                print("-----------------------------------")
            # Prompt the user to select a task that they would like to edit
            try:
                option = int(input("\nSelect a task by it's number, or enter -1 to go back to the main menu.\n\nTask Number: "))
                if 0 < option <= len(my_tasks):
                    selected_task = my_tasks[option-1]
                elif option == -1:  # If they select -1 break the loop and return to main menu
                    break
                else:  # If users enter integers outside of the range, send them back to the start of the loop
                    input("\nThat value is not in range, press ENTER and try again.")
                    continue
            except ValueError:  # Catching erorrs if the user doesn't enter an integer
                input("\nThat value was not a valid integer, press ENTER and try again.")
                continue  # Send user back to the start of the loop
            
            # Print the task details to the screen and then ask the user to confirm what they would like to edit
            response = input(f"""\033cYou have selected Task {option}. 
-----------------------------------            
{selected_task.display()} 
-----------------------------------
Would you like to:
    
e - Edit this task
c - Mark it complete?
x - Exit to menu

Your choice: """).lower()
            if response == 'c':  # If user responds with c run the mark_complete task method
                selected_task.mark_complete()
                continue    
            elif response == 'e':  # If the user selects to edit the task, present them with two further options.
                if selected_task.completed:  # If the task is already complete, inform the used that it can no longer be edited and return them to start of loop
                    input(f"\n\"{selected_task.title}\" is complete and can no longer be edited. Press ENTER to continue.\n")
                    continue
                else:  # If the task is incomplete, present the user with the option to change the due date and to reassign to another user
                    edit_choice = input("\nWhat would you like to edit:\n\nu - the User assigned to the task\nd - the due date\n\nYour choice: ")
                    if edit_choice.lower() == 'u': # If the user selects to change the user
                        while True:
                            # Prompt the user to input a new task assignee
                            new_assignee = input("Who is now assigned to this task? ")
                            # Confirm that the user is registered already
                            if new_assignee in [user.username for user in get_all_user_data()]: 
                                break
                            else:  # If the user is not confirmed, communicate this then allow them to try again
                                print("\nUser does not exist. Please enter a valid username.\n")
                        selected_task.update_assignee(new_assignee)  # If the user is valid, run the update_assignee task method, passing in the username as an argument
                    elif edit_choice.lower() == 'd':  # If the user selects to change the due date
                        while True:
                            try:  # Prompt the user to input a new date in the correct format
                                new_due_date = input("\nWhat is the new due date of the task (DD MMM YYYY): ")
                                new_date_time = datetime.strptime(new_due_date, DATETIME_STRING_FORMAT)  # Convert the date string to a datetime object
                                selected_task.update_due_date(new_date_time)  # Run the update_due_date Task method passing in the datetime object as an argument
                                break  # end the loop
                            except ValueError:  # Catch date validation problems, communicate the problem and prompt user to try again
                                print("Invalid datetime format. Please use the format specified")
        else:  # If the user has no tasks, prompt them to create some and send them back to the main menu
            print("\033cYou have no tasks. Press 'a' at the main menu to create your first task!")
            print("-----------------------------------")
            input("Press ENTER to return to the main menu.")
            break  # End the loop


def generate_reports(confirmation=True):
    """
    Create task_overview.txt and user_overview.txt files and populate them with the latest information from the system
    """
    if not os.path.exists("task_overview.txt"):  # Create task_overview.txt if it doesn't already exist
        with open("task_overview.txt", "w") as default_file:
            pass

    if not os.path.exists("user_overview.txt"):  # Create user_overview.txt if it doesn't already exist
        with open("user_overview.txt", "w") as default_file:
            pass
    
    # Calculate the task overview stats and assign them to variables
    task_list = get_all_task_data()  # Get the full task list from tasks.txt
    total_tasks = len(task_list)  # Count the number of tasks in the full task list
    total_completed_tasks = len([t for t in task_list if t.completed == True])  # Count the number of completed tasks in the full task list
    total_uncompleted_tasks = len([t for t in task_list if t.completed == False])  # Count the number of incomplete tasks in the full task list
    total_overdue_tasks = len([t for t in task_list if (t.due_date < datetime.now() and t.completed == False)])  # Count the number of overdue tasks in the full task list
    percentage_of_incomplete_tasks = (total_uncompleted_tasks / total_tasks) * 100  # Calculate the percentage of incomplete tasks in the full task list
    percentage_of_overdue_tasks = (total_overdue_tasks / total_tasks) * 100  # Calculate the percentage of overdue tasks in the full task list

    # Open the task overview file and write the stats to it in an easy to read format
    with open("task_overview.txt", "w") as task_overview_file:
        task_overview_file.write(f"""-----------------------------------
    TASK OVERVIEW
-----------------------------------
    Completed tasks:    {total_completed_tasks}
    Incomplete tasks:   {total_uncompleted_tasks}
    Overdue tasks:      {total_overdue_tasks}
    ---------------------------
    Total tasks:        {total_tasks}

    BY PERCENTAGE:
    
    Incomplete tasks:   {percentage_of_incomplete_tasks:.1f}%
    Overdue tasks:      {percentage_of_overdue_tasks:.1f}%
-----------------------------------""")

    # Generate the user task statistics and write them to the user_overview.txt file
    user_data = get_all_user_data()  # Get the latest user data from the system
    # Create a heading with some high level data about total tasks and total users
    heading = (f"""-----------------------------------
    INDIVIDUAL SUMMARIES
-----------------------------------
    Total Users:        {len(user_data)}
    Total Tasks:        {total_tasks}
-----------------------------------""")
    # Generate the body of the report by iterating over each user in user.txt and printing their individual stats by calling User.stats() to generate the data
    user_statistics = ""  # Create a string variable to add all the user task data to
    for user in user_data:  # For each user
        user_stats = user.stats()  # Retrieeve the stats dict generated by calling .stats() 
        if user_stats['total_user_tasks'] == 0:  # If the user has no tasks, display this on a single line and append it to the user_statistics string variable.
            user_statistics += (f"""\n    {user.username} has 0 tasks.
-----------------------------------""")
        else: # If the user has one task or more, append the full report using the dict values to the user_statistics string variable
            user_statistics += (f"""\n>> {user.username}
    Total Tasks:        {user_stats['total_user_tasks']}
    Percentage of all:  {user_stats['percentage_of_total_tasks']:.1f}%
    Completeness by percentage:   
        Completed:      {user_stats['percentage_tasks_completed']:.1f}%
        Incomplete:     {user_stats['percentage_pending_tasks']:.1f}%
        Overdue:        {user_stats['percentage_overdue_tasks']:.1f}%
-----------------------------------""")
    # Once data has been retrieved for all users, open the file and write the heading and user_statistics strings together
    with open("user_overview.txt", "w") as user_overview_file:
        user_overview_file.write(heading+user_statistics)
    # Display a success message if confirmation is True.
    if confirmation == True:
        input("Congratulations, your reports have been generated.\n\nuser_overview.txt\ntask_overview.txt\n\nPress ENTER to return to the main menu.")
    

def display_statistics():
    """
    Ask the user which report they would like to view.
    When they've made their selection, retrieve either the Task or User overview reports from the corresponding *.txt file generated by generate_report()
    """
    generate_reports(confirmation=False)  # Update the reports, if the reports don't exist already, create them

    while True:
        # Ask user to select which report they would like to view
        selected_report = int(input(f"""\033cWhich report would you like to view?
            
    1. Task Overview Report.
    2. User Overview report.
    3. Return to Main Menu.
        
Your selection: """))
        if selected_report == 1:  # If user selects task overview, open task_overview.txt and print the contents to the screen
            with open("task_overview.txt", "r") as task_overview_file:
                print("\033c" + task_overview_file.read())  # Clear the terminal then print the full contents to the screen
                input("Press ENTER to return to previous menu.")
        elif selected_report == 2:  # If user selects user overview, open user_overview.txt and print the contents to the screen
            with open("user_overview.txt", "r") as user_overview_file:
                print("\033c" + user_overview_file.read())  # Clear the terminal then print the full contents to the screen
                input("Press ENTER to return to previous menu.")
        else:
            break

#########################
# Initialise Files
######################### 

# If no user.txt file exists, write one with a default admin account
if not os.path.exists("user.txt"):
    with open("user.txt", "w") as default_file:
        default_file.write("admin, adm1n")

# If no tasks.txt file exists, create an empty one to accept tasks
if not os.path.exists("tasks.txt"):
    with open("tasks.txt", "w") as default_file:
        pass

#########################
# User Login
######################### 

# keep trying until a successful login
logged_in_user = False
while not logged_in_user:  # While there's no logged_in_user
    print("\033cLOGIN")
    curr_user = input("Username: ")  # Request a username from the user
    curr_pass = input("Password: ")  # Request a password from the user
    logged_in_user = User.validate(curr_user,curr_pass)  # Pass the username and password to the User.validate function
    if not logged_in_user:  # if logged_in_user is still false
        input("\nThat username and password combination does not match, please press ENTER and try again.")

#########################
# Main Program
######################### 

while True:
    # Present the user with a menu of options for them to select
    print("\033c")  # Clear the terminal
    if logged_in_user.username == 'admin':  # If the user is admin, show the extended menu options
        # Ask user to choose a menu option
        menu = input("""Select one of the following Options below:
    r - Registering a user
    a - Adding a task
    va - View all tasks
    vm - view my task
    gr - generate reports
    ds - display statistics
    e - Exit
    : """).lower()
    else:  # Present options for all other user types. note: Removed "register a user" from the menu for non-admin accounts.
        # Ask user to choose a menu option
        menu = input("""Select one of the following Options below:
    a - Adding a task
    va - View all tasks
    vm - view my task
    e - Exit
    : """).lower()

    if menu == 'r' and logged_in_user.username == 'admin':  # Register new user (if admin)
        print("\033c")  # Clear the terminal
        reg_user()  # Call the reg_user view function

    elif menu == 'a':  # Add a new task
        print("\033c")  # Clear the terminal
        add_task()  # Call the add_task view function

    elif menu == 'va':  # View all tasks
        print("\033c")  # Clear the terminal
        view_all()  # Call the view_all view function 
        input("Press ENTER to return to the main menu.")
        
    elif menu == 'vm':  # View my tasks
        view_mine()  # Call the view_mine view function

    elif menu == 'gr'and logged_in_user.username == 'admin': # Generate reports (if admin)
        print("\033c")  # Clear the terminal
        generate_reports()  # Call the generate reports function

    elif menu == 'ds' and logged_in_user.username == 'admin':  # display statistics (if admin)
        display_statistics()

    elif menu == 'e':  # Exit program
        print("\033c")  # Clear the terminal
        print('Goodbye!!!')
        exit()

    else:  # Default case
        print("You have made a wrong choice, Please Try again")
