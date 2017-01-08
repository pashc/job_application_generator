import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

APPLICATIONS_DIR = './applications'
BIN_DIR = './bin'
CERTIFICATES_DIR = './certificates'
CV_DIR = './cv'


def run():
    dirs = _get_company_dirs()
    personal_json = _load_json_from(APPLICATIONS_DIR)
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
    address_json = _load_json_from(cur_dir)
    return template \
        .replace('{{COMPANY_NAME}}', address_json['company']) \
        .replace('{{COMPANY_STREET}}', address_json['street']) \
        .replace('{{COMPANY_ZIP}}', address_json['zip']) \
        .replace('{{COMPANY_CITY}}', address_json['city'])


def _format_application_text(cur_dir, template):
    application_text = _read_from_specific_file(cur_dir, 'txt')
    return template.replace('{{APPLICATION_TEXT}}', application_text)


def _format_certificates(template):
    cert_pdfs = _get_and_check_specific_files(Path(CERTIFICATES_DIR), 'pdf')
    cert_formats = ['\\includepdf[]{{{}}}\n'.format(str(pdf)) for pdf in cert_pdfs]
    return template.replace('{{CERTIFICATES}}', ''.join(cert_formats))


def _format_cv(template):
    cv_pdf = _get_and_check_specific_file(Path(CV_DIR), 'cv.pdf')
    if cv_pdf is not None:
        return template.replace('{{CV}}', '\\includepdf[]{{{}}}'.format(str(cv_pdf)))
    else:
        return template.replace('{{CV}}', '')


def _format_personal_data(personal_json, template):
    return template \
        .replace('{{FIRSTNAME}}', personal_json['firstname']) \
        .replace('{{LASTNAME}}', personal_json['lastname']) \
        .replace('{{STREET}}', personal_json['street']) \
        .replace('{{ZIP}}', personal_json['zip']) \
        .replace('{{CITY}}', personal_json['city']) \
        .replace('{{PHONE_NUMBER}}', personal_json['phone_number']) \
        .replace('{{E_MAIL}}', personal_json['e_mail'])


def _format_signature(template):
    signature_png = _get_specific_file(Path(BIN_DIR), 'png')
    return template.replace('{SIGNATURE}', str(signature_png))


def _format_template(cur_dir, personal_json, template):
    cur_template = _format_personal_data(personal_json, template)
    cur_template = _format_address(cur_dir, cur_template)
    cur_template = _format_application_text(cur_dir, cur_template)
    cur_template = _format_signature(cur_template)
    cur_template = _format_cv(cur_template)
    cur_template = _format_certificates(cur_template)
    return cur_template


def _get_and_check_specific_file(cur_dir, file_name):
    if (cur_dir / file_name).exists():
        return _get_specific_file(cur_dir, file_name)
    else:
        return None


def _get_and_check_specific_files(cur_dir, file_name):
    return [x for x in cur_dir.iterdir() if x.name.endswith(file_name)]


def _get_company_dirs():
    app_dir = Path(APPLICATIONS_DIR)
    return [x for x in app_dir.iterdir() if x.is_dir()]


def _get_specific_file(cur_dir, file_name):
    return _get_and_check_specific_files(cur_dir, file_name)[0]


def _load_json_from(cur_dir):
    return json.loads(_read_from_specific_file(cur_dir, 'json'))


def _process_dirs(dirs, personal_json, template):
    print('processing {} companies...'.format(len(dirs)))
    for cur_dir in dirs:
        cur_template = _format_template(cur_dir, personal_json, template)

        app_tex = cur_dir / 'app.tex'
        _write_template(app_tex, cur_template)
        _create_pdf(app_tex, cur_dir)

    print('finished')


def _read_from_specific_file(cur_dir, file_name):
    path = Path(cur_dir)
    specific_file = _get_specific_file(path, file_name)
    with specific_file.open() as file:
        return file.read()


def _write_template(app_tex, cur_template):
    if not app_tex.exists():
        app_tex.touch()
    with app_tex.open('w') as file:
        file.write(cur_template)


if __name__ == '__main__':
    run()
