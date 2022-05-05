import os.path
import shutil

from jinja2 import Environment, PackageLoader

from pkg_resources import resource_filename, resource_listdir


class Report:

    """Base class for HTML reports.

    Subclasses should implement the `generate` method, used to
    generate and output the report into the supplied directory. The
    calling code is responsible for ensuring that the directory exists
    and is writable.

    The intention is that the same Report object can be used to
    produce multiple reports in a given context, such as a single
    corpus. The contextual data should be supplied to the `__init__`
    method, and the data for a single specific report passed to the
    `generate` method.

    """

    _package_name = 'tacl'
    _report_name = ''

    def _copy_static_assets(self, output_dir):
        """Copy assets for the report to `output_dir`.

        :param output_dir: directory to output assets to
        :type output_dir: `str`

        """
        base_directory = 'assets/{}'.format(self._report_name)
        for asset in resource_listdir(self._package_name, base_directory):
            filename = resource_filename(
                self._package_name, '{}/{}'.format(base_directory, asset))
            shutil.copy2(filename, output_dir)

    def generate(self, output_dir):
        """Generate the report, writing it to `output_dir`."""
        raise NotImplementedError

    def _get_template(self):
        """Returns a template for this report.

        :rtype: `jinja2.Template`

        """
        loader = PackageLoader(self._package_name, 'assets/templates')
        env = Environment(loader=loader)
        return env.get_template('{}.html'.format(self._report_name))

    def _write(self, context, report_dir, report_name, assets_dir=None,
               template=None):
        """Writes the data in `context` in the report's template to
        `report_name` in `report_dir`.

        If `assets_dir` is supplied, copies all assets for this report
        to the specified directory.

        If `template` is supplied, uses that template instead of
        automatically finding it. This is useful if a single report
        generates multiple files using the same template.

        :param context: context data to render within the template
        :type context: `dict`
        :param report_dir: directory to write the report to
        :type report_dir: `str`
        :param report_name: name of file to write the report to
        :type report_name: `str`
        :param assets_dir: optional directory to output report assets to
        :type assets_dir: `str`
        :param template: template to render and output
        :type template: `jinja2.Template`

        """
        if template is None:
            template = self._get_template()
        report = template.render(context)
        output_file = os.path.join(report_dir, report_name)
        with open(output_file, 'w', encoding='utf-8') as fh:
            fh.write(report)
        if assets_dir:
            self._copy_static_assets(assets_dir)
