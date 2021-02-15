from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
import smtplib

Base = declarative_base()

class Table(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    task = Column(String)
    deadline = Column(Date, default=datetime.today())

    def __init__(self, task, deadline):
        self.task = task
        self.deadline = deadline

    def __repr__(self):
        return self.string_field

class ToDoList():
    def __init__(self):
        engine = create_engine('sqlite:///todo.db')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def menu(self):
        menu_items = {'1': 'Today\'s tasks',
                      '2': 'Week\'s tasks',
                      '3': 'All tasks',
                      '4': 'Missed tasks',
                      '5': 'Add task',
                      '6': 'Delete task',
                      '7': 'Send email',
                      '0': 'Exit'}
        while True:
            for k, v in menu_items.items():
                print(f'{k}) {v}')
            print("\nSelect options:")
            choice = int(input())
            if choice == 1:
                self.todays_tasks()
            elif choice == 2:
                self.weeks_tasks()
            elif choice == 3:
                self.all_tasks()
            elif choice == 4:
                self.missed_tasks()
            elif choice == 5:
                self.add_task()
            elif choice == 6:
                self.delete_task()
            elif choice == 7:
                self.send_email()
            elif choice == 0:
                print('\nBye!')
                exit()
            else:
                print('Incorrect input, try again.')

    def todays_tasks(self):
        today = datetime.today()
        print('\nToday {}:'.format(today.strftime('%#d %b')))
        rows = self.session.query(Table).filter(Table.deadline == today.date()).all()
        if len(rows) == 0:
            print('Nothing to do!')
        else:
            for n, row in enumerate(rows):
                print('{}. {}'.format(n + 1, row.task))
        print()

    def weeks_tasks(self):
        today = datetime.today()
        for d in range(7):
            day = today + timedelta(days=d)
            print('\n{}:'.format(day.strftime('%A %#d %b')))
            rows = self.session.query(Table).filter(Table.deadline == day.date()).order_by(Table.id).all()
            if len(rows) == 0:
                print('Nothing to do!')
            else:
                for n, row in enumerate(rows):
                    print('{}. {}'.format(n + 1, row.task))
        print()

    def all_tasks(self):
        print('\nAll tasks:')
        rows = self.session.query(Table).order_by(Table.deadline, Table.id).all()
        if len(rows) == 0:
            print('Nothing to do!')
        else:
            for n, row in enumerate(rows):
                print('{}. {}. {}'.format(n + 1,
                                          row.task,
                                          row.deadline.strftime('%#d %b')))
        print()

    def missed_tasks(self):
        rows = self.session.query(Table).filter(Table.deadline < datetime.today()).order_by(Table.deadline, Table.id).all()
        print('\nMissed tasks:')
        if len(rows) == 0:
            print('Nothing is missed!')
        else:
            for n, row in enumerate(rows):
                print('{}. {}. {}'.format(n + 1, row.task,
                                          row.deadline.strftime('%#d %b')))
        print()

    def send_email(self):
        select=input("All, selected or missed tasks? (a/s/m)\n")
        if select == "A" or select == "a":
            rows = self.session.query(Table).order_by(Table.deadline, Table.id).all()
        elif select == "S" or select == "s":
            rows = self.session.query(Table).order_by(Table.id).all()
            if len(rows) == 0:
                print('Nothing to send!')
            else:
                for n, row in enumerate(rows):
                    print('{}. {}. {}'.format(row.id, row.task,
                                          row.deadline.strftime('%#d %b')))
            select_id = int(input("\nSelect task:\n"))
            rows = self.session.query(Table).order_by(Table.id).filter(Table.id == select_id).all()
        elif select == "m" or select == "M":
            rows = self.session.query(Table).filter(Table.deadline < datetime.today()).order_by(Table.deadline, Table.id).all()
        else:
            print('Incorrect input. Will be sent all tasks')

        subject = input("Enter subject of mail\n")
        server = smtplib.SMTP("smtp.mail.ru", 587)
        server.starttls()
        #Enter your username and password using the keyboard, or using variables
        #email = "your_email@mail.ru"
        #password = "your_password"
        email = input("Enter your email\n")
        password = input("Password:\n")
        server.login(email, password)
        to = input("Enter send email:\n")
        text = input("Enter message:\n")
        for n, row in enumerate(rows):
                text += (('\n{}. {}. {}\n'.format(n + 1, row.task, row.deadline)))

        body = "\r\n".join((
            "From: %s" % email,
            "To: %s" % to,
            "Subject: %s" % subject,
            "",
            text))

        server.sendmail(email, [to], body)
        server.quit()
        print("\nSuccessfully send email!\n")

    def add_task(self):
        task = input('\nEnter task\n')
        deadline = input('Enter deadline (%Y-%m-%d)\n')

        new_deadline = datetime.strptime(deadline, "YYYY-%MM-%DD")
        new_row = Table(task=task,
                        deadline=new_deadline)
        self.session.add(new_row)
        self.session.commit()
        print('The task has been added!\n')

    def delete_task(self):
        rows = self.session.query(Table).order_by(Table.deadline).all()
        if len(rows) == 0:
            print('\nNothing to delete!\n')
        else:
            print('\nChoose the number of the task you want to delete:')
            for n, row in enumerate(rows):
                print('{}. {}. {}'.format(n + 1,
                                      row.task,
                                      row.deadline.strftime('%#d %b')))
            dlt = int(input())
            if 0 < dlt <= len(rows):
                dlt_row = rows[dlt - 1]
                self.session.delete(dlt_row)
                self.session.commit()
                print("The task has been deleted!\n")
            else:
                print("There's no such task!\n")

tasks = ToDoList()
tasks.menu()
