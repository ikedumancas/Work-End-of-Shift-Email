import os
from gmail import send_message

def main():
    with open("report.html", "r") as report_file, open("recipients.csv", "r") as recipients_file:
        recipients = recipients_file.read().split(',')
        email =  send_message("migueld@codev.com",recipients, "End of shift report", report_file.read(), 'html')
        print("Email Sent.")
        print(email)


if __name__ == '__main__':
    main()
