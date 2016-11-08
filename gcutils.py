import boto
import gcs_oauth2_boto_plugin
import shutil
import StringIO
import tempfile
import os
from six.moves import cPickle

class GoogleCloudService():
	def __init__(self, data_dir):
		self.data_dir = data_dir
		self.GOOGLE_STORAGE = 'console.cloud.google.com/storage/browser'
		self.TENSORFLOW_BUCKET = 'rnn-tensorflow'
		self.CLIENT_ID = '857458742632-lrt61p69cvb8bc4sa5lv3k8adterfc3t.apps.googleusercontent.com'
		self.CLIENT_SECRET = 'f58f6QWrjj1qqTZjIrFR5Fna'
		self.project_id = 'crucial-raceway-148802'
	
	def upload_file_google_cloud(self, filename, fileObject):
	    # Make some temporary files.
	    temp_dir = tempfile.mkdtemp(prefix='googlestorage')
	    tempfiles = {
	        filename : fileObject
	    }
	    for temp_filename, contents in tempfiles.iteritems():
	      with open(os.path.join(temp_dir, temp_filename), 'wb') as fh:
	            cPickle.dump(contents, fh)
	    
	    # Upload these files to TENSORFLOW_BUCKET.
	    for temp_filename in tempfiles:
	      with open(os.path.join(temp_dir, temp_filename), 'r') as localfile:
	    
	        dst_uri = boto.storage_uri(
	            self.TENSORFLOW_BUCKET + '/' + self.data_dir + '/' + temp_filename, self.GOOGLE_STORAGE)
	        # The key-related functions are a consequence of boto's
	        # interoperability with Amazon S3 (which employs the
	        # concept of a key mapping to localfile).
	        dst_uri.new_key().set_contents_from_file(localfile)
	      print 'Successfully created "%s/%s"' % (
	          dst_uri.bucket_name, dst_uri.object_name)
	
	
	def download_file_google_cloud(self, filename):
	    gcs_oauth2_boto_plugin.SetFallbackClientIdAndSecret(self.CLIENT_ID, self.CLIENT_SECRET)
	    
	    src_uri = boto.storage_uri(
	        self.TENSORFLOW_BUCKET + '/' + self.data_dir + '/' + filename, self.GOOGLE_STORAGE)
	    
	    # Create a file-like object for holding the object contents.
	    object_contents = StringIO.StringIO()
	    # The unintuitively-named get_file() doesn't return the object
	    # contents; instead, it actually writes the contents to
	    # object_contents.
	    src_uri.get_key().get_file(object_contents)
	    
	    bucket_dst_uri = boto.storage_uri(
	        self.TENSORFLOW_BUCKET + '/' + self.data_dir + '/' +filename, self.GOOGLE_STORAGE)
	    
	    dst_uri = bucket_dst_uri
	    object_contents.seek(0)
	    dst_uri.new_key().set_contents_from_file(object_contents)
	    
	    x_text = object_contents.getvalue()
	    return x_text
	

