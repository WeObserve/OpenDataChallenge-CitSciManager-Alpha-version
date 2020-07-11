from pymongo import MongoClient
from config import config


class DataStoryModel:
    def __init__(self):
        self.client = MongoClient(config['dev'].DB_URI,maxPoolSize=50,wtimeOut=2500)
        self.db = self.client[config['dev'].DB_NAME]

    def get_projects(self):
        projects = {}
        try:
            projects = self.db.projects.find({},{"projectid":1,"name":1})
        except Exception as e:
            print(e)
        return projects

    def get_file_details(self, project):
        file_details = []
        try:
            file_details = list(self.db.files.find({"projectid":project},{"_id":0,"projectid":0}))
        except Exception as e:
            print(e)
        return file_details

    def get_project_details(self,project):
        project_details = {}
        try:
            project_details = self.db.projects.find_one({"projectid":project},
                                                    {"projectid":1,"name":1,"organization":1,
                                                     "owner.name":1,"owner.email":1,"datastories":1,"_id":0})
        except Exception as e:
            print(e)
        return project_details

    def get_sender_details(self,senders):
        sender_details = []
        try:
            sender_details = list(self.db.users.find({"_id":{"$in":senders}},{"name":1,"email":1}))
        except Exception as e:
            print(e)
        return sender_details

    def find_draft_datastory_details(self,project):
        datastory_details = {}
        try:
            datastory_details = self.db.datastories.find_one({"projectid":project,"status":{"$eq":"draft"}})
        except Exception as e:
            print(e)
        return datastory_details

    def get_datastory_details(self, project):
        #print(project)
        datastory_details = self.find_draft_datastory_details(project)
        if datastory_details:
            return datastory_details
        else:
            file_details = self.get_file_details(project)
            project_details = self.get_project_details(project)
            senders = list(set([file.get('uuid') for file in file_details]))
            sender_details = {doc.pop('_id',None):doc for doc in self.get_sender_details(senders)}
            datastory_details = project_details
            datastory_details.update({'files': file_details, 'senders':sender_details})
         #   print(datastory_details)
            return datastory_details

    def save_draft_datastory(self,datastory):
        print(f'In Models: {datastory}')
        #datastory['status'] = 'draft'
        result = self.db.datastories.update_one({'projectid':datastory.get('projectid'),
                                                       'status':{'$exists':True,'$eq':'draft'}},
                                                      {'$set':{
                                                          'content':datastory.get('content'),
                                                          'files':datastory.get('files'),
                                                          'senders':datastory.get('senders')
                                                      },
                                                      '$setOnInsert':{
                                                          "projectid":datastory.get('projectid'),
                                                          "name":datastory.get('name'),
                                                          "organization":datastory.get('organization'),
                                                          "owner":datastory.get('owner'),
                                                          "status":"draft"
                                                      }},
                                                      upsert=True)
        #print(f'result is: {result}')
        print(result.upserted_id)
        if result.upserted_id:
            self.update_project_datastory(datastory.get('projectid'),result.upserted_id)

    def update_project_datastory(self,projectid,id):
        print('Reached update project datastory..')
        result = self.db.projects.update_one({'projectid':projectid},
                                             {'$addToSet':{
                                                 "datastories":id}},
                                             upsert=True)
        #print(result)


    def publish_datastory(self, datastory):
        result = self.db.datastories.update_one({'projectid': datastory.get('projectid'),
                                                 'status': {'$exists': True, '$eq': 'draft'}},
                                                {'$set': {
                                                    'content': datastory.get('content'),
                                                    'files': datastory.get('files'),
                                                    'senders': datastory.get('senders'),
                                                    'status': "published",
                                                    'unique_url':datastory.get('unique_url'),
                                                    'published_date':datastory.get('published_date')
                                                }},
                                                upsert=True)
        #print(f'result is: {result}')

    def view_datastory(self, url):
        datastory_details = {}
        try:
            datastory_details = self.db.datastories.find_one({'unique_url':url},
                                              {'_id':0})
        except Exception as e:
            print(e)
        return datastory_details

    def get_published_datastories(self):
        datastories = []
        try:
            result = list(self.db.datastories.find({"status":"published"}, {"unique_url": 1,"_id": 0}))
            datastories = [result[i].get('unique_url') for i in range(len(result)) ]
        except Exception as e:
            print(e)
        return datastories





