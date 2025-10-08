sections_in_model = ['UC 305x305x158', 'UB 254x146x37', 'IPE 200', 'EA 70x70x7', 'EA 80x80x8', 'CFC 150x65x20x3.0']
classifications_in_model = []
section_list = []

for section in sections_in_model:
    components = section.split(' ')
    if len(components) > 2:
        classifications_in_model.append(components[0]+' '+components[1])
    else:
        classifications_in_model.append(components[0])

for classification in classifications_in_model:
    match classification:
        case 'UB':
            section_list.append('I-Sections')
        case 'IPE':
            section_list.append('I-Sections')
        case 'UC':
            section_list.append('H-Sections')
        case 'CHS':
            section_list.append('CHS')
        case 'EA':
            section_list.append('Equal Angles')
        case other:
            section_list.append('Not-optimisable')

print(section_list)