
# coding: utf-8

# # Data Wrangling using Python and MongoDB
# 
# ###### by Prasad Pagade 
# 
# 
# ## Project Details (Wrangle OpenStreetMap Data):
# 
# 1. Location: Santa Clara, CA, USA
# 
# 2. Reason for choosing the location: I live in the **Bay Area** and I am very passionate about the city **Santa Clara** in which I reside. The Santa Clara OSM file was 58MB which met the minimum file size of 50MB. Hence, I chose the Santa Clara dataset from MapZen.
# 
# 3. Dataset: [Santa Clara, CA](https://1drv.ms/u/s!Alalhc0dZibggwbIg32Q8crZoDmr)
# 
# ### Objective
# You will choose any area of the world in https://www.openstreetmap.org and use data munging techniques, such as assessing the quality of the data for validity, accuracy, completeness, consistency and uniformity, to clean the OpenStreetMap data for a part of the world that you care about. Finally, you will choose either MongoDB or SQL as the data schema to complete your project.
# 
# #### References:
# 1. Udacity "Data Wrangling with MongoDB" - Lesson 6
# 
# 2. [MongoDB documentation](https://docs.mongodb.com/manual/tutorial/install-mongodb-enterprise-on-windows/?_ga=1.121437642.337829721.1481582931)
# 
# 
# #### Table of content:
# 
# 1. Data Audit
# 2. Problem encountered
# 3. Data Cleaning
# 4. Insights through MongoDB
# 5. Conclusion

# ##  1. Data Audit

# In[27]:

# Import all the libraries

import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
import collections
import pymongo
from pymongo import MongoClient


# In[28]:

import os
"""
datadir = "data"
datafile = "San_Jose_city.osm"
sj_data = os.path.join(datadir, datafile)
#sj_data.replace("\\","\")
sj_data1 = "San_Jose_city.osm"
"""
## test Santa Clara data
sc_data = "SantaClara_county.osm"


# In[29]:

sc_data


# In[30]:

os.path.exists(sc_data)


# In[31]:

# now lets parse through the OSM file using an element tree parser and explore the tags on a highlevel.

# We use the count_tags method used in the exercise in Lesson 6 - MongoDB

def count_tags(filename):
    tags = {}
    print filename
    for event,elem in ET.iterparse(filename):
        if elem.tag in tags:
            tags[elem.tag] += 1
        else:
            tags[elem.tag] = 1
    return tags


# In[32]:

sc_tags = count_tags(sc_data)
sc_tags


# In[33]:

print 'The original OSM file is {} MB'.format(os.path.getsize(sc_data)/1.0e6)


# In[34]:

# Print a sample of the file. Here I am printing the first 100 elements

OSM_FILE = sc_data  # Replace this with your osm file
SAMPLE_FILE = "sample.osm"

k = 100 # Parameter: print the first k elements (or every kth element)

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


# print the first  k top level elements
for i, element in enumerate(get_element(OSM_FILE)):
    if i <= k:
        print ET.tostring(element)
'''
# or print every  kth top level elements
for i, element in enumerate(get_element(OSM_FILE)):
    if i % k == 0:
        print ET.tostring(element)
'''
# Also writing the sample file to view it in Sublime text
with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    # Write every kth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))

    output.write('</osm>')


# So, I wanted to oversee the structure of the OSM file. I sampled the first 100 elements and exported them to "SAMPLE_FILE.osm". Found out that the OSM file is structured into Nodes, Ways and Tags. 

# We want to explore the data a bit more.Before we process the data and add it into the database, we should check the
# "k" value for each **"tag"** and see if there are any potential problems.
# 
# The lesson from "Case Study" provided us with 3 regular expressions to check for certain patterns in the tags. We would like to change the data model and expand the "addr:street" type of keys to a dictionary like this:
# {"address": {"street": "Some value"}}
# 
# So, we have to see if we have such tags, and if we have any tags with
# problematic characters.
# 
# The function 'key_type', such that we have a count of each of four tag categories in a dictionary:
# 
# 1.  "lower", for tags that contain only lowercase letters and are valid,
# 2.  "lower_colon", for otherwise valid tags with a colon in their names,
# 3.  "problemchars", for tags with problematic characters, and
# 4.  "other", for other tags that do not fall into the other three categories.
# 

# In[35]:

import re

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def key_type(element, keys):
    if element.tag == 'tag':
        for val in element.iter('tag'):
            k = element.get('k')
            #search for the "lower"
            if lower.search(k):
                keys['lower'] += 1
            elif lower_colon.search(k):
                keys['lower_colon'] += 1
            elif problemchars.search(k):
                keys['problemchars'] += 1
            else:
                keys['other'] += 1
    return keys

def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys
            


# In[36]:

sc_tag_category = process_map(sc_data)

pprint.pprint(sc_tag_category)


# Now, let us explore the users

# In[37]:

# this function will tell us how many unique users have already contributed to the map data

def get_user(element):
    if element.get('uid'):
        uid = element.attrib['uid']
        return uid
    else:
        return None
    
    

def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if get_user(element):
            users.add(get_user(element))

    return users

sc_users = process_map(sc_data)
len(sc_users)


# So **547** users have contributed to the map data. That's way less than what I had expected.

# # 2. Problem encountered

# Next we audit the street names to see if they are in their expected format. If not, then we may have to map a way to rename the street names to its expected values.

# ## 2.1 Street Names

# In[38]:

from collections import defaultdict

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected = ["Avenue", "Boulevard", "Commons", "Court", "Drive", "Lane", "Parkway", 
                         "Place", "Road", "Square", "Street", "Trail"]
# we will be updating the mapping dictionary from the audit iterations
mapping = {'Ave'  : 'Avenue',
           'Blvd' : 'Boulevard',
           'Dr'   : 'Drive',
           'Ln'   : 'Lane',
           'Pkwy' : 'Parkway',
           'Rd'   : 'Road',
           'Rd.'   : 'Road',
           'St'   : 'Street',
           'street' :"Street",
           'Ct'   : "Court",
           'Cir'  : "Circle",
           'Cr'   : "Court",
           'ave'  : 'Avenue',
           'Hwg'  : 'Highway',
           'Hwy'  : 'Highway',
           'Sq'   : "Square"}



# **This menthod below audits for the street type names and updates any abbreviation which may not represent the standard ones for naming the streets**

# In[39]:

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])

    return street_types


# In[40]:

sc_street_types = audit(sc_data)


# In[41]:

pprint.pprint(dict(sc_street_types))


# That's a lot less abbreviations than I was expecting to come up. It looks like the data is already cleaned up. None the less I found some abbr. like Rd,ave, St which we would update using the funtion below. We also update the **mapping{}** above looking at the result from street_types

# In[42]:

# Updating the street names. This last function update_name is the last step of the process, which take the old name and update them with a better name

def update_street_name(name, mapping):

    m = street_type_re.search(name)
    # print "m.group:" + m.group()
    better_name = name
    
    if m:
        if m.group() in mapping.keys():
            better_street_type = mapping[m.group()]
            better_name = street_type_re.sub(better_street_type,name)
            
    return better_name

print '**************************BETTER NAMES**************************'
for street_type, ways in sc_street_types.iteritems():
    for name in ways:
        better_name = update_street_name(name, mapping)
        print name, "=>", better_name



# ## Zip Codes

# We use similar technique above to clean any unconventional zipcodes found in our Santa Clara data

# In[43]:

from collections import defaultdict

def audit_zipcode(invalid_zipcode,zipcode):
    twoDigits = zipcode[0:2]
    if not twoDigits.isdigit():
        invalid_zipcode[twoDigits].add(zipcode)
    
    elif twoDigits != 95:
        invalid_zipcode[twoDigits].add(zipcode)
        
def is_zipcode(elem):
    return (elem.attrib['k'] == "addr:postcode")

def audit_zip(osmfile):
    osm_file = open(osmfile, "r")
    invalid_zipcodes = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_zipcode(tag):
                    audit_zipcode(invalid_zipcodes,tag.attrib['v'])

    return invalid_zipcodes


# In[44]:

sc_zipcodes = audit_zip(sc_data)

pprint.pprint(dict(sc_zipcodes))


# majority of the data looks clean. The clean zip code is summarised below. There are the format of 5 digits, 4 digits and 5 digits - 5 digits which are valid and need no formatting.

# In[45]:

def update_name(zipcode):
    testNum = re.findall('[a-zA-Z]*', zipcode)
    if testNum:
        testNum = testNum[0]
    testNum.strip()
    if testNum == "CA":
        convertedZipcode = (re.findall(r'\d+', zipcode))
        if convertedZipcode:
            if convertedZipcode.__len__() == 2:
                return (re.findall(r'\d+', zipcode))[0] + "-" +(re.findall(r'\d+', zipcode))[1]
            else:
                return (re.findall(r'\d+', zipcode))[0]

for street_type, ways in sc_zipcodes.iteritems():
    for name in ways:
        better_name = update_name(name)
        print name, "=>", better_name


#  # 3. MongoDB

# In order to analyze our dataset in MongoDb we will need to convert the XML  to JSON. We will use the following set of rules learnt from the Case Study of the lectures:
# - you should process only 2 types of top level tags: "node" and "way"
# - all attributes of "node" and "way" should be turned into regular key/value pairs, except:
#     - attributes in the CREATED array should be added under a key "created"
#     - attributes for latitude and longitude should be added to a "pos" array,
#       for use in geospacial indexing. Make sure the values inside "pos" array are floats
#       and not strings. 
# - if the second level tag "k" value contains problematic characters, it should be ignored
# - if the second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
# - if the second level tag "k" value does not start with "addr:", but contains ":", you can
#   process it in a way that you feel is best. For example, you might split it into a two-level
#   dictionary like with "addr:", or otherwise convert the ":" to create a valid key.
# - if there is a second ":" that separates the type/direction of a street,
#   the tag should be ignored

# In[46]:

# Preparing database for MongoDB
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
startswith_addr = re.compile(r'addr:')
startswith_street = re.compile(r'^street')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
POS = ["lon", "lat"]

def shape_element(element):
    node = {}
        
    if element.tag == "node" or element.tag == "way" :
        # YOUR CODE HERE
        node['type'] = element.tag
        # initialize empty address
        address = {}
        # parsing through attributes
        for a in element.attrib:
            if a in CREATED:
                if 'created' not in node:
                    node['created'] = {}
                    node['created'][a] = element.get(a)
                elif a in ['lat','lon']:
                    continue
                else:
                    node[a] = element.get(a)
        #population
        if 'lat' in element.attrib and 'lon' in element.attrib:
            node['pos'] = [float(element.get('lat')), float(element.get('lon'))]
        
        #Parse 2nd- level tags
        for e in element:
            # parse second-level tags for ways and populate `node_refs`
            if e.tag == 'nd':
                if 'node_refs' not in node:
                    node['node_refs'] = []
                if 'ref' in e.attrib:
                    node['node_refs'].append(e.get('ref'))

            # throw out not-tag elements and elements without `k` or `v`
            if e.tag != 'tag' or 'k' not in e.attrib or 'v' not in e.attrib:
                continue
            key = e.get('k')
            val = e.get('v')

            # skip problematic characters
            if problemchars.search(key):
                continue

            # parse address k-v pairs
            elif startswith_addr.search(key):
                key = key.replace('addr:', '')
                address[key] = update_street_name(val, mapping)

            # catch-all
            else:
                node[key] = val
        # compile address
        if len(address) > 0:
            node['address'] = {}
            street_full = None
            street_dict = {}
            street_format = ['prefix', 'name', 'type']
            # parse through address objects
            for key in address:
                val = address[key]
                if startswith_street.search(key):
                    if key == 'street':                  
                        street_full = val
                    elif 'street:' in key:
                        street_dict[key.replace('street:', '')] = val
                else:
                    node['address'][key] = val
            # assign street_full or fallback to compile street dict
            if street_full:
                node['address']['street'] = street_full
            elif len(street_dict) > 0:
                node['address']['street'] = ' '.join([street_dict[key] for key in street_format])
        return node
    else:
        return None
   
 


# In[47]:

def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data



# In[48]:

process_map(sc_data)


# In[49]:

data = process_map(sc_data)


# In[51]:

client = MongoClient()
db = client.SantaClaraOSM
collection = db.santaclaraMAP
collection.insert(data)


# In[52]:

collection


# **File Sizes**

# In[53]:

import os
print 'The original OSM file is {} MB'.format(os.path.getsize(sc_data)/1.0e6) # convert from bytes to megabytes
print 'The JSON file is {} MB'.format(os.path.getsize(sc_data + ".json")/1.0e6) # convert from bytes to megabytes


# # 4. insights through MongoDB

# **Number of documents**

# In[54]:

collection.find().count()


# ** Number of Unique Users **

# In[55]:

# Number of unique users
len(collection.distinct('user'))


# **Number of nodes**

# In[56]:

# Number of nodes
collection.find({"type":"node"}).count()


# **Number of ways**

# In[57]:

# Number of ways
collection.find({"type":"way"}).count()


# ** Top 5 contributers **

# In[58]:

result = collection.aggregate( [     { "$group" : {"_id" : "$user", 
                                        "count" : { "$sum" : 1} } },
                                        { "$sort" : {"count" : -1} }, 
                                        { "$limit" : 5 } ] )

print(list(result))


# ** Top 10 amenities in Santa Clara **

# In[59]:

amenity = collection.aggregate([{'$match': {'amenity': {'$exists': 1}}},                                 {'$group': {'_id': '$amenity',                                             'count': {'$sum': 1}}},                                 {'$sort': {'count': -1}},                                 {'$limit': 10}])
print(list(amenity))


# ** Top 10 cuisines in Santa Clara**

# In[60]:

cuisine = collection.aggregate([{"$match":{"amenity":{"$exists":1},
                                 "amenity":"restaurant",}},      
                      {"$group":{"_id":{"Food":"$cuisine"},
                                 "count":{"$sum":1}}},
                      {"$project":{"_id":0,
                                  "Food":"$_id.Food",
                                  "Count":"$count"}},
                      {"$sort":{"Count":-1}}, 
                      {"$limit":10}])
print(list(cuisine))


# ** Universities in Santa Clara **

# In[61]:

universities = collection.aggregate([{"$match":{"amenity":{"$exists":1}, "amenity": "university", "name":{"$exists":1}}},
                                    {"$group":{"_id":"$name", "count":{"$sum":1}}},
                                    {"$sort":{"count":-1}}])

print(list(universities))


# # 5. Conclusion #

# ## Summary statistics##
# 
# - size of the file --> The original OSM file is **58.944542 MB** --> The JSON file is **61.66255 MB  **
# 
# - number of unique users --> **534**
# 
# - number of nodes and ways --> nodes: **263052**   ways: **39339**
# 

# ## Ideas to improve the data ##
# 
# I found that the Santa Clara OSM data was fairly clean. There are 534 unique users contributing to the data. Every person has their own way of addressing street names. We can eliminate these types of human errors by keeping a data entry form which has pre-defined naming conventions.
# Also, this dataset can be better understood by visualizations using a visualization tool like Tableau. This would helps us compare different nodes in the data visually.
# 
# - Cost of implementation:
# We need a team and structure that can maintain the above suggestions. Once the data entry form is set up, only minimal supervision would be required to make any changes periodically.
# 
# 
# 

# In[ ]:



