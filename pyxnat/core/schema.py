from lxml import etree

# REST collection resources tree
resources_tree = {'projects':['experiments', 'subjects', 'resources'],
            'subjects':['experiments', 'resources'],
            'experiments':['assessors', 'reconstructions', 'scans', 
                           'resources'],
            'assessors':['resources', 'in_resources','out_resources'],
            'reconstructions':['in_resources','out_resources'],
            'scans':['resources'],
            'resources':['files'],
            'files':[],
            'in_resources':['files'],
            'in_files':[],
            'out_resources':['files'],
            'out_files':[],
            }

# REST resources that are not natively supported
extra_resources_tree = {'projects':['assessors', 'scans', 'reconstructions'],
            'subjects':['assessors', 'scans', 'reconstructions'],
            }

# REST <Python to URI> translation table 
rest_translation = {'in_resources':'in/resources',
                    'in_files':'in/files',
                    'out_resources':'out/resources',
                    'out_files':'out/files',
                    'in_resource':'in/resource',
                    'in_file':'in/file',
                    'out_resource':'out/resource',
                    'out_file':'out/file',
                    }

# REST json format <id_header, label_header>
json = {'projects':['ID', 'ID'],
        'subjects':['ID', 'label'],
        'experiments':['ID', 'label'],
        'assessors':['ID', 'label'],
        'reconstructions':['ID', 'label'],
        'scans':['ID', 'label'],
        'resources':['xnat_abstractresource_id', 'label'],
        'out_resources':['xnat_abstractresource_id', 'label'],
        'in_resources':['xnat_abstractresource_id', 'label'],
        'files':['Name', 'Name'],
        }

resources_singular = [key.rsplit('s', 1)[0] for key in resources_tree.keys()]
resources_plural   = resources_tree.keys()
resources_types    = resources_singular + resources_plural

default_datatypes = {'projects':'xnat:projectData',
                     'subjects':'xnat:subjectData',
                     'experiments':'xnat:mrSessionData',
                     'assessors':'xnat:imageAssessorData',
                     'reconstructions':None,
                     'scans':'xnat:mrScanData',
                     'resources':None,
                     'in_resources':None,
                     'out_resources':None,
                     }

def datatype_attributes(root, datatype):
    def _iterchildren(node, pathsofar):
        elements = []

        for child in node.iterchildren():
            if isinstance(child.tag, (str, unicode)) \
                and child.tag.split('}')[1] == 'element':
                    elements.append('%s/%s'%(pathsofar, child.get('name')))
                    elements.extend(_iterchildren(child, '%s/%s'%
                                        (pathsofar, child.get('name')))
                                    )

            elif isinstance(child.tag, (str, unicode)) \
                and child.tag.split('}')[1] == 'attribute':
                    elements.append('%s/%s'%(pathsofar, child.get('name')))

            elif isinstance(child.tag, (str, unicode)) \
                and child.tag.split('}')[1] == 'extension':
                    ct_xpath = "/xs:schema/xs:complexType[@name='%s']"% \
                                                child.get('base').split(':')[1]
                    for complex_type in \
                        node.getroottree().xpath(ct_xpath, namespaces=child.nsmap):
                            same = False
                            for ancestor in child.iterancestors():
                                if ancestor.get('name') == child.get('base').split(':')[1]:
                                    same = True
                                    break
                            if not same:
                                elements.extend(_iterchildren(complex_type, pathsofar))

                    elements.extend(_iterchildren(child, pathsofar))            

            else:
                elements.extend(_iterchildren(child, pathsofar))

        return elements

    ct_xpath = "/xs:schema/xs:complexType[@name='%s']"%datatype.split(':')[1]
    attributes = []

    for complex_type in root.xpath(ct_xpath, namespaces=root.nsmap):
        for child in complex_type.iterchildren():                
            attributes.extend(_iterchildren(child, datatype))

    return attributes

def datatypes(root):
    return [element.get('type')
                for element in \
                    root.xpath('/xs:schema/xs:element', namespaces=root.nsmap)
            ]
