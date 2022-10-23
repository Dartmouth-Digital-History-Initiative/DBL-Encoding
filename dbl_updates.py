import csv
import sys
import xml.etree.ElementTree as ET
from io import StringIO
from pathlib import Path
import html


# Function which takes the tsv and xml files and 
# Uses tsv data to add dbl_ids to the standoff markup 
def dbl_updates(tsv, xml, namespaces):
    proj_ids = {} 
    tsv_data = [] 
    with open(tsv) as file:
        # read the tsv file
        t = csv.reader(file, delimiter="\t")
        for line in t:
            tsv_data.append(line)
        try:
            # get each dbl_id from the tsv and map it to the 
            # dbl interview instance 
            # ie. dbl_001_person_01 : dbl_902
            dbl_header = tsv_data[0].index('dbl_id')
            tsv_type = tsv_data[1][0].split('_')
            data_type = tsv_type[2]
            data_type = data_type.capitalize()
            for i in range(1, len(tsv_data)):
                if tsv_data[i][dbl_header] != '':
                    proj_ids[tsv_data[i][0]] = tsv_data[i][dbl_header]
        except:
            print("Error: No dbl_id header found")

    standoff_list = 'list' + data_type

    for s in xml.findall('ns0:standOff', namespaces):
        sub = s

    for s in sub.findall('ns0:'+standoff_list, namespaces):
        l = s

    for person in l.findall('ns0:'+tsv_type[2], namespaces):
        # Gets the dbl interview id of the entities
        dblId = person.attrib.values()
        dblId = list(dblId)
        dblId = dblId[0]
        # Checks if the interview id maps to a project id from the tsv 
        if dblId in proj_ids:
            id = ET.SubElement(person,'ns0:idno')
            id.text = proj_ids[dblId]
            id.set('type', 'project')
            #ET.indent(id)
           
# Takes an xml document formatted as a string and returns it's namespaces
def get_namespaces(xml_string):
    namespaces = dict([node for _, node in ET.iterparse(StringIO(xml_string), events=['start-ns'])])
    namespaces["ns0"] = namespaces[""]
    return namespaces

# updates standoff with dbl_ids
# to run: python3 dbl_updates.py <tsv file path> <narrator_updates.xml file path>
if __name__ == "__main__":
    output = 'updated.xml'

    tsv_name = sys.argv[1]
    if tsv_name == '-h':
        print('This is a tool to add dbl_ids from a tsv into an existing standOff markup of an xml file.')
        print('To run the tool:\n \tpython3 dbl_updates.py <tsv file path> <narrator_updates.xml file path>')
    else: 
        xml_name = sys.argv[2]
        
        # reads xml into a string so that StringIO can find namespaces
        xml_string = ""
        with open(xml_name) as file:
            t = file.readlines()
            for line in t:
                xml_string += line
        
        namespaces = get_namespaces(xml_string)

        # Using ElementTree python library to manipulate xml file
        tree = ET.parse(xml_name)
        root = tree.getroot()
        dbl_updates(tsv_name, root, namespaces)

        # Setting the updated xml file name
        narrator = xml_name.split('.')
        output = narrator[0]
        tree.write(output)
        
        # Removing the default namespace string from the xml output 
        # then creating the final output file
        xml_string = ""
        with open(output) as file:
            t = file.readlines()
            for line in t:
                xml_string += line

        txt = xml_string.replace("ns0:", "")
        text_file = open(output, "w")
        text_file.write(html.unescape(txt))
        text_file.close()

        p = Path(output)
        p.rename(p.with_suffix('.xml'))
        

