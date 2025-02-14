
import os
import secrets

from flask import url_for
from flask_login import current_user
from flask_mail import Message
from flaskblog import app, mail
from PIL import Image


def save_picture(form_picture):
    '''Updates a user's profile picture'''

    # Delete the current profile picture from the 'server'.
    prev_picture = os.path.join(app.root_path, 'static/profile_pics', current_user.image_file)
    if not prev_picture.endswith('default.jpg'):
        os.remove(prev_picture)

    # Encode the image name to a random hex.
    random_hex = secrets.token_hex(8)

    # Assemble the path and filename of the new image with the hexed name.
    _, file_ext = os.path.splitext(form_picture.filename)
    picture_file_name = random_hex + file_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_file_name)

    # Resize the image.
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    # Save and return the new, resized image.
    i.save(picture_path)
    return picture_file_name


def send_reset_email(user):
    '''Sends an email to the user with the reset token.'''

    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='flaskblog.vs@gmail.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link
        {url_for('users.reset_token', token=token, _external=True)}

        If you did not make this request then simply ignore this email and no changes will be made.
        '''
    mail.send(msg)
    