# TRAIN TICKET BOOKING SYSYTEM.

# Created by ~ SABANNA PUJARI.
# Project (18/07/2023-28/11/2023).

# This project is easy to use and it is terminal based project.

# in my project one class, so many function and crud operation i have been created to make train ticket booking system.
import mysql.connector
from datetime import datetime

class TicketBookingSystem:
    def __init__(self):
        self.mydb = mysql.connector.connect(host='localhost', user='root', passwd='chintu@1215', database='testdb')
        self.mycursor = self.mydb.cursor()
        self.trains = {}
        self.booked_tickets = []
        self.admin_username = "admin@123"
        self.admin_password = "123456"
        self.current_user = None
        self.create_invoices_table()
        self.create_canceled_tickets_table()
        self.train_id = None
        self.train_name=None
        self.fare = None
        # self.status = None

    def create_user_table(self):
        self.mycursor.execute("SHOW TABLES LIKE 'user_registration'")
        result = self.mycursor.fetchone()
        if not result:
            self.mycursor.execute("CREATE TABLE user_registration (username VARCHAR(250), password VARCHAR(250))")

    def create_canceled_tickets_table(self):
        self.mycursor.execute("""
            CREATE TABLE IF NOT EXISTS canceled_tickets (
                ticket_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(250),
                train_id INT,
                num_tickets INT,
                total_fare INT,
                status VARCHAR(20) DEFAULT 'canceled',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (train_id) REFERENCES train_details(train_id)
            )
        """)
        self.mydb.commit()

    def create_train_table(self):
        self.mycursor.execute("SHOW TABLES LIKE 'train_details'")
        result = self.mycursor.fetchone()
        if not result:
            self.mycursor.execute("CREATE TABLE train_details (train_id INT, train_name VARCHAR(250), seats INT, fare INT)")

    def register_user(self, username, password):
        self.mycursor.execute("SELECT username FROM user_registration WHERE username=%s", [username])
        user = self.mycursor.fetchone()

        if user:
            print("\nUsername already taken. Please choose another one.")
        else:
            data = (username, password)
            query = "INSERT INTO user_registration VALUES (%s, %s)"
            self.mycursor.execute(query, data)
            self.mydb.commit()
            print("\nRegistration successful. You can now log in.")

    def validate_username(self, username):
        # Validation rule: username must contain at least one '@' symbol
        if '@' not in username:
            print("Invalid username. Username must contain '@'.")
            return False
        return True

    def validate_password(self, password):
        # Validation rule: password must contain only digits
        if not password.isdigit():
            print("Invalid password. Password must contain only digits.")
            return False
        return True

    def login_user(self, username, password):
        self.mycursor.execute("SELECT username, password FROM user_registration WHERE username=%s", [username])
        user = self.mycursor.fetchone()

        if user and str(user[1]) == password:
            return True
        else:
            return False

    def admin_login(self, username, password):
        return username == self.admin_username and password == self.admin_password


    def view_trains(self, is_admin=False):
        print("\nAvailable Trains:\n")
        self.mycursor.execute("SELECT * FROM train_details")
        train_data = self.mycursor.fetchall()

        if not train_data:
            print("No trains available.")
            return

        for train in train_data:
            train_id, train_name, seats, fare = train
            print(f"Train ID: {train_id}")
            print(f"Train Name: {train_name}")
            print(f"Seats Available: {seats}")
            print(f"Fare: {fare}")
            print("-" * 30)

            
    def add_new_train(self):
        try:
            train_id = int(input("Enter Train ID: "))
            name = input("Enter Train Name: ")
            seats = int(input("Enter Seats Available: "))
            fare = int(input("Enter Fare: "))
        except ValueError:
            print("Invalid input. Please enter valid numeric values for Train ID, Seats Available, and Fare.")
            return

        new_train = "INSERT INTO train_details (train_id, train_name, seats, fare) VALUES (%s, %s, %s, %s)"
        data = (train_id, name, seats, fare)

        self.mycursor.execute(new_train, data)
        self.mydb.commit()

        print(f"\nNew train added: {name} (Train ID: {train_id}, Seats: {seats}, Fare: {fare})")


    def delete_train(self):
        try:
            train_id = int(input("Enter Train ID to delete: "))
        except ValueError:
            print("Invalid input. Please enter a valid Train ID (a number).")
            return

        # Check if the train_id exists in the train_details table
        self.mycursor.execute("SELECT * FROM train_details WHERE train_id = %s", [train_id])
        train_info = self.mycursor.fetchone()

        if train_info:
            # Check if there are booked tickets for this train
            self.mycursor.execute("SELECT * FROM booked_tickets WHERE train_id = %s", [train_id])
            booked_tickets = self.mycursor.fetchall()

            if booked_tickets:
                print("Cannot delete the train. There are booked tickets associated with it.")
            else:
                self.mycursor.execute("DELETE FROM train_details WHERE train_id = %s", [train_id])
                self.mydb.commit()
                print(f"\nTrain {train_id} deleted.")
        else:
            print("\nTrain not found.")


    def create_invoices_table(self):
        self.mycursor.execute("SHOW TABLES LIKE 'invoicess'")
        result = self.mycursor.fetchone()
        if not result:
            self.mycursor.execute("CREATE TABLE invoicess (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(250), train_id INT, num_tickets INT, total_fare INT, status VARCHAR(20) DEFAULT 'confirmed', Date_&_Time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")


    def generate_invoice(self, username, train_id, num_tickets, total_fare, status='confirmed'):
        if num_tickets <= 0:
            return

        invoice_query = "INSERT INTO invoicess (username, train_id, num_tickets, total_fare, status) VALUES (%s, %s, %s, %s, %s)"
        invoice_data = (username, train_id, num_tickets, total_fare, status)

        self.mycursor.execute(invoice_query, invoice_data)
        self.mydb.commit()
        print("Invoice generated and stored for train_id", train_id)

        # Store booked ticket data in the system
        booked_ticket = {
            'username': username,
            'train_id': train_id,
            'num_tickets': num_tickets,
            'total_fare': total_fare
        }
        self.booked_tickets.append(booked_ticket)

    def insert_canceled_ticket(self, username, train_id, num_tickets, total_fare):
        canceled_ticket_query = "INSERT INTO canceled_tickets (username, train_id, num_tickets, total_fare) VALUES (%s, %s, %s, %s)"
        canceled_ticket_data = (username, train_id, num_tickets, total_fare)

        self.mycursor.execute(canceled_ticket_query, canceled_ticket_data)
        self.mydb.commit()


    def book_ticket(self, train_id, num_tickets):
        self.mycursor.execute("SELECT * FROM train_details WHERE train_id = %s", [train_id])
        train_info = self.mycursor.fetchone()

        if train_info:
            train_id, name, seats, fare = train_info

            if seats >= num_tickets:
                total_fare = num_tickets * fare
                confirmation = input(f"Do you want to book {num_tickets} ticket(s) for {name} for a total fare of {total_fare}? (yes, no): ")

                if confirmation.lower() == "yes":
                    seats -= num_tickets
                    ticket = {"train_id": train_id, "num_tickets": num_tickets, "total_fare": total_fare}

                    # Update the seats in the train_details table
                    self.mycursor.execute("UPDATE train_details SET seats = %s WHERE train_id = %s", [seats, train_id])

                    # Store booked ticket data in the database
                    booked_ticket_query = "INSERT INTO booked_tickets (username, train_id, num_tickets, total_fare) VALUES (%s, %s, %s, %s)"
                    booked_ticket_data = (self.current_user, train_id, num_tickets, total_fare)
                    self.mycursor.execute(booked_ticket_query, booked_ticket_data)

                    # Generate and store invoice
                    self.generate_invoice(self.current_user, train_id, num_tickets, total_fare)

                    # Commit changes to the database after all operations are completed
                    self.mydb.commit()

                    return True, name, total_fare, num_tickets
                else:
                    print("\nBooking cancelled.")
                    return False, None, None, None
            else:
                print("\nNot enough seats available.")
                return False, None, None, None
        else:
            print("\nInvalid train ID.")
            return False, None, None, None
        
    def update_train_details(self, old_train_id, new_train_id):
        try:
            # Delete associated rows in booked_tickets table
            self.mycursor.execute("DELETE FROM booked_tickets WHERE train_id = %s", [old_train_id])

            # Update train_id in train_details table
            self.mycursor.execute("UPDATE train_details SET train_id = %s WHERE train_id = %s", [new_train_id, old_train_id])

            self.mydb.commit()
            print("Train details updated successfully.")
        except Exception as e:
            print(f"Error updating train details: {e}")
            self.mydb.rollback()


    def view_invoices(self):
        self.mycursor.execute("SELECT id, train_id, num_tickets, total_fare, status, `Date_Time` FROM invoicess WHERE username = %s", [self.current_user])
        invoices_data = self.mycursor.fetchall()

        if not invoices_data:
            print("\nNo invoices available.\n")
        else:
            print("\nInvoices:")
            for invoice in invoices_data:
                invoice_id, train_id, num_tickets, total_fare, status, timestamp = invoice
                self.mycursor.execute("SELECT train_name FROM train_details WHERE train_id = %s", [train_id])
                train_name = self.mycursor.fetchone()[0]

                print(f"Train Name: {train_name}")
                print(f"Tickets Booked: {num_tickets}")
                print(f"Total Fare: {total_fare}")
                print(f"Status: {status}")
                print(f"Date_Time: {timestamp}")

                # Update the status in the console based on the 'status' column
                if status == 'canceled':
                    print("This ticket has been canceled.")
                elif status == 'pending':
                    print("Payment is pending confirmation.")
                elif status == 'confirmed':
                    print("Ticket is confirmed.")

                print("-" * 30)



    def view_invoices_admin(self):
        self.view_invoices()


    def view_invoices_admin(self):
        self.mycursor.execute("SELECT id, username, train_id, num_tickets, total_fare, status, `Date_Time` FROM invoicess")
        invoices_data = self.mycursor.fetchall()

        if not invoices_data:
            print("\nNo invoices available.\n")
        else:
            print("\nInvoices:")
            for invoice in invoices_data:
                invoice_id, username, train_id, num_tickets, total_fare, status, timestamp = invoice
                self.mycursor.execute("SELECT train_name FROM train_details WHERE train_id = %s", [train_id])
                train_name = self.mycursor.fetchone()[0]

                print(f"Invoice ID: {invoice_id}")
                print(f"Username: {username}")
                print(f"Train Name: {train_name}")
                print(f"Tickets Booked: {num_tickets}")
                print(f"Total Fare: {total_fare}")
                print(f"Status: {status}")
                print(f"Date_Time: {timestamp}")

                # Update the status in the console based on the 'status' column
                if status == 'canceled':
                    print("This ticket has been canceled.")
                elif status == 'pending':
                    print("Payment is pending confirmation.")
                elif status == 'confirmed':
                    print("Ticket is confirmed.")

                print("-" * 30)


    def create_booked_tickets_table(self):
        self.mycursor.execute("""
            CREATE TABLE IF NOT EXISTS booked_tickets (
                ticket_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(250),
                train_id INT,
                num_tickets INT,
                total_fare INT,
                FOREIGN KEY (train_id) REFERENCES train_details(train_id)
            )
        """)
        self.mydb.commit()

    def view_booked_tickets(self):
    # recover booked tickets for the current user from the database
        self.mycursor.execute("SELECT * FROM booked_tickets WHERE username = %s", [self.current_user])
        booked_tickets = self.mycursor.fetchall()

        if not booked_tickets:
            print("\nNo tickets have been booked yet.\n")
        else:
            print("\nYour Booked Tickets:")
            ticket_number = 1

            for ticket in booked_tickets:
                # Extract ticket details
                ticket_id, username, train_id, num_tickets, total_fare = ticket

                # recover train name from train_details table
                self.mycursor.execute("SELECT train_name FROM train_details WHERE train_id = %s", [train_id])
                train_name = self.mycursor.fetchone()[0]

                print(f"Ticket {ticket_number}: Train Name: {train_name}, Tickets Booked: {num_tickets}, Total Fare: {total_fare}\n")
                ticket_number += 1

    def verify_user(self, username, password):
    # Check if the provided username and password match a user in the database
        self.mycursor.execute("SELECT * FROM user_registration WHERE username = %s AND password = %s", [username, password])
        user_data = self.mycursor.fetchone()

        return user_data is not None


    def view_booked_tickets_admin(self):
        self.mycursor.execute("SELECT * FROM booked_tickets")
        booked_tickets = self.mycursor.fetchall()

        if not booked_tickets:
            print("\nNo tickets have been booked yet.\n")
        else:
            print("\nAll Booked Tickets:")
            ticket_number = 1

            for ticket in booked_tickets:
                # Extract ticket details
                ticket_id, username, train_id, num_tickets, total_fare = ticket

                self.mycursor.execute("SELECT train_name FROM train_details WHERE train_id = %s", [train_id])
                train_name = self.mycursor.fetchone()[0]

                print(f"Ticket {ticket_number}: Username: {username}, Train Name: {train_name}, Tickets Booked: {num_tickets}, Total Fare: {total_fare}\n")
                ticket_number += 1


    def fetch_booked_tickets(self):
        self.mycursor.execute("SELECT * FROM booked_tickets WHERE username = %s", [self.current_user])
        return self.mycursor.fetchall()
    
    
    def cancel_ticket(self, ticket_number):
        booked_tickets = self.fetch_booked_tickets()

        if not booked_tickets:
            print("\nNo tickets have been booked yet.\n")
            return None,None

        print("\nBooked Tickets:")
        for i, ticket in enumerate(booked_tickets, start=1):
            ticket_id, username, train_id, num_tickets, total_fare = ticket
            self.mycursor.execute("SELECT train_name FROM train_details WHERE train_id = %s", [train_id])
            train_name = self.mycursor.fetchone()[0]

            print(f"Ticket {i}: Train Name: {train_name}, Tickets Booked: {num_tickets}, Total Fare: {total_fare}")

        if ticket_number < 1 or ticket_number > len(booked_tickets):
            print("\nInvalid ticket number.\n")
            return None,None

        selected_ticket = booked_tickets[ticket_number - 1]
        ticket_id, username, train_id, num_tickets, total_fare = selected_ticket

        if username != self.current_user:
            print("\nYou can only cancel your own tickets.\n")
            return None,None

        self.mycursor.execute("SELECT train_name FROM train_details WHERE train_id = %s", [train_id])
        train_name = self.mycursor.fetchone()[0]

        # Update the available seats in the train_details table
        self.mycursor.execute("UPDATE train_details SET seats = seats + %s WHERE train_id = %s", [num_tickets, train_id])
        self.mydb.commit()

        # Delete the canceled ticket from booked_tickets table
        self.mycursor.execute("DELETE FROM booked_tickets WHERE ticket_id = %s", [ticket_id])
        self.mydb.commit()

        # Insert the canceled ticket into the canceled_tickets table
        self.insert_canceled_ticket(username, train_id, num_tickets, total_fare)


        print(f"\nTicket {ticket_number}: Train Name: {train_name}, Tickets Booked: {num_tickets}, Total Fare: {total_fare} has been canceled.\n")
        return train_id,num_tickets





    def update_invoice_status(self, train_id, num_tickets, status, ticket_number):
    # Fetch the id from the 'invoicess' table based on train_id and num_tickets
        self.mycursor.execute("SELECT id FROM invoicess WHERE train_id = %s AND num_tickets = %s", [train_id, num_tickets])
        invoice_id = self.mycursor.fetchone()

        if invoice_id is not None:
            # Consume the result before executing another query
            self.mycursor.fetchall()

            # Update the status of the corresponding invoice
            self.mycursor.execute("UPDATE invoicess SET status = %s WHERE id = %s", [status, invoice_id[0]])
            self.mydb.commit()

            print(f"Invoice status updated for train_id {train_id}")
            print(f"Status: {status}")

            print(f"Ticket {ticket_number}: Train Name: {train_id}, Tickets Booked: {num_tickets}")
            print(f"Status: {status}")

        else:
            print(f"No matching invoice found for train_id {train_id} and num_tickets {num_tickets}")
            print(f"Unable to update status for ticket_number {ticket_number}")


    def update_train_details(self):
        try:
            train_id = int(input("Enter Train ID to update: "))
        except ValueError:
            print("Invalid input. Please enter a valid Train ID (a number).")
            return

        # Check if the train_id exists in the train_details table
        self.mycursor.execute("SELECT * FROM train_details WHERE train_id = %s", [train_id])
        train_info = self.mycursor.fetchone()

        if train_info:
            print("\nTrain Details:")
            print(f"Train ID: {train_info[0]}")
            print(f"Train Name: {train_info[1]}")
            print(f"Seats Available: {train_info[2]}")
            print(f"Fare: {train_info[3]}")
            print("-" * 30)

            print("_________________________________________________________")
            print("\n------------------Update Train Details: -----------------")
            print("_________________________________________________________")
            print("1. Update Train Name")
            print("2. Update Seats Available")
            print("3. Update Fare")
            print("4. Return to Admin Menu")
            print("_________________________________________________________")
            print("_________________________________________~ SABANNA PUJARI")

            update_choice = input("Enter your choice: ")

            # if update_choice == '1':
            #     new_train_id = int(input("Enter the new Train ID: "))
            #     self.mycursor.execute("UPDATE train_details SET train_id = %s WHERE train_id = %s", [new_train_id, train_id])
            #     print("Train ID updated successfully.")

            if update_choice == '1':
                new_train_name = input("Enter the new Train Name: ")
                self.mycursor.execute("UPDATE train_details SET train_name = %s WHERE train_id = %s", [new_train_name, train_id])
                print("Train Name updated successfully.")

            elif update_choice == '2':
                new_seats = int(input("Enter the new Seats Available: "))
                self.mycursor.execute("UPDATE train_details SET seats = %s WHERE train_id = %s", [new_seats, train_id])
                print("Seats Available updated successfully.")

            elif update_choice == '3':
                new_fare = int(input("Enter the new Fare: "))
                self.mycursor.execute("UPDATE train_details SET fare = %s WHERE train_id = %s", [new_fare, train_id])
                print("Fare updated successfully.")

            elif update_choice == '4':
                return

            else:
                print("Invalid choice. Please try again.")

            self.mydb.commit()
            print("Train details updated successfully.")
        else:
            print("\nTrain not found.")

    def process_online_payment(self):
        pass

    def get_num_tickets(self):
        pass
    
    def respond_to_help_request(self, username):
        # You can implement the logic to respond to the user's help request here
        # For example, send an email, update the database, etc.
        print(f"\nResponding to help request for user: {username}")
        response_message = input("Enter your response: ")
        print(f"Response sent to user {username}: {response_message}")


    def view_canceled_tickets_admin(self):
        self.mycursor.execute("SELECT * FROM canceled_tickets")
        canceled_tickets = self.mycursor.fetchall()

        if not canceled_tickets:
            print("\nNo tickets have been canceled yet.\n")
        else:
            print("\nAll Canceled Tickets:")
            ticket_number = 1

            for ticket in canceled_tickets:
                # Extract ticket details
                ticket_id, username, train_id, num_tickets, total_fare, status, timestamp = ticket

                self.mycursor.execute("SELECT train_name FROM train_details WHERE train_id = %s", [train_id])
                train_name = self.mycursor.fetchone()[0]

                print(f"Ticket {ticket_number}: Username: {username}, Train Name: {train_name}, Tickets Canceled: {num_tickets}, Total Fare: {total_fare}, Status: {status}, Date_Time: {timestamp}\n")
                ticket_number += 1


    def calculate_total_revenue(self):
        total_revenue = sum(ticket['total_fare'] for ticket in self.booked_tickets)
        print()
        print(f"Total amount : {total_revenue}")

    def main(self):
        self.create_user_table()
        self.create_train_table()

        while True:
            print("_________________________________________________________")
            print("\n------------- Trains Ticket Booking System --------------")
            print("_________________________________________________________")
            print("1. \t User Registration.")
            print("2. \t User Login.")
            print("3. \t Admin Login.")
            print("4. \t Exit.")
            print("_________________________________________________________")
            print("_________________________________________~ SABANNA PUJARI")
            print()

            choice = input("Enter a choice (1,2,3,4): ")

            if choice == '1':
                print("\nUser Registration:")
                username = input("Enter your username: ")

                # Validate the username
                if not self.validate_username(username):
                    continue

                password = input("Enter your password: ")

                # Validate the password
                if not self.validate_password(password):
                    continue

                self.register_user(username, password)

            elif choice == '2':
                print("\nUser Login:")
                username = input("Enter your username: ")

                # Validate the username
                if not self.validate_username(username):
                    continue

                password = input("Enter your password: ")

                # Validate the password
                if not self.validate_password(password):
                    continue

                if self.login_user(username, password):
                    print(f"\nWelcome, {username}!")
                    self.current_user = username
                    self.user_menu()

                else:
                    print("\nInvalid username or password. Please try again.")

            elif choice == '3':
                print("\nAdmin Login:")
                admin_username = input("Enter admin username: ")
                print()
                admin_password = input("Enter admin password: ")
                print()
                if self.admin_login(admin_username, admin_password):
                    print("\nAdmin login successful.")
                    self.admin_menu()
                else:
                    print("\nInvalid admin info.")

            elif choice == '4':
                print("\nThank you for using the Train Ticket Booking System!")
                print("Have a great day...")
                break

            else:
                print("\nInvalid choice. Please try again.")

    def user_menu(self):
        num_tickets = None
        status = None
        while True:
            print("________________________________________________________")
            print("\n-------------------User :----------------------------")
            print("________________________________________________________")
            print("1. \t View Available Trains.")
            print("2. \t Book a Ticket.")
            print("3. \t View Booked Tickets.")
            print("4. \t Cancel a Ticket.")
            print("5. \t View Total Amount.")
            print("6. \t Invoices.")
            print("7. \t Help and Support.")
            print("8. \t Logout.")
            print("_________________________________________________________")
            print("_________________________________________~ SABANNA PUJARI")
            print()

            choice = input("Enter a choice (1,2,3,4,5,6,7,8): ")

            if choice == '1':
                self.view_trains()

            elif choice == '2':
                train_id = input("Enter the Train ID: ")
                print()
                num_tickets = input("Enter the number of tickets: ")
                print()

                # Check if num_tickets is a positive integer
                if not num_tickets.isdigit() or int(num_tickets) <= 0:
                    print("\nInvalid number of tickets. Please provide a positive integer for the number of tickets.\n")
                    continue

                booking_status, train_name, fare, num_tickets = self.book_ticket(train_id, int(num_tickets))

                if booking_status:
                    print(f"\nBooking successful! Train: {train_name}, Fare: {fare}, Tickets: {num_tickets}")

                else:
                    print("\nBooking failed. Please try again.")

            elif choice == '3':
                self.view_booked_tickets()

            elif choice == '4':
                self.view_booked_tickets()
                ticket_number = int(input("Enter the ticket number you want to cancel: "))
                train_id, num_tickets = self.cancel_ticket(ticket_number)
                self.update_invoice_status(train_id, num_tickets, 'canceled', ticket_number)

            elif choice == '5':
                self.calculate_total_revenue()

            elif choice == '6':
                self.view_invoices()


            elif choice == '7':
                self.help_and_support()

            elif choice == '8':
                print(f"\nLogged out successfully, Goodbye! {self.current_user}!")
                print("Have A Great Day...\n")
                self.current_user = None
                break

            else:
                print("\nInvalid choice. Please try again.")


    def help_and_support(self):
        print("\nHelp and Support:")
        print("---------------------")
        print("1. Canceled/Booked Ticket - Payment will be received in 3 days.")
        print("2. Any other problem - Call us on 8104292075 or 022-21342134.")
        print("3. Any other problem - Mail us on ttbs@gmail.com.")
        print("4. problem occurring during booking ticket.")
        print("5. Return to User Menu.")


    def admin_menu(self):
        while True:
            print("_______________________________________________________")
            print("\n-------------------------Admin :--------------------")
            print("_______________________________________________________")
            print("1. \t View Available Trains.")
            print("2. \t Add a New Train.")
            print("3. \t Delete a Train.")
            print("4. \t View Invoices.")
            print("5. \t Update train details.")
            print("6. \t Logout.")
            print("_________________________________________________________")
            print("_________________________________________~ SABANNA PUJARI")
            print()
            choice = input("Enter a choice (1,2,3,4,5,6): ")

            if choice == '1':
                self.view_trains(is_admin=True)

            elif choice == '2':
                self.add_new_train()

            elif choice == '3':
                self.delete_train()

            elif choice == '4':
                self.view_invoices_admin()

            elif choice == '5':
                self.update_train_details()

            elif choice == '6':
                print(f"\nAdmin logout successful , Goodbye! {self.admin_username}")
                print("Have A Great Day...\n")
                self.admin_username = None
                break

            else:
                print("\nInvalid choice. Please try again.")


ticket_system = TicketBookingSystem()
ticket_system.current_user = None
ticket_system.main()