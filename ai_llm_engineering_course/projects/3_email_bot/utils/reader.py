from imap_tools import MailBox, AND
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import os
import re 

load_dotenv()

# Dados da sua conta Gmail
class EmailReader:
    def __init__(self, params):
        self.params = params
        self.email = os.getenv("MAILER_ADDRESS")
        self.password = os.getenv("MAILER_PWD")
        self.seen = params.get("seen", False)

    def read_emails(self):
        emails = []
        with MailBox("imap.gmail.com").login(self.email, self.password, initial_folder="INBOX") as mailbox:
            for msg in mailbox.fetch(AND(seen=self.seen), limit=1, reverse=True):

                # Print detailed information about the email for debugging
                print("\n===== EMAIL DETAILS =====")
                print(f"From: {msg.from_}")
                print(f"To: {msg.to}")
                print(f"Subject: {msg.subject}")
                print(f"Date: {msg.date}")
                print(f"Message-ID: {msg.headers.get('Message-ID', 'N/A')}")
                print(f"In-Reply-To: {msg.headers.get('In-Reply-To', 'N/A')}")
                print(f"References: {msg.headers.get('References', 'N/A')}")
                
                # Print all headers for debugging
                print("\n----- All Headers -----")
                for header, value in msg.headers.items():
                    print(f"{header}: {value}")
                
                # Check if this is a reply based on headers
                is_reply = "In-Reply-To" in msg.headers or "References" in msg.headers
                print(f"\nEmail headers indicate this is {'a reply' if is_reply else 'a new message'}")
                
                # Check if this email was sent by the account owner
                is_sent_by_owner = False
                if msg.from_ and self.email in msg.from_:
                    print(f"This email was sent by the account owner: {msg.from_}")
                    is_sent_by_owner = True
                else:
                    print(f"This email was received from: {msg.from_}")
                
                # Print subject for debugging
                if msg.subject and ('Re:' in msg.subject or 'RE:' in msg.subject or 'res:' in msg.subject):
                    print("Subject indicates this is a reply")
                    is_reply = True
                
                # Get the body content
                body = msg.html if msg.html else msg.text
                is_html = bool(msg.html)
                
                # Print a sample of the raw body for debugging
                print("\n----- Raw Body Sample (first 300 chars) -----")
                print(body[:300] + "..." if len(body) > 300 else body)
                
                # Extract reply and original content
                reply_body, original_body = self.extract_reply(body, is_html, is_reply, is_sent_by_owner)
                
                print("\n----- Extracted Content -----")
                print("REPLY BODY:", reply_body[:100] + "..." if len(reply_body) > 100 else reply_body)
                print("ORIGINAL BODY:", original_body[:100] + "..." if len(original_body) > 100 else original_body)
                print("===== END EMAIL DETAILS =====\n")

                emails.append({
                    "id": msg.uid,
                    "from": msg.from_,
                    "subject": msg.subject,
                    "text": reply_body,
                    "original_text": original_body,
                    "is_reply": is_reply,
                    "in_reply_to": msg.headers.get("In-Reply-To", None),
                    "message_id": msg.headers.get("Message-ID", None),
                    "raw": msg,
                })
        return emails

    def extract_reply(self, text, is_html=False, is_reply=False, is_sent_by_owner=False):
        """
        Extract reply and original message from email content.
        
        Args:
            text: The email body text
            is_html: Whether the email is in HTML format
            is_reply: Whether the email is a reply based on headers
            is_sent_by_owner: Whether the email was sent by the account owner
            
        Returns:
            tuple: (reply_body, original_body)
        """
        # For debugging
        print(f"\nProcessing {'HTML' if is_html else 'plain text'} email")
        print(f"is_reply: {is_reply}, is_sent_by_owner: {is_sent_by_owner}")
        
        # If this email was sent by the account owner, it's a reply
        if is_sent_by_owner:
            print("This email was sent by the account owner, treating as reply")
            # For emails sent by the owner, we want to put the content in reply_body
            return text.strip() if text else "", ""
            
        # If it's not a reply according to headers, we might want to handle it differently
        if not is_reply:
            print("Email headers indicate this is a new message, not a reply")
            # For new messages from others, we want to put the content in original_body
            if not self._looks_like_reply(text, is_html):
                print("Content analysis confirms this is a new message")
                # For a new message from someone else, set the entire content as original
                return "", text.strip() if text else ""
        
        if is_html:
            soup = BeautifulSoup(text, 'html.parser')
            
            # Method 1: Look for Gmail's standard quote markers
            gmail_quote = soup.find('div', class_='gmail_quote')
            if gmail_quote:
                print("Found gmail_quote div")
                original = gmail_quote.get_text().strip()
                gmail_quote.extract()  # Remove the quote from the soup
                reply = soup.get_text().strip()
                return reply, original
            
            # Method 2: Look for blockquote elements (common in many email clients)
            blockquote = soup.find('blockquote')
            if blockquote:
                print("Found blockquote element")
                original = blockquote.get_text().strip()
                blockquote.extract()
                reply = soup.get_text().strip()
                return reply, original
                
            # Method 3: Look for quoted content with specific styling
            # Gmail often adds a color style to quoted text
            quoted_text = soup.find(['span', 'font'], style=lambda s: s and ('color' in s.lower() or 'rgb' in s.lower()))
            if quoted_text and len(quoted_text.get_text()) > 50:  # Ensure it's substantial text
                print("Found quoted text with styling")
                original = quoted_text.get_text().strip()
                quoted_text.extract()
                reply = soup.get_text().strip()
                return reply, original
                
            # Method 4: Look for div with specific attributes that Gmail uses
            gmail_extra = soup.find('div', {'data-smartmail': 'gmail_quote'})
            if gmail_extra:
                print("Found div with data-smartmail attribute")
                original = gmail_extra.get_text().strip()
                gmail_extra.extract()
                reply = soup.get_text().strip()
                return reply, original
            
            # Method 5: Look for Gmail's specific structure with hr tags
            hr_tags = soup.find_all('hr')
            for hr in hr_tags:
                # Check if this hr tag is followed by a div that might contain the original message
                next_div = hr.find_next('div')
                if next_div and len(next_div.get_text()) > 100:  # Substantial content
                    print("Found hr tag followed by content div")
                    original = next_div.get_text().strip()
                    hr.extract()
                    next_div.extract()
                    reply = soup.get_text().strip()
                    return reply, original
                
            # If we couldn't find HTML markers, convert to text and try text-based methods
            print("No HTML markers found, converting to text")
            full_text = soup.get_text()
        else:
            full_text = text
            
        # Print a sample of the text for debugging
        print(f"Text sample (first 100 chars): {full_text[:100]}")

        # Enhanced list of common email separators
        splitters = [
            # Portuguese patterns
            r"(?i)^Em .+, .+ escreveu:$",
            r"(?i)^Em .+ escreveu:$",
            r"(?i)^De: .+$",
            r"(?i)^-----Mensagem original-----$",
            # English patterns
            r"(?i)^On .+ wrote:$",
            r"(?i)^On .+, .+ wrote:$",
            r"(?i)^From: .+$",
            r"(?i)^----- Original Message -----$",
            r"(?i)^----- Forwarded Message -----$",
            # Generic patterns
            r"(?i)^>+\s*$",  # Lines with only > characters
            r"(?i)^--+\s*$",  # Divider lines
            r"(?i)^Sent from .+$",  # "Sent from my iPhone" etc.
        ]

        # Try to split by common separators
        for splitter in splitters:
            parts = re.split(splitter, full_text, maxsplit=1, flags=re.MULTILINE)
            if len(parts) > 1:
                print(f"Split successful using pattern: {splitter}")
                return parts[0].strip(), parts[1].strip()

        # Enhanced fallback: Look for patterns of quoted lines (starting with >)
        lines = full_text.splitlines()
        reply_lines = []
        original_lines = []
        quote_marker_count = 0
        
        # First pass: count lines with quote markers
        for line in lines:
            if line.strip().startswith(">"):
                quote_marker_count += 1
                
        # If we have a significant number of quoted lines, process them
        if quote_marker_count > 2:  # At least 3 quoted lines to consider it a pattern
            print(f"Found {quote_marker_count} lines with '>' markers")
            in_original = False
            
            for line in lines:
                stripped = line.strip()
                if stripped.startswith(">"):
                    in_original = True
                    # Remove the > marker and add to original lines
                    original_lines.append(re.sub(r'^>+\s*', '', stripped))
                elif in_original and not stripped:
                    # Empty lines within quoted content stay with the original
                    original_lines.append('')
                else:
                    # Non-quoted lines go to the reply
                    reply_lines.append(stripped)
                    
            reply = "\n".join(reply_lines).strip()
            original = "\n".join(original_lines).strip()
            
            if original:  # Only return if we actually found original content
                return reply, original
        
        # Last resort: Try to identify a signature block as a separator
        signature_patterns = [
            r"(?i)^--\s*$",  # Common signature separator
            r"(?i)^Regards,\s*$",
            r"(?i)^Best regards,\s*$",
            r"(?i)^Atenciosamente,\s*$",
            r"(?i)^Att\.,\s*$",
        ]
        
        for pattern in signature_patterns:
            for i, line in enumerate(lines):
                if re.match(pattern, line.strip()) and i < len(lines) - 1:
                    # Found a potential signature separator
                    reply = "\n".join(lines[:i]).strip()
                    original = "\n".join(lines[i:]).strip()
                    if original and len(original) > 20:  # Ensure it's substantial
                        print(f"Split by signature pattern: {pattern}")
                        return reply, original
        
        # If all else fails and it's a reply according to headers, try to make an educated guess
        if is_reply:
            print("Headers indicate this is a reply, but no clear separation found in content")
            # For replies without clear separation, we might want to set a portion as original
            # This is a heuristic approach - adjust as needed
            if len(full_text) > 200:  # If it's a substantial message
                # Assume the first part is the reply and the rest might be original
                # This is just a guess - you might want to adjust this logic
                split_point = len(full_text) // 3  # Use the first third as reply
                return full_text[:split_point].strip(), full_text[split_point:].strip()
        
        # If it's not a reply or we couldn't find any separation, treat according to headers and sender
        if is_sent_by_owner:
            print("No clear separation found, but this is from the account owner")
            # For emails sent by the owner, put content in reply_body
            return full_text.strip(), ""
        elif is_reply:
            print("No clear separation found, but headers indicate this is a reply")
            # For replies without clear separation, we set the entire content as reply
            return full_text.strip(), ""
        else:
            print("No clear separation found, treating as new message")
            # For new messages from others, set the entire content as original
            return "", full_text.strip()
            
    def _looks_like_reply(self, text, is_html=False):
        """
        Analyze content to determine if it looks like a reply regardless of headers.
        
        Args:
            text: The email body text
            is_html: Whether the email is in HTML format
            
        Returns:
            bool: True if the content looks like a reply, False otherwise
        """
        # Check for common reply indicators in the content
        reply_indicators = [
            r"(?i)Em .+ escreveu:",
            r"(?i)On .+ wrote:",
            r"(?i)-----Mensagem original-----",
            r"(?i)----- Original Message -----",
            r"(?i)----- Forwarded Message -----",
            r"(?i)^>",  # Lines starting with >
        ]
        
        if is_html:
            # For HTML, check if there are quote elements
            soup = BeautifulSoup(text, 'html.parser')
            if (soup.find('blockquote') or 
                soup.find('div', class_='gmail_quote') or 
                soup.find('div', {'data-smartmail': 'gmail_quote'})):
                return True
                
            # Convert to text for further checks
            content = soup.get_text()
        else:
            content = text
            
        # Check for reply indicators in the text
        for indicator in reply_indicators:
            if re.search(indicator, content, re.MULTILINE):
                return True
                
        # Check if there are multiple lines starting with >
        lines = content.splitlines()
        quote_lines = sum(1 for line in lines if line.strip().startswith('>'))
        if quote_lines > 2:  # If there are at least 3 quoted lines
            return True
            
        return False
