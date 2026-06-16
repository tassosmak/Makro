from Makro.MakroCore import flags

def gen_file(filename=str):
    with open(f'{flags.base_folder}/../Plugins/{filename}.json', 'w+') as recover:
        recover.write('''{
        "premisions": {
            "Filesystem": false,
            "Notifications": false,
            "Personal_data": false
        }
    }''')