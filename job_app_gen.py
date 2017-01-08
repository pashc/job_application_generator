import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

APPLICATIONS_DIR = './applications'


def run():
    dirs = _get_company_dirs()
    personal_json = _get_json_from(APPLICATIONS_DIR)
    template = _read_from_specific_file(APPLICATIONS_DIR, 'tex')

    _process_dirs(dirs, personal_json, template)


def _cleanup(output_path):
    files_to_remove = ['.aux', '.log', '.out']
    for file in output_path.iterdir():
        if str(file)[-4:] in files_to_remove:
            os.remove(str(file))


def _create_pdf(app_tex, output_dir):
    pdflatex = shutil.which('pdflatex')
    if not pdflatex:
        print('pdflatex is not installed')
        sys.exit('Abort')

    subprocess.run([pdflatex, '-output-dir=' + str(output_dir), '-jobname=job_application', str(app_tex.absolute())],
                   stdout=subprocess.DEVNULL)
    _cleanup(output_dir)


def _format_address(cur_dir, template):
    address_json = _get_json_from(cur_dir)
    return template \
        .replace('{{COMPANY_NAME}}', address_json['company']) \
        .replace('{{COMPANY_STREET}}', address_json['street']) \
        .replace('{{COMPANY_ZIP}}', address_json['zip']) \
        .replace('{{COMPANY_CITY}}', address_json['city'])


def _format_application_text(cur_dir, template):
    application_text = _read_from_specific_file(cur_dir, 'txt')
    return template.replace('{{APPLICATION_TEXT}}', application_text)


def _format_personal_data(personal_json, template):
    return template \
        .replace('{{FIRSTNAME}}', personal_json['firstname']) \
        .replace('{{LASTNAME}}', personal_json['lastname']) \
        .replace('{{STREET}}', personal_json['street']) \
        .replace('{{ZIP}}', personal_json['zip']) \
        .replace('{{CITY}}', personal_json['city']) \
        .replace('{{PHONE_NUMBER}}', personal_json['phone_number']) \
        .replace('{{E_MAIL}}', personal_json['e_mail'])


def _get_company_dirs():
    app_dir = Path(APPLICATIONS_DIR)
    return [x for x in app_dir.iterdir() if x.is_dir()]


def _get_json_from(cur_dir):
    return json.loads(_read_from_specific_file(cur_dir, 'json'))


def _process_dirs(dirs, personal_json, template):
    print('processing {} companies...'.format(len(dirs)))
    for cur_dir in dirs:
        cur_template = _format_template(cur_dir, personal_json, template)

        app_tex = cur_dir / 'app.tex'
        _write_template(app_tex, cur_template)
        _create_pdf(app_tex, cur_dir)

    print('finished')


def _format_template(cur_dir, personal_json, template):
    cur_template = _format_personal_data(personal_json, template)
    cur_template = _format_address(cur_dir, cur_template)
    cur_template = _format_application_text(cur_dir, cur_template)
    return cur_template


def _read_from_specific_file(cur_dir, file_name):
    path = Path(cur_dir)
    specific_file = [x for x in path.iterdir() if x.is_file() and x.name.endswith(file_name)][0]
    with specific_file.open() as file:
        return file.read()


def _write_template(app_tex, cur_template):
    if not app_tex.exists():
        app_tex.touch()
    with app_tex.open('w') as file:
        file.write(cur_template)


if __name__ == '__main__':
    run()
