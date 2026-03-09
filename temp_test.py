from skyrim_ini_editor import INIFile
ini=INIFile('sample_skyrim.ini','test')
# modify a property
for entry in ini.sections['Display']:
    if entry.get('type')=='property' and entry['key']=='bFull Screen':
        entry['value']='true'
        ini.modified=True
        break
ini.save()
print(open('sample_skyrim.ini').read())
