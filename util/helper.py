import csv
import os
import random
import string
import secrets
import uuid
from django.core.files import File


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def certificate_template_path(instance, filename):
    new_filename = random.randint(1, 3910209312)
    name, ext = get_filename_ext(filename)
    final_filename = f'{name}{ext}'.format(new_filename=new_filename, ext=ext)
    return f"certificates/templates/{final_filename}".format(
        new_filename=new_filename,
        final_filename=final_filename
    )


def events_banner_image_path(instance, filename):
    new_filename = random.randint(1, 3910209312)
    name, ext = get_filename_ext(filename)
    final_filename = f'{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return f"banners/event/{new_filename}/{final_filename}".format(
        new_filename=new_filename,
        final_filename=final_filename
    )



def get_emails_from_csv_file(file_path: File) -> list[str]:
    emails: list[str] = []
    try:
        # Handle both text and binary content
        content = file_path.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8')
            
        # Use StringIO to create a file-like object
        from io import StringIO
        csv_file = StringIO(content)
        
        # Read CSV with DictReader
        csv_reader = csv.DictReader(csv_file)
        emails = [row for row in csv_reader]
        
        # Close StringIO
        csv_file.close()
        
        # Reset file pointer for potential future reads
        file_path.seek(0)
        
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
    return emails


# This is a helper function to fetch emails from event_enrollment table and use the emails to send reminders and
# certificates
def get_emails_from_event_attendance(event_id) -> list:
    from event_enrolment.models import EventEnrollment  # Lazy import to avoid circular import
    attendance_list = EventEnrollment.objects.filter(event_id=event_id)
    if attendance_list.exists():
        emails: list = [attendance.user_id.email for attendance in attendance_list]
        return emails
    else:
        pass


def combined_recipient_list(csv_file_path, event_id) -> list:
    csv_emails = get_emails_from_csv_file(csv_file_path)
    attendance_emails = get_emails_from_event_attendance(event_id)
    combined_emails = list(set(csv_emails + attendance_emails))
    return combined_emails

# def generate_random_password(length):
#     letters = string.ascii_lowercase
#     password = ''.join(random.choice(letters) for _ in range(length))
#     return 'MLH_' + password

def generate_unique_string(length: int = 8) -> str:
    unique_uuid = uuid.uuid4().hex[:length]
    return ''.join(secrets.choice(string.ascii_letters.upper() + string.digits) for _ in range(length)) + unique_uuid