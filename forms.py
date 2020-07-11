from flask_wtf import FlaskForm
from wtforms import SelectField, FieldList, FormField, StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class PlotDatasetForm(FlaskForm):
    project_id = SelectField(u'Select a project:', choices=[], validators=[DataRequired()])
    published_stories = FieldList(StringField(u'Published Data stories:'))
    contributors = FieldList(StringField(u'Contributors:'))
    project_owner = StringField(u'Project Owner: ')
    organization = StringField(u'Organization: ')


class SaveDraftForm(FlaskForm):
    project_details_form = FormField(PlotDatasetForm)
    editordata = TextAreaField(id="summernote")


class PublishForm(FlaskForm):
    draft_form = FormField(SaveDraftForm)
   # publish_button = SubmitField("Publish Data Story")
    unique_url = StringField("Unique URL")





