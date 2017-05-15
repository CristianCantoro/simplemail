#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Adapted from:
# http://www.finefrog.com/2008/05/06/sending-email-with-attachments-in-python/

import os
import sys
import smtplib
from smtplib import SMTPAuthenticationError
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

import logging
logger=logging.getLogger('mail.mandamail')

logger.setLevel(logging.DEBUG)


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class ConnectionError(Error):
  
  def __init__(self, server):
    self.server = server
    self.msg = "Errore nella connessione al server %s" %server

    logger.error(self.msg)
    sys.stderr.write(self.msg)


import getpass

def auth(smtp, username, password):
  try:
    smtp.login(username,password)
  except SMTPAuthenticationError:
    logger.error("Autenticazione fallita.")
    return False
  
  logger.info("Autenticazione avvenuta correttamente.")
  return True

AVAILABLE_FORMATS = ['html', 'plaintext', 'both']

def attach_both(message, html_text, plaintext_text):
    part1 = MIMEText(plaintext_text , 'plain')
    part2 = MIMEText(html_text , 'html')
    
    message.attach(part1)
    message.attach(part2)
    
def attach_html(message, html_text, plaintext_text):
    part2 = MIMEText(html_text , 'html')
    message.attach(part2)

def attach_plaintext(message, html_text, plaintext_text):
    part1 = MIMEText(plaintext_text , 'plain')
    message.attach(part1)


ATTACH = {
'html': attach_html,
'plaintext': attach_plaintext,
'both': attach_both
}

def inviamail(app=None, mailfrom='', mailto=None, files=None, cc=None, bcc=None, \
          server = None, auth_required=False, username='', password=None, \
          subject='', mail_format=None, html_text='', plaintext_text='', \
          blacklist=None, passwd_force_ask=False, dry_send=False):
    
    if mailto is None:
      mailto=[]
      
    if files is None:
      files=[]
      
    if cc is None:
      cc=[] 
      
    if bcc is None:
      bcc=[]
      
    if blacklist is None:
      blacklist=[]
    
    logger.debug("files: %s" %files)
    assert isinstance(files, list)
    
    logger.debug("cc: %s" %cc)
    assert isinstance(cc,list)
    
    logger.debug("bcc: %s" %bcc)
    assert isinstance(bcc,list)

    logger.debug("auth_required: %s" %auth_required)
    assert isinstance(auth_required,bool)

    logger.debug("passwd_force_ask: %s" %passwd_force_ask)
    assert isinstance(passwd_force_ask,bool)

    logger.debug("dry_send: %s" %dry_send)
    assert isinstance(dry_send,bool)
    
    logger.debug("mail_format: %s" %mail_format)
    assert mail_format in AVAILABLE_FORMATS

    # Record the MIME types of both parts - text/plain and text/html.
   
    logger.debug("mailto: %s" %mailto)
    logger.debug("cc: %s" %cc)
    logger.debug("bcc: %s" %bcc)
    
    mailto = set(mailto)
    cc=set(cc)
    bcc=set(bcc)
    
    mailto.difference_update(blacklist)
    cc.difference_update(blacklist)
    bcc.difference_update(blacklist)
    
    mailto = list(mailto)
    cc = list(cc)
    bcc = list(bcc)

    # Bug that I forgot to fix from 6 years ago:
    # https://forum.mozillaitalia.org/index.php?topic=49084.0
    # The primary MIME type of the message must be 'mixed' and
    # not 'alternative'
    message = MIMEMultipart('mixed')
    message['From'] = mailfrom
    message['To'] = COMMASPACE.join(mailto)
    message['Date'] = formatdate(localtime=True)
    message['Subject'] = subject
    message['Cc'] = COMMASPACE.join(cc)
    message['Bcc'] = COMMASPACE.join(bcc)

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    
    ATTACH[mail_format](message, html_text, plaintext_text)

    for f in files:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(f, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
        message.attach(part)
   
    mailto = list(mailto)
    mailto.extend(cc)
    mailto.extend(bcc)
    
    addresses = list(set(mailto))

    #print message.as_string()
    msg = """ EMAIL SUMMARY
    Email will be sent to: %s
    file attached: %s
""" %(', '.join(addresses), ', '.join(files))

    logger.info(msg)
    try:
      smtp = smtplib.SMTP(server)
      smtp.ehlo()
    except ConnectionError(server):
      logger.error("Errore nella connessione al server")
      return -1
      
    if auth_required:
      smtp.starttls()

      if password == None or not auth(smtp, username, password) or passwd_force_ask:
        while 1:
            password = getpass.getpass("Password:")
            if auth(smtp, username, password):
                break              

        logger.info("Login avvenuto correttamente")
      
    if not dry_send:
        smtp.sendmail(mailfrom, addresses, message.as_string())

    smtp.close()
    
    logger.info("Email inviata correttamente")
    
    return 0


# ----- main -----
if __name__ == '__main__':
    pass
