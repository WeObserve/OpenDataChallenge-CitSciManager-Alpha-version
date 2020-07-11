from flask import Flask, render_template, request, session,flash, redirect, url_for
from config import config
from datastory_service import process_create_datastory, process_view_datastory
from flask_googlemaps import GoogleMaps, Map
from models import DataStoryModel
from forms import PublishForm
import random
from datetime import datetime

app = Flask(__name__)
app.config.from_object(config['dev'])
GoogleMaps(app)


def define_map(datastory_details):
    loc_map = Map(identifier='locations-view',
                      lat=datastory_details.get('files')[0].get('location')[1],
                      lng=datastory_details.get('files')[0].get('location')[0],
                      markers=[{'lat': file.get('location')[1],
                                'lng': file.get('location')[0],
                                'infobox': "Image: " + str(file.get('path')) +
                                           "\n Location: " + str(tuple(file.get('location'))) +
                                           "\n Date: " + str(file.get('date')) +
                                           "\n Contributor: " + str(datastory_details.get('senders')
                                                                    .get(file.get('uuid')).get('name'))}
                               for file in datastory_details.get('files')],
                      fit_markers_to_bounds=True)
    return loc_map


def set_project_details_form(form, datastory_details):
    contributors = [details.get('name') for sender, details in datastory_details.get('senders').items()]
    for contributor in contributors:
        form.draft_form.project_details_form.contributors.append_entry(contributor)
    form.draft_form.project_details_form.project_owner.data = datastory_details.get('owner').get('name')
    form.draft_form.project_details_form.organization.data = datastory_details.get('organization')
    if datastory_details.get('content'):
        form.draft_form.editordata.data = datastory_details.get('content')
    else:
        form.draft_form.editordata.data = ""


def generate_random_string():
    # Need to handle unique urls in a better way. We can check if the url already exists in the database and generate
    # new one if exists. But in that case it needs more calls to database. Another option is to use uuid python library
    # but the unique ids are not readable. With current code, we cannot add unique index on the field unique_url. This
    # is because we save drafts in the same collection and drafts do not have unique urls. If we have more than one
    # draft, unique index will raise on error.
    all_chars = 'abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    unique_url = ''.join(random.choice(all_chars) for i in range(3))+'-'\
                 + ''.join(random.choice(all_chars) for i in range(3))+'-'\
                 + ''.join(random.choice(all_chars) for i in range(3))
    return unique_url


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/collect', methods=['GET', 'POST'])
def collect():
    return render_template('collect.html')

# Current code makes many calls to database during create data stories and sets the form and map every time. As we use
# Google Maps API setting map every time is expensive and needs to be improved. I was unable to use session to store the
# data. We may need to look into other options to improve performance by reducing the number of calls to database.

# Also, this code does not take into account different users. This need to be updated so that user id is also used when
# making the calls to database. User id must be retreived from session and must be passed as a varaible in all calls.
@app.route('/datastories/', methods=['GET', 'POST'])
def create_datastories():
    form = PublishForm()
    projects = DataStoryModel().get_projects()
    form.draft_form.project_details_form.project_id.choices = [(p.get('projectid'), p.get('name')) for p in projects]
    published_stories = DataStoryModel().get_published_datastories()
    for story in published_stories:
        form.draft_form.project_details_form.published_stories.append_entry(story)
    #print(published_stories)
    print('This is get datastories..')
    if request.method == "POST":
        project_id = form.draft_form.project_details_form.project_id.data
        #print(project_id)
        datastory_details = DataStoryModel().get_datastory_details(project_id)
        #print(datastory_details)

        if "plot-dataset-on-map" in request.form:
            print('Reached plot on map..')
            loc_map = define_map(datastory_details)
            set_project_details_form(form, datastory_details)
            #print(form.draft_form.project_details_form.contributors)
            #print(form.draft_form.editordata)
            return render_template('datastory.html', map=loc_map, form=form)

        elif "save-draft-datastory" in request.form:
            print('Reached save draft..')
            #print(form.draft_form.editordata.data)
            datastory_details['content'] = form.draft_form.editordata.data
            loc_map = define_map(datastory_details)
            set_project_details_form(form, datastory_details)
            DataStoryModel().save_draft_datastory(datastory_details)  # Add validation
            return render_template('datastory.html', map=loc_map, form=form)

        elif "discard-draft-datastory" in request.form:
            print('Reached discard draft..')
            datastory_details['content'] = ""
            set_project_details_form(form, datastory_details)
            DataStoryModel().save_draft_datastory(datastory_details)
            loc_map = define_map(datastory_details)
            return render_template('datastory.html', map=loc_map, form=form)

        elif "publish-datastory" in request.form:
            print('Reached publish..')
            #print(datastory_details)
            # For now text editor data is stored as html string including images. We may need to extract attachments and
            # store them in another location to save size.
            datastory_details['content'] = form.draft_form.editordata.data
            set_project_details_form(form, datastory_details)
            loc_map = define_map(datastory_details)
            if datastory_details.get('content') == "":
                flash('Please enter your story.')
                return render_template('datastory.html', map=loc_map, form=form)
            else:
                unique_url = generate_random_string()
                datastory_details['unique_url'] = unique_url
                datastory_details['published_date'] = datetime.now()
                form.unique_url.data = unique_url
                DataStoryModel().publish_datastory(datastory_details)
                # Call email service with senders and owner email address
                return render_template('datastory.html', map=loc_map, form=form)
    return render_template('datastory.html', map=None, form=form)


@app.route('/datastories/<url>')
def view_datastory(url):
    print(url)
    datastory_details = DataStoryModel().view_datastory(url)
    loc_map = define_map(datastory_details)
    return render_template('publish.html',map=loc_map, datastory=datastory_details)


if __name__ == '__main__':
    app.run(debug=True)
