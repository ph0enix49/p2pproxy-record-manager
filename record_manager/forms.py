#!/usr/bin/env python

from flask_wtf import Form
from flask.ext.babel import gettext as _
from wtforms import BooleanField
from wtforms.fields import SelectField, DateTimeField
from wtforms.validators import DataRequired

class RecordForm(Form):
    """
    Form for records
    """
    channel_id = SelectField(_(u'Channel'), coerce=int)
    start = DateTimeField(
        format='%d-%m-%Y %H:%M',
        validators=[DataRequired()])
    end = DateTimeField(format='%d-%m-%Y %H:%M', validators=[DataRequired()])
    # not implemented
    recurring = BooleanField(_(u'Recurring'), default=False)
