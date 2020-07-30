from flask_wtf import FlaskForm
from wtforms import SelectField, FieldList, FormField, StringField, TextAreaField, SubmitField, PasswordField, \
    BooleanField, MultipleFileField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_wtf.file import FileAllowed, FileRequired


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
    unique_url = StringField("Unique URL")


class CreateProjectForm(FlaskForm):
    project_name = StringField(u'Create Project')
    license = SelectField(u'Attach License', choices=[('creative commons', 'Creative Commons'),
                                                      ('non-commercial', 'Non-Commercial')])


class UploadDataFilesForm(FlaskForm):
    raw_file_type = SelectField(u'Select Type of Files', choices=[('images', 'Images')])
    raw_data_files = MultipleFileField(u'Data Files', id='raw_data_files')


class UploadMetadataForm(FlaskForm):
    meta_file_type = SelectField(u'Select Type of Files', choices=[('csv', 'CSV')])
    meta_data_files = MultipleFileField(u'Data Files', id='metadata_files')


class DataProcessorForm(FlaskForm):
    project_id = StringField(u'Project ID')
    create_project_form = FormField(CreateProjectForm)
    upload_raw_data_form = FormField(UploadDataFilesForm)
    upload_metadata_form = FormField(UploadMetadataForm)


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=6, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Join Now')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
