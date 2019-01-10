# Google Cloud Datastore 

> To start using google cloud datastore in your project you must install **google-cloud-datastore** library:  
```pip install google-cloud-datastore```

Related files: [**flask_blogging/gcdatastore.py**](/../../blob/master/flask_blogging/gcdatastore.py)

**Required configuration parameters(environment variables):**  
  - **Config parameter name** - `GOOGLE_APPLICATION_CREDENTIALS`  
  `GOOGLE_APPLICATION_CREDENTIALS` - it's a path to the service account credentials. 

## Preparation stage
* Choose a project you'll work with
* [Go to the console](https://console.cloud.google.com/apis/library/datastore.googleapis.com) and enable **Cloud Datastore API** if it doesn't yet.
* Your project requires an active App Engine application. Confirm that your project has an active App Engine app from the [App Engine dashboard](https://appengine.google.com/dashboard).
* [Create](https://cloud.google.com/iam/docs/service-accounts) a service account for your project and download *.json file with credentials.
* Set **Cloud Datastore Owner** role for you service account, or more granular permissions.  
* Install [gcloud](https://cloud.google.com/sdk/gcloud/) or using a web UI do the following:
  - create the file `index.yaml` and write into it:
     ```indexes:

		- kind: Post
		  properties:
		  - name: post_id
		  - name: tags

		- kind: Post
		  properties:
		  - name: user_id
		  - name: post_date
			direction: desc
     ```
  - activate service account:  
    ```gcloud auth activate-service-account [ACCOUNT] --key-file=KEY_FILE [--password-file=PASSWORD_FILE     | --prompt-for-password] [GCLOUD_WIDE_FLAG …]```  
  - create composite indexes(`it's required for the tags filtering`):  
    ```gcloud datastore create-indexes index.yaml```  

## Usage
* Install all requirements for your project and **google-cloud-datastore** library as well.
* Set environment variable `GOOGLE_APPLICATION_CREDENTIALS` with path to your service account creadentials file in a terminal or in your code:
```python
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/user/app/credentials.json"
```  
* import class GoogleCloudDatastore:
```python
from flask_blogging.gcdatastore import GoogleCloudDatastore
```
* And now you can use it! For example:
```python
gc_datastore = GoogleCloudDatastore()
blog_engine = BloggingEngine(app, gc_datastore, file_upload=file_upload)
```
