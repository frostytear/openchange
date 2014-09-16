#!/usr/bin/python

import optparse
import os,sys

from openchange import mapistore

def print_tree(folder, indent):
    print '   '*indent + '[F]: ' + folder.get_properties(['PidTagDisplayName'])['PidTagDisplayName']
    for f in folder.get_child_folders():
        print_tree(f, indent+1)
        
parser = optparse.OptionParser(usage="%prog --username=<username> [options]", version="%prog 1.0")
parser.add_option("--username", type="string", help="Set the username to use with mapistore")
parser.add_option("--mapping-path", type="string", help="Specify mapistore mapping path")
parser.add_option("--openchangedb", type="string", help="Specify openchangedb URL")

group = optparse.OptionGroup(parser, "Debug Options")
group.add_option("-d", "--debuglevel", type="int", dest="debuglevel", default=0)
parser.add_option_group(group)

opts,args = parser.parse_args()

if not opts.username:
    print "[ERR] --username option required"
    parser.print_help()
    sys.exit(1)

if opts.mapping_path:
    mapistore.set_mapping_path(opts.mapping_path)

# Create MAPIStore Object
mstore = mapistore.MAPIStore()

# Change log_level
if opts.debuglevel is not None:
    mstore.debuglevel = opts.debuglevel

if opts.openchangedb is not None:
    mstore.set_parm("mapiproxy:openchangedb", opts.openchangedb)

# Display info
mstore.dump()

# Initialise MAPIStore
print "[PYMAPISTORE] Initialise MAPIStore for user " + opts.username
mstore.initialize(opts.username)
print

# List backends
print '[PYMAPISTORE] List backends:'
backends = mstore.list_backends()
for i in backends:
	print i
print

# Get available contexts 
print '[PYMAPISTORE] List subfolders and messages for each context:'
 
cap_list = mstore.capabilities()
  
# Iterate over the available contexts and open root folder, subfolders and messages
for cap in cap_list:
	name = cap['name']
	if name:
		print '[CONTEXT]: ' + name
 	
	uri = cap['url']
	try:
		ctx = mstore.add_context(uri)
	except:
		print "[PYMAPISTORE][ERR]: '" + name + "' couldn't be opened"
		print
		continue
 
	root_fld = ctx.open()
 	
	subfld_count = root_fld.get_child_count(mapistore.FOLDER_TABLE) 
	print '[NUMBER OF SUBFOLDERS]: ' + repr(subfld_count)
	if subfld_count > 0:
		for fld in root_fld.get_child_folders():
			print '[SUBFOLDER]: ' + fld.get_uri()
	msg_count = root_fld.get_child_count(mapistore.MESSAGE_TABLE)
	print '[NUMBER OF MESSAGES]: ' + repr(msg_count)
	if msg_count > 0:
		for msg in root_fld.get_child_messages():
			print '[MESSAGE]: ' + msg.get_uri()
	print

# Create, move and delete subfolders
# *PARTICULAR TO MY ENVIRONMENT*
print '[PYMAPISTORE] Add INBOX context:'
in_ctx = mstore.add_context('sogo://user1:user1@mail/folderINBOX')
print

print '[PYMAPISTORE] Open INBOX root folder:'
in_fld = in_ctx.open()
print

print '[PYMAPISTORE] Open BLAH folder:'
blah_fld = in_fld.open_folder('sogo://user1:user1@mail/folderINBOX/foldersampleblah/')
print

print '[PYMAPISTORE] Create FOO subfolder:'
foo_fld = in_fld.create_folder('FOO')
print

# Display the hierarchy
print "[PYMAPISTORE] INBOX hierarchy:"
print_tree(in_fld, 0)
print

# Display and modify folder properties
print '[PYMAPISTORE] Get FOO properties:'
print foo_fld.get_properties();
print

print "[PYMAPISTORE] Set FOO 'PidTagContentCount' property:"
print foo_fld.get_properties(['PidTagContentCount']);

foo_fld.set_properties({'PidTagContentCount': 2L});

print foo_fld.get_properties(['PidTagContentCount']);

# Set back to original value
foo_fld.set_properties({'PidTagContentCount': 0L});
print

### Copy folder ###
print '[PYMAPISTORE] Duplicate BLAH (copy into FOO):'
try:
    blah_fld.copy_folder(foo_fld, 'BLAHC', mapistore.NON_RECURSIVE)
except:
    print "[PYMAPISTORE][ERR] Can't copy folder"
    print sys.exc_info()[0]
    print
   
print "[PYMAPISTORE] INBOX hierarchy:"
print_tree(in_fld, 0)
print

# Move folder
print '[PYMAPISTORE] Move FOO subfolder to BLAH as FOOM:'

try:
	foo_fld.move_folder(blah_fld, 'FOOM')
except:
	print "[PYMAPISTORE][ERR] Can't move folder"
	print sys.exc_info()[0]
	print

	print '[PYMAPISTORE][ERR] Delete FOO folder:'
	foo_fld.delete(mapistore.DEL_ALL)
	print
 
print "[PYMAPISTORE] INBOX hierarchy:"
print_tree(in_fld, 0)
print

print '[PYMAPISTORE] Display FOOM properties:'
foom_fld = blah_fld.open_folder('sogo://user1:user1@mail/folderINBOX/foldersampleblah/folderFOOM/')
print foom_fld.get_properties();
print

# Copy folder
print '[PYMAPISTORE] Copy FOOM into INBOX as FOOC:'
try:
	foom_fld.copy_folder(in_fld, 'FOOC', mapistore.RECURSIVE)
except:
	print "[PYMAPISTORE][ERR] Can't copy folder"
	print sys.exc_info()[0]
	print
   
print "[PYMAPISTORE] INBOX hierarchy:"
print_tree(in_fld, 0)
print

print '[PYMAPISTORE] Display FOOC properties:'
fooc_fld = in_fld.open_folder('sogo://user1:user1@mail/folderINBOX/folderFOOC/')
print fooc_fld.get_properties();
print

# Create message
print '[PYMAPISTORE] Create FOO message in BLAH:'
foo_msg = blah_fld.create_message(mapistore.CREATE_GENERIC)
uri = foo_msg.get_uri()
print '[PYMAPISTORE] URI: ' + uri
print
  
# Check that it appears
print '[PYMAPISTORE] INBOX hierarchy:'
print '[NUMBER OF MESSAGES]: ' + repr(blah_fld.get_child_count(mapistore.MESSAGE_TABLE))
print

# Clean up
print '[PYMAPISTORE] Delete FOOC folder:'
fooc_fld.delete(mapistore.DEL_ALL)
print

print '[PYMAPISTORE] Delete FOOM folder:'
try:
    foom_fld.delete(mapistore.DEL_ALL)
except:
    print '[PYMAPISTORE][ERR] Cannot delete FOOM folder. Use stubbornness'
    foom_fld.delete(mapistore.DEL_ALL)
print

print '[PYMAPISTORE] Delete FOO message:'
blah_fld.delete_message(uri, mapistore.PERMANENT_DELETE)
print

print "[PYMAPISTORE] INBOX hierarchy:"
print_tree(in_fld, 0)
print

# Test move and copy messages
# *PARTICULAR TO MY ENVIRONMENT*
print '[PYMAPISTORE] Add Sent context:'
sent_ctx = mstore.add_context('sogo://user1:user1@mail/folderSent')
print

print '[PYMAPISTORE] Open Sent root folder:'
sent_fld = sent_ctx.open()
print

print '[PYMAPISTORE] Sent child messages:'
uri_list = []
for m in sent_fld.get_child_messages():
    uri = m.get_uri()
    uri_list.append(uri)
    print uri
print

print '[PYMAPISTORE] Copy child messages to INBOX:'
sent_fld.copy_messages(uri_list, in_fld)
print

print '[PYMAPISTORE] INBOX child messages:'
uri_list = []
for m in in_fld.get_child_messages():
    uri = m.get_uri()
    uri_list.append(uri)
    print uri
print

print '[PYMAPISTORE] Move child messages into BLAH:'
in_fld.move_messages(uri_list, blah_fld)
print

print '[PYMAPISTORE] INBOX child messages:'
for m in in_fld.get_child_messages():
    print m.get_uri()
print

print '[PYMAPISTORE] BLAH child messages (delete them once shown):'
for m in blah_fld.get_child_messages():
    uri = m.get_uri()
    print uri
    blah_fld.delete_message(uri, mapistore.PERMANENT_DELETE)
print
