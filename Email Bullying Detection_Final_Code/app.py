from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_cors import CORS
import mysql.connector
import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, classification_report
import joblib
import os
from datetime import datetime
import secrets
import imaplib
import email
from email.header import decode_header
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import openpyxl
from io import BytesIO
import time
import random
from faker import Faker
import ssl

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)

# Initialize Faker for generating realistic data
fake = Faker()

# Configuration
class Config:
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'root',
        'database': 'bullymail_db'
    }
    
    MODEL_PATH = 'saved_models'
    DATASET_PATH = 'datasets'

# Create directories
os.makedirs(Config.MODEL_PATH, exist_ok=True)
os.makedirs(Config.DATASET_PATH, exist_ok=True)

# Enhanced bullying phrases with academic context
BULLYING_PHRASES = [
    # Direct insults and personal attacks
    "you're worthless", "nobody likes you", "you should quit", "you're stupid",
    "can't do anything right", "useless student", "hopeless case", "waste of space",
    "you'll never succeed", "pathetic attempt", "embarrassing work", "complete failure",
    "don't belong here", "dumb idea", "ridiculous question", "everyone hates you",
    "you're a joke", "worthless contribution", "mental midget", "academic fraud",
    "incompetent fool", "should drop out", "stupid question", "waste of time",
    "failure student", "not cut out for", "terrible work", "awful performance",
    "disappointing effort", "below standards", "inadequate research", "poor quality",
    
    # Academic undermining
    "your research is flawed", "methodology is incompetent", "analysis is worthless",
    "can't understand basics", "fundamentally wrong approach", "academically weak",
    "intellectually deficient", "conceptually bankrupt", "theoretically unsound",
    "empirically invalid", "statistically insignificant", "methodologically unsound",
    
    # Power imbalance exploitation
    "as your advisor I'm disappointed", "you'll never get a recommendation",
    "your career is over", "no one will hire you", "reputation is ruined",
    "academic suicide", "professional embarrassment", "colleague laughing stock",
    
    # Subtle bullying
    "surprised you got this far", "expected better from you", "others are progressing faster",
    "not meeting potential", "consistent underperformance", "becoming a concern",
    "department is worried", "faculty has concerns", "standards are slipping"
]

NON_BULLYING_PHRASES = [
    # Positive reinforcement
    "great work", "well done", "excellent job", "good effort", "nice progress",
    "impressive work", "keep trying", "you can do it", "proud of you", "excellent question",
    "valuable contribution", "smart approach", "creative solution", "helpful comment",
    "constructive feedback", "meaningful input", "important perspective", "useful insight",
    "outstanding performance", "remarkable progress", "exceptional quality", "brilliant idea",
    "innovative approach", "thorough research", "comprehensive analysis", "excellent points",
    "well articulated", "thoughtful response", "insightful comments", "professional work",
    
    # Academic encouragement
    "showing strong potential", "demonstrates good understanding", "clear improvement",
    "developing nicely", "mastering concepts", "grasping complex ideas", "analytical skills growing",
    "research potential evident", "academic promise shown", "intellectual curiosity appreciated",
    
    # Constructive feedback
    "consider exploring further", "potential for expansion", "opportunity for depth",
    "suggest additional reading", "recommend further analysis", "build upon this foundation",
    "develop this concept", "expand your methodology", "strengthen your argument",
    
    # Professional communication
    "looking forward to your progress", "excited to see development", "confident in your abilities",
    "trust your judgment", "value your perspective", "appreciate your dedication",
    "respect your approach", "admire your persistence", "commend your efforts"
]

NEUTRAL_PHRASES = [
    "meeting scheduled for", "deadline approaching for", "submission required by",
    "office hours at", "department announcement", "course materials posted",
    "assignment due", "exam schedule", "grade posted", "feedback available",
    "recommendation letter", "transcript request", "scholarship application",
    "research proposal", "thesis defense", "dissertation committee",
    "conference presentation", "journal submission", "publication opportunity"
]

class EmailIntegration:
    def __init__(self):
        self.config = {
            'imap_server': 'imap.gmail.com',
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'email': '',
            'password': ''
        }
    
    def configure_email(self, email_address, app_password):
        """Configure email settings"""
        self.config['email'] = email_address
        self.config['password'] = app_password
        return True
    
    def test_connection(self):
        """Test email connection"""
        try:
            # Test SMTP
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.starttls()
            server.login(self.config['email'], self.config['password'])
            server.quit()
            
            # Test IMAP
            mail = imaplib.IMAP4_SSL(self.config['imap_server'])
            mail.login(self.config['email'], self.config['password'])
            mail.logout()
            
            return True, "Email configuration successful"
        except Exception as e:
            return False, f"Email configuration failed: {str(e)}"
    
    def connect_imap(self):
        """Connect to IMAP server with error handling"""
        try:
            mail = imaplib.IMAP4_SSL(self.config['imap_server'])
            mail.login(self.config['email'], self.config['password'])
            return mail
        except imaplib.IMAP4.error as e:
            print(f"IMAP login error: {e}")
            return None
        except Exception as e:
            print(f"IMAP connection error: {e}")
            return None
    
    def fetch_emails(self, mailbox='INBOX', limit=5):
        """Fetch emails from mailbox with better error handling"""
        if not self.config['email'] or not self.config['password']:
            return []
            
        mail = self.connect_imap()
        if not mail:
            return []
        
        try:
            mail.select(mailbox)
            result, data = mail.search(None, 'ALL')
            
            if result != 'OK':
                return []
                
            email_ids = data[0].split()
            emails = []
            
            for i, email_id in enumerate(email_ids[-limit:]):
                if i >= limit:
                    break
                
                try:
                    result, msg_data = mail.fetch(email_id, '(RFC822)')
                    if result == 'OK':
                        email_body = self.parse_email(msg_data[0][1])
                        if email_body['body']:  # Only include emails with content
                            emails.append({
                                'id': email_id.decode(),
                                'subject': email_body['subject'],
                                'from': email_body['from'],
                                'body': email_body['body'],
                                'date': email_body['date']
                            })
                except Exception as e:
                    print(f"Error processing email {email_id}: {e}")
                    continue
            
            mail.close()
            mail.logout()
            return emails
            
        except Exception as e:
            print(f"Error fetching emails: {e}")
            try:
                mail.logout()
            except:
                pass
            return []
    
    def parse_email(self, raw_email):
        """Parse raw email content with better encoding handling"""
        try:
            msg = email.message_from_bytes(raw_email)
            
            # Decode subject
            subject = ""
            subject_header = msg["Subject"]
            if subject_header:
                decoded_parts = decode_header(subject_header)
                for part, encoding in decoded_parts:
                    if isinstance(part, bytes):
                        subject += part.decode(encoding or 'utf-8', errors='ignore')
                    else:
                        subject += str(part)
            else:
                subject = "No Subject"
            
            # Get sender
            from_header = msg.get("From", "Unknown Sender")
            
            # Get date
            date_header = msg.get("Date", "Unknown Date")
            
            # Get body with better encoding handling
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition", ""))
                    
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        try:
                            payload = part.get_payload(decode=True)
                            if payload:
                                body = payload.decode('utf-8', errors='ignore')
                                break
                        except:
                            try:
                                body = part.get_payload(decode=False)
                                break
                            except:
                                continue
            else:
                try:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body = payload.decode('utf-8', errors='ignore')
                    else:
                        body = msg.get_payload(decode=False)
                except:
                    body = msg.get_payload(decode=False)
            
            # Clean up body
            if body:
                body = ' '.join(body.splitlines())  # Remove excessive newlines
                body = body.strip()
            
            return {
                'subject': subject,
                'from': from_header,
                'body': body or 'No content',
                'date': date_header
            }
        except Exception as e:
            print(f"Error parsing email: {e}")
            return {'subject': 'Error', 'from': 'Error', 'body': 'Error parsing email', 'date': 'Error'}
    
    def send_email(self, to_email, subject, body):
        """Send email with proper error handling"""
        if not self.config['email'] or not self.config['password']:
            return False, "Email not configured"
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config['email']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Create secure connection
            context = ssl.create_default_context()
            
            # Connect and send
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.starttls(context=context)  # Secure the connection
            server.login(self.config['email'], self.config['password'])
            text = msg.as_string()
            server.sendmail(self.config['email'], to_email, text)
            server.quit()
            
            return True, "Email sent successfully"
            
        except smtplib.SMTPAuthenticationError:
            return False, "Authentication failed. Check email and app password."
        except smtplib.SMTPConnectError:
            return False, "Connection to SMTP server failed."
        except smtplib.SMTPSenderRefused:
            return False, "Sender refused. Check if you're allowed to send from this address."
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"
    
    def get_email_config_instructions(self):
        """Get instructions for email configuration"""
        return {
            'gmail_instructions': [
                "1. Enable 2-Factor Authentication in your Google Account",
                "2. Go to Google Account Settings → Security → 2-Step Verification",
                "3. Generate an App Password:",
                "   - Go to Google Account → Security → App passwords",
                "   - Select 'Mail' as the app",
                "   - Select your device",
                "   - Copy the 16-character app password",
                "4. Use the app password (not your regular password) in the configuration"
            ],
            'outlook_instructions': [
                "1. For Outlook/Hotmail, you might need to use your regular password",
                "2. Ensure 'Less secure app access' is enabled",
                "3. Or use app-specific passwords if 2FA is enabled"
            ]
        }

class EmailDatasetGenerator:
    def __init__(self):
        self.fake = Faker()
        self.university_domains = [
            "@harvard.edu", "@stanford.edu", "@mit.edu", "@berkeley.edu",
            "@oxford.ac.uk", "@cambridge.ac.uk", "@yale.edu", "@princeton.edu",
            "@columbia.edu", "@chicago.edu", "@umich.edu", "@ucla.edu"
        ]
        self.academic_roles = [
            "Professor", "Associate Professor", "Assistant Professor", "Lecturer",
            "Research Assistant", "Teaching Assistant", "PhD Student", "Masters Student",
            "Undergraduate Student", "Department Head", "Dean", "Advisor"
        ]
        self.course_codes = [
            "CS101", "MATH201", "PHYS301", "BIO401", "CHEM202", "ENG102",
            "HIST151", "PSYCH210", "ECON301", "SOC101", "PHIL202", "ART105"
        ]
        
    def generate_bullying_email(self):
        """Generate a bullying email with academic context"""
        templates = [
            # Direct bullying
            "I've reviewed your {assignment} and I must say this is completely unacceptable. {bullying_phrase} Your work demonstrates a fundamental lack of understanding that is concerning at this stage of your academic career.",
            
            # Academic undermining
            "Regarding your recent {submission}, the quality is far below what we expect from students at this level. {bullying_phrase} You need to seriously reconsider whether you're cut out for this program.",
            
            # Personal attacks
            "Your performance in {course} has been consistently disappointing. {bullying_phrase} Other students are progressing while you seem to be falling further behind.",
            
            # Power imbalance
            "As your {academic_role}, I'm deeply concerned about your capabilities. {bullying_phrase} This level of work is embarrassing for both of us.",
            
            # Subtle bullying
            "While I appreciate your effort on the {project}, the results are quite surprising. {bullying_phrase} I expected better given your background and preparation."
        ]
        
        template = random.choice(templates)
        bullying_phrase = random.choice(BULLYING_PHRASES)
        
        email_content = template.format(
            assignment=random.choice(["assignment", "paper", "thesis chapter", "research proposal"]),
            submission=random.choice(["submission", "project", "research paper", "analysis"]),
            course=random.choice(self.course_codes),
            academic_role=random.choice(["advisor", "professor", "supervisor"]),
            project=random.choice(["research project", "term paper", "dissertation", "capstone"]),
            bullying_phrase=bullying_phrase
        )
        
        return email_content
    
    def generate_non_bullying_email(self):
        """Generate a non-bullying email with academic context"""
        templates = [
            # Positive feedback
            "I wanted to commend you on your excellent work on the {assignment}. {positive_phrase} Your analysis was thorough and well-reasoned, showing significant improvement.",
            
            # Constructive feedback
            "Thank you for your submission of the {project}. {positive_phrase} I've provided some suggestions for further development in the attached feedback.",
            
            # Encouragement
            "Your progress in {course} has been impressive. {positive_phrase} Keep up the good work and don't hesitate to reach out if you need guidance.",
            
            # Professional communication
            "Regarding your {submission}, I appreciate the effort you've put into this. {positive_phrase} There are some areas for improvement that we can discuss during office hours.",
            
            # Supportive
            "I've reviewed your work on the {project} and I'm pleased with your development. {positive_phrase} You're showing strong potential in this area."
        ]
        
        template = random.choice(templates)
        positive_phrase = random.choice(NON_BULLYING_PHRASES)
        
        email_content = template.format(
            assignment=random.choice(["assignment", "paper", "research project"]),
            project=random.choice(["project", "analysis", "research paper"]),
            course=random.choice(self.course_codes),
            submission=random.choice(["submission", "work", "paper"]),
            positive_phrase=positive_phrase
        )
        
        return email_content
    
    def generate_neutral_email(self):
        """Generate a neutral administrative email"""
        templates = [
            "This is a reminder that the {deadline} for {item} is approaching. Please ensure timely submission.",
            "Department announcement: {event} has been scheduled for {date}. All students are expected to attend.",
            "Your {request} has been processed. You can collect the documents from the department office.",
            "Office hours for {course} have been updated. The new schedule is available on the course website.",
            "The {meeting} scheduled for {date} has been {status}. We will notify you of the new arrangements."
        ]
        
        template = random.choice(templates)
        neutral_phrase = random.choice(NEUTRAL_PHRASES)
        
        email_content = template.format(
            deadline=random.choice(["deadline", "due date", "submission date"]),
            item=random.choice(["assignment", "project", "research paper", "thesis proposal"]),
            event=random.choice(["seminar", "workshop", "guest lecture", "department meeting"]),
            date=self.fake.date_between(start_date='-30d', end_date='+30d').strftime('%B %d, %Y'),
            request=random.choice(["transcript request", "recommendation letter", "scholarship application"]),
            course=random.choice(self.course_codes),
            meeting=random.choice(["faculty meeting", "thesis committee", "research group"]),
            status=random.choice(["cancelled", "rescheduled", "moved to virtual"])
        )
        
        return email_content
    
    def generate_sender_info(self, is_bullying=False):
        """Generate realistic sender information"""
        role_weights = {
            "Professor": 0.3,
            "Associate Professor": 0.25,
            "Assistant Professor": 0.2,
            "Lecturer": 0.15,
            "Department Head": 0.05,
            "Dean": 0.05
        } if is_bullying else {
            "Professor": 0.2,
            "Associate Professor": 0.2,
            "Assistant Professor": 0.2,
            "Lecturer": 0.2,
            "PhD Student": 0.1,
            "Teaching Assistant": 0.1
        }
        
        roles = list(role_weights.keys())
        weights = list(role_weights.values())
        role = random.choices(roles, weights=weights)[0]
        
        first_name = self.fake.first_name()
        last_name = self.fake.last_name()
        domain = random.choice(self.university_domains)
        email = f"{first_name.lower()}.{last_name.lower()}{domain}"
        
        return {
            'name': f"{role} {first_name} {last_name}",
            'email': email,
            'role': role
        }
    
    def generate_subject(self, is_bullying=False, is_neutral=False):
        """Generate appropriate email subject"""
        if is_neutral:
            subjects = [
                "Department Announcement",
                "Meeting Schedule Update",
                "Deadline Reminder",
                "Office Hours Change",
                "Important Information"
            ]
        elif is_bullying:
            subjects = [
                "Concerns About Your Performance",
                "Regarding Your Recent Submission",
                "Serious Discussion Needed",
                "Performance Review",
                "Urgent: Academic Progress"
            ]
        else:
            subjects = [
                "Great Work on Your Assignment",
                "Feedback on Your Submission",
                "Progress Update",
                "Research Opportunity",
                "Congratulations on Your Work"
            ]
        
        course = random.choice(self.course_codes)
        return f"{random.choice(subjects)} - {course}"

class EmailAnalyzer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=2000, stop_words='english', ngram_range=(1, 2))
        self.model = None
        self.model_type = None
        self.model_metrics = {}
        self.stop_words = set(stopwords.words('english'))
        self.dataset_generator = EmailDatasetGenerator()
        
    def preprocess_text(self, text):
        """Clean and preprocess email text"""
        if not isinstance(text, str):
            return ""
            
        # Convert to lowercase
        text = text.lower()
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Tokenize and remove stopwords
        tokens = word_tokenize(text)
        tokens = [token for token in tokens if token not in self.stop_words and len(token) > 2]
        return ' '.join(tokens)
    
    def rule_based_check(self, text):
        """Perform rule-based bullying detection"""
        if not isinstance(text, str):
            return [], 0
            
        text_lower = text.lower()
        bullying_matches = []
        
        for phrase in BULLYING_PHRASES:
            if phrase in text_lower:
                bullying_matches.append(phrase)
        
        bullying_score = len(bullying_matches) / len(BULLYING_PHRASES) if BULLYING_PHRASES else 0
        return bullying_matches, bullying_score
    
    def generate_large_dataset(self, num_samples=10000):
        """Generate a large comprehensive dataset"""
        print(f"Generating large dataset with {num_samples} samples...")
        
        emails = []
        labels = []
        senders = []
        subjects = []
        timestamps = []
        
        # Distribution: 40% bullying, 40% non-bullying, 20% neutral
        bullying_count = int(num_samples * 0.4)
        non_bullying_count = int(num_samples * 0.4)
        neutral_count = num_samples - bullying_count - non_bullying_count
        
        # Generate bullying emails
        for i in range(bullying_count):
            if i % 1000 == 0:
                print(f"Generated {i} bullying emails...")
            email_content = self.dataset_generator.generate_bullying_email()
            sender_info = self.dataset_generator.generate_sender_info(is_bullying=True)
            subject = self.dataset_generator.generate_subject(is_bullying=True)
            
            emails.append(email_content)
            labels.append(1)  # Bullying
            senders.append(sender_info['name'])
            subjects.append(subject)
            timestamps.append(fake.date_time_between(start_date='-1y', end_date='now'))
        
        # Generate non-bullying emails
        for i in range(non_bullying_count):
            if i % 1000 == 0:
                print(f"Generated {i} non-bullying emails...")
            email_content = self.dataset_generator.generate_non_bullying_email()
            sender_info = self.dataset_generator.generate_sender_info(is_bullying=False)
            subject = self.dataset_generator.generate_subject(is_bullying=False)
            
            emails.append(email_content)
            labels.append(0)  # Non-bullying
            senders.append(sender_info['name'])
            subjects.append(subject)
            timestamps.append(fake.date_time_between(start_date='-1y', end_date='now'))
        
        # Generate neutral emails
        for i in range(neutral_count):
            if i % 500 == 0:
                print(f"Generated {i} neutral emails...")
            email_content = self.dataset_generator.generate_neutral_email()
            sender_info = self.dataset_generator.generate_sender_info(is_bullying=False)
            subject = self.dataset_generator.generate_subject(is_neutral=True)
            
            emails.append(email_content)
            labels.append(0)  # Neutral classified as non-bullying
            senders.append(sender_info['name'])
            subjects.append(subject)
            timestamps.append(fake.date_time_between(start_date='-1y', end_date='now'))
        
        print("Dataset generation completed!")
        return emails, labels, senders, subjects, timestamps
    
    def save_large_dataset_to_excel(self, num_samples=10000, filename='large_email_dataset.xlsx'):
        """Save large dataset to Excel file with multiple sheets"""
        print(f"Starting generation of {num_samples} samples...")
        
        emails, labels, senders, subjects, timestamps = self.generate_large_dataset(num_samples)
        
        # Create main DataFrame
        df = pd.DataFrame({
            'email_id': range(1, len(emails) + 1),
            'timestamp': timestamps,
            'sender': senders,
            'subject': subjects,
            'email_content': emails,
            'label': labels,
            'label_description': ['Bullying' if label == 1 else 'Not Bullying' for label in labels],
            'word_count': [len(email.split()) for email in emails],
            'character_count': [len(email) for email in emails]
        })
        
        # Add some additional features
        df['has_academic_context'] = df['email_content'].apply(
            lambda x: any(word in x.lower() for word in ['research', 'study', 'paper', 'thesis', 'assignment', 'course'])
        )
        df['urgency_level'] = df['subject'].apply(
            lambda x: 'High' if any(word in x.lower() for word in ['urgent', 'immediate', 'asap', 'important']) else 'Normal'
        )
        
        # Create summary statistics
        summary_data = {
            'Total Samples': [len(emails)],
            'Bullying Emails': [sum(labels)],
            'Non-Bullying Emails': [len(labels) - sum(labels)],
            'Bullying Percentage': [f"{(sum(labels) / len(labels) * 100):.2f}%"],
            'Average Word Count': [f"{df['word_count'].mean():.2f}"],
            'Average Character Count': [f"{df['character_count'].mean():.2f}"],
            'Dataset Created': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        }
        summary_df = pd.DataFrame(summary_data)
        
        # Create label distribution
        label_dist = pd.DataFrame({
            'Label': ['Bullying', 'Non-Bullying'],
            'Count': [sum(labels), len(labels) - sum(labels)],
            'Percentage': [f"{(sum(labels) / len(labels) * 100):.2f}%", 
                          f"{((len(labels) - sum(labels)) / len(labels) * 100):.2f}%"]
        })
        
        # Save to Excel with multiple sheets
        filepath = os.path.join(Config.DATASET_PATH, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Email Dataset', index=False)
            summary_df.to_excel(writer, sheet_name='Dataset Summary', index=False)
            label_dist.to_excel(writer, sheet_name='Label Distribution', index=False)
            
            # Add sample data sheet
            sample_size = min(100, len(df))
            df_sample = df.head(sample_size)
            df_sample.to_excel(writer, sheet_name='Sample Data', index=False)
        
        print(f"Dataset saved to {filepath}")
        
        # Return dataset info
        dataset_info = {
            'filepath': filepath,
            'total_samples': len(emails),
            'bullying_samples': sum(labels),
            'non_bullying_samples': len(labels) - sum(labels),
            'file_size': f"{os.path.getsize(filepath) / (1024*1024):.2f} MB"
        }
        
        return dataset_info
    
    def create_training_dataset(self, num_samples=2000):
        """Create a smaller dataset for immediate training"""
        emails, labels, _, _, _ = self.generate_large_dataset(num_samples)
        return emails, labels

    def train_model(self, model_type='logistic', save_model=True, training_samples=2000):
        """Train the machine learning model"""
        print(f"Training model with {training_samples} samples...")
        emails, labels = self.create_training_dataset(training_samples)
        
        # Preprocess emails
        processed_emails = [self.preprocess_text(email) for email in emails]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            processed_emails, labels, test_size=0.3, random_state=42, stratify=labels
        )
        
        # Vectorize text
        X_train_tfidf = self.vectorizer.fit_transform(X_train)
        X_test_tfidf = self.vectorizer.transform(X_test)
        
        # Train model
        if model_type == 'svm':
            self.model = SVC(kernel='linear', probability=True, random_state=42)
            self.model_type = 'SVM'
        else:
            self.model = LogisticRegression(random_state=42, max_iter=1000)
            self.model_type = 'Logistic Regression'
        
        self.model.fit(X_train_tfidf, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_tfidf)
        y_pred_proba = self.model.predict_proba(X_test_tfidf)
        
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        self.model_metrics = {
            'precision': round(precision, 3),
            'recall': round(recall, 3),
            'f1_score': round(f1, 3),
            'model_type': self.model_type,
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'accuracy': round((y_pred == y_test).mean(), 3)
        }
        
        # Save model if requested
        if save_model:
            self.save_model()
        
        return self.model_metrics

    def save_model(self):
        """Save the trained model and vectorizer"""
        if self.model is None:
            return False
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"{self.model_type}_{timestamp}.joblib"
        vectorizer_filename = f"vectorizer_{timestamp}.joblib"
        
        model_path = os.path.join(Config.MODEL_PATH, model_filename)
        vectorizer_path = os.path.join(Config.MODEL_PATH, vectorizer_filename)
        
        joblib.dump(self.model, model_path)
        joblib.dump(self.vectorizer, vectorizer_path)
        
        # Update latest model reference
        latest_model_path = os.path.join(Config.MODEL_PATH, 'latest_model.joblib')
        latest_vectorizer_path = os.path.join(Config.MODEL_PATH, 'latest_vectorizer.joblib')
        
        joblib.dump(self.model, latest_model_path)
        joblib.dump(self.vectorizer, latest_vectorizer_path)
        
        return True

    def load_model(self, model_type='latest'):
        """Load a trained model"""
        try:
            if model_type == 'latest':
                model_path = os.path.join(Config.MODEL_PATH, 'latest_model.joblib')
                vectorizer_path = os.path.join(Config.MODEL_PATH, 'latest_vectorizer.joblib')
            else:
                # Find the most recent model of specified type
                model_files = [f for f in os.listdir(Config.MODEL_PATH) 
                             if f.startswith(model_type) and f.endswith('.joblib')]
                if not model_files:
                    return False
                model_path = os.path.join(Config.MODEL_PATH, sorted(model_files)[-1])
                vectorizer_path = model_path.replace(model_type, 'vectorizer')
            
            if os.path.exists(model_path) and os.path.exists(vectorizer_path):
                self.model = joblib.load(model_path)
                self.vectorizer = joblib.load(vectorizer_path)
                self.model_type = model_type.capitalize()
                return True
        except Exception as e:
            print(f"Error loading model: {e}")
        
        return False

    def predict_bullying(self, email_text):
        """Predict if email contains bullying content"""
        if self.model is None:
            # Try to load latest model
            if not self.load_model():
                return {"error": "Model not trained. Please train the model first."}
        
        # Rule-based check
        rule_matches, rule_score = self.rule_based_check(email_text)
        
        # ML-based prediction
        processed_text = self.preprocess_text(email_text)
        text_tfidf = self.vectorizer.transform([processed_text])
        ml_prediction = self.model.predict(text_tfidf)[0]
        ml_probability = self.model.predict_proba(text_tfidf)[0][1]
        
        # Combined decision with weighted scoring
        rule_weight = 0.4
        ml_weight = 0.6
        
        combined_score = (rule_score * rule_weight) + (ml_probability * ml_weight)
        final_prediction = 1 if combined_score > 0.5 else 0
        
        return {
            'is_bullying': bool(final_prediction),
            'confidence': round(combined_score, 3),
            'rule_based_matches': rule_matches,
            'rule_based_score': round(rule_score, 3),
            'ml_prediction': bool(ml_prediction),
            'ml_confidence': round(ml_probability, 3),
            'model_used': self.model_type,
            'combined_score': round(combined_score, 3)
        }

# Initialize components
analyzer = EmailAnalyzer()
email_integration = EmailIntegration()

def get_db_connection():
    """Create database connection"""
    try:
        conn = mysql.connector.connect(**Config.DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def init_database():
    """Initialize database tables"""
    try:
        conn = get_db_connection()
        if conn is None:
            print("Failed to connect to database")
            return False
            
        cursor = conn.cursor()
        
        # Create emails table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyzed_emails (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email_subject TEXT,
                email_from TEXT,
                email_text TEXT NOT NULL,
                is_bullying BOOLEAN NOT NULL,
                confidence FLOAT NOT NULL,
                rule_based_matches TEXT,
                rule_based_score FLOAT,
                ml_prediction BOOLEAN,
                ml_confidence FLOAT,
                model_used VARCHAR(50),
                email_date TIMESTAMP NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create users table for authentication
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'moderator',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create model history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                model_type VARCHAR(50) NOT NULL,
                precision_score FLOAT,
                recall_score FLOAT,
                f1_score FLOAT,
                accuracy FLOAT,
                training_samples INT,
                test_samples INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create dataset history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dataset_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                total_samples INT,
                bullying_samples INT,
                non_bullying_samples INT,
                file_size VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create email configuration table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_config (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email_address VARCHAR(255),
                configured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(50)
            )
        ''')
        
        # Create default admin user
        cursor.execute('''
            INSERT IGNORE INTO users (username, password, role) 
            VALUES ('admin', 'admin123', 'admin')
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully")
        return True
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Simple authentication
        if username == 'admin' and password == 'admin123':
            session['user_id'] = 1
            session['username'] = username
            session['role'] = 'admin'
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Email Configuration Routes
@app.route('/api/configure-email', methods=['POST'])
def configure_email():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.json
        email_address = data.get('email')
        app_password = data.get('app_password')
        
        if not email_address or not app_password:
            return jsonify({'success': False, 'error': 'Email and app password are required'})
        
        # Configure email integration
        email_integration.configure_email(email_address, app_password)
        
        # Test connection
        success, message = email_integration.test_connection()
        
        # Store configuration in database
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO email_config (email_address, status) 
                VALUES (%s, %s)
            ''', (email_address, 'success' if success else 'failed'))
            conn.commit()
            cursor.close()
            conn.close()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Email configured successfully',
                'test_result': message
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Email configuration failed',
                'details': message
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/test-email-connection')
def test_email_connection():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        success, message = email_integration.test_connection()
        return jsonify({
            'success': success,
            'message': message,
            'configured': bool(email_integration.config['email'])
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/email-instructions')
def get_email_instructions():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        instructions = email_integration.get_email_config_instructions()
        return jsonify({'success': True, 'instructions': instructions})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/send-test-email', methods=['POST'])
def send_test_email():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.json
        to_email = data.get('to_email', email_integration.config['email'])  # Send to self by default
        
        success, message = email_integration.send_email(
            to_email, 
            "Test Email from BullyMail System", 
            "This is a test email to verify that your email configuration is working correctly.\n\nIf you received this email, your BullyMail system is properly configured for email integration."
        )
        
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Enhanced Dataset Routes
@app.route('/api/generate-large-dataset', methods=['POST'])
def generate_large_dataset():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.json
        num_samples = data.get('num_samples', 10000)
        
        if num_samples > 50000:
            return jsonify({'success': False, 'error': 'Maximum 50,000 samples allowed'})
        
        # Start dataset generation in background
        dataset_info = analyzer.save_large_dataset_to_excel(num_samples=num_samples)
        
        # Store dataset info in database
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO dataset_history 
                (filename, total_samples, bullying_samples, non_bullying_samples, file_size)
                VALUES (%s, %s, %s, %s, %s)
            ''', (
                'large_email_dataset.xlsx',
                dataset_info['total_samples'],
                dataset_info['bullying_samples'],
                dataset_info['non_bullying_samples'],
                dataset_info['file_size']
            ))
            conn.commit()
            cursor.close()
            conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'Large dataset with {num_samples} samples generated successfully',
            'dataset_info': dataset_info
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/generate-dataset', methods=['POST'])
def generate_dataset():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.json
        num_samples = data.get('num_samples', 2000)
        
        dataset_info = analyzer.save_large_dataset_to_excel(num_samples=num_samples)
        
        return jsonify({
            'success': True, 
            'message': f'Dataset with {num_samples} samples generated successfully',
            'dataset_info': dataset_info
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/download-dataset/<filename>')
def download_dataset(filename):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        filepath = os.path.join(Config.DATASET_PATH, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            return jsonify({'success': False, 'error': 'File not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/dataset-history')
def get_dataset_history():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'success': False, 'error': 'Database connection failed'})
            
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT * FROM dataset_history 
            ORDER BY created_at DESC 
            LIMIT 10
        ''')
        
        history = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'history': history})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/available-datasets')
def get_available_datasets():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        datasets = []
        if os.path.exists(Config.DATASET_PATH):
            for filename in os.listdir(Config.DATASET_PATH):
                if filename.endswith('.xlsx'):
                    filepath = os.path.join(Config.DATASET_PATH, filename)
                    file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
                    created_time = datetime.fromtimestamp(os.path.getctime(filepath))
                    
                    datasets.append({
                        'filename': filename,
                        'file_size': f"{file_size:.2f} MB",
                        'created_at': created_time.strftime("%Y-%m-%d %H:%M:%S"),
                        'download_url': f"/api/download-dataset/{filename}"
                    })
        
        return jsonify({'success': True, 'datasets': datasets})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Email Integration Routes
@app.route('/api/fetch-emails', methods=['POST'])
def fetch_emails():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    mailbox = data.get('mailbox', 'INBOX')
    limit = data.get('limit', 10)
    
    try:
        emails = email_integration.fetch_emails(mailbox, limit)
        
        # Analyze each email
        analyzed_emails = []
        for email_data in emails:
            analysis = analyzer.predict_bullying(email_data['body'])
            
            analyzed_email = {
                **email_data,
                'analysis': analysis
            }
            analyzed_emails.append(analyzed_email)
            
            # Store in database
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO analyzed_emails 
                    (email_subject, email_from, email_text, is_bullying, confidence, 
                     rule_based_matches, rule_based_score, ml_prediction, ml_confidence, model_used, email_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    email_data['subject'],
                    email_data['from'],
                    email_data['body'],
                    analysis['is_bullying'],
                    analysis['confidence'],
                    ', '.join(analysis['rule_based_matches']),
                    analysis['rule_based_score'],
                    analysis['ml_prediction'],
                    analysis['ml_confidence'],
                    analysis['model_used'],
                    datetime.now()
                ))
                conn.commit()
                cursor.close()
                conn.close()
        
        return jsonify({'success': True, 'emails': analyzed_emails})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/analyze-email', methods=['POST'])
def analyze_email():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    email_text = data.get('email_text', '')
    email_subject = data.get('email_subject', '')
    email_from = data.get('email_from', '')
    
    if not email_text:
        return jsonify({'error': 'No email text provided'})
    
    try:
        result = analyzer.predict_bullying(email_text)
        
        # Store analysis in database
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO analyzed_emails 
                (email_subject, email_from, email_text, is_bullying, confidence, 
                 rule_based_matches, rule_based_score, ml_prediction, ml_confidence, model_used)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                email_subject,
                email_from,
                email_text,
                result['is_bullying'],
                result['confidence'],
                ', '.join(result['rule_based_matches']),
                result['rule_based_score'],
                result['ml_prediction'],
                result['ml_confidence'],
                result['model_used']
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
        
        return jsonify({'success': True, 'result': result})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/analysis-history', methods=['GET'])
def get_analysis_history():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'success': False, 'error': 'Database connection failed'})
            
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT * FROM analyzed_emails 
            ORDER BY created_at DESC 
            LIMIT 50
        ''')
        
        history = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'history': history})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/system-stats', methods=['GET'])
def get_system_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'success': True, 'stats': {
                'total_analyses': 0,
                'bullying_detected': 0,
                'recent_activity': 0,
                'model_count': 0,
                'dataset_count': 0,
                'detection_rate': 0
            }})
            
        cursor = conn.cursor()
        
        # Total analyses
        cursor.execute('SELECT COUNT(*) FROM analyzed_emails')
        total_analyses = cursor.fetchone()[0]
        
        # Bullying detected
        cursor.execute('SELECT COUNT(*) FROM analyzed_emails WHERE is_bullying = 1')
        bullying_count = cursor.fetchone()[0]
        
        # Recent activity (last 7 days)
        cursor.execute('''
            SELECT COUNT(*) FROM analyzed_emails 
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        ''')
        recent_activity = cursor.fetchone()[0]
        
        # Model count
        cursor.execute('SELECT COUNT(*) FROM model_history')
        model_count = cursor.fetchone()[0]
        
        # Dataset count
        cursor.execute('SELECT COUNT(*) FROM dataset_history')
        dataset_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        stats = {
            'total_analyses': total_analyses,
            'bullying_detected': bullying_count,
            'recent_activity': recent_activity,
            'model_count': model_count,
            'dataset_count': dataset_count,
            'detection_rate': round((bullying_count / total_analyses * 100) if total_analyses > 0 else 0, 2)
        }
        
        return jsonify({'success': True, 'stats': stats})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/model-status')
def model_status():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        model_files = []
        if os.path.exists(Config.MODEL_PATH):
            model_files = [f for f in os.listdir(Config.MODEL_PATH) if f.endswith('.joblib')]
            
        latest_model = 'latest_model.joblib' if 'latest_model.joblib' in model_files else None
        
        # Get model history from database
        conn = get_db_connection()
        history = []
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('''
                SELECT * FROM model_history 
                ORDER BY created_at DESC 
                LIMIT 5
            ''')
            history = cursor.fetchall()
            cursor.close()
            conn.close()
        
        return jsonify({
            'success': True,
            'model_loaded': analyzer.model is not None,
            'model_type': analyzer.model_type,
            'saved_models': model_files,
            'latest_model': latest_model,
            'training_history': history
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/train-model', methods=['POST'])
def train_model():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    model_type = data.get('model_type', 'logistic')
    save_model = data.get('save_model', True)
    training_samples = data.get('training_samples', 2000)
    
    try:
        results = analyzer.train_model(model_type, save_model, training_samples)
        
        # Save model metrics to database
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO model_history 
                (model_type, precision_score, recall_score, f1_score, accuracy, training_samples, test_samples)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                results['model_type'],
                results['precision'],
                results['recall'],
                results['f1_score'],
                results['accuracy'],
                results['training_samples'],
                results['test_samples']
            ))
            conn.commit()
            cursor.close()
            conn.close()
        
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/load-model', methods=['POST'])
def load_model():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    model_type = data.get('model_type', 'latest')
    
    try:
        success = analyzer.load_model(model_type)
        if success:
            return jsonify({'success': True, 'message': f'{model_type} model loaded successfully'})
        else:
            return jsonify({'success': False, 'error': 'Model not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    if init_database():
        print("Starting BullyMail Application...")
        print("Access the application at: http://localhost:5000")
        print("Admin login: admin / admin123")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("Failed to initialize database. Please check your MySQL configuration.")