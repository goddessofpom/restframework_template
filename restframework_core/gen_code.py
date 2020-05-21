import sys
import re
from os import path


class CodeGenerator(object):
    def __init__(self, module_name, name, verbose_name=None):
        self.module_name = module_name
        self.name = name.capitalize()
        self.verbose_name = verbose_name
        self.parent_path = path.dirname(path.dirname(__file__))

    def _find_pos(self, target, content):
        tab=re.search(target, content)
        pos=tab.start()
        return pos
    
    @property
    def _lower_name(self):
        return self.name.lower()

    @property
    def url_template(self):
        lower = self._lower_name
        return f"""router.register(r'{lower}', {self.name}ViewSet, basename="{lower}")"""

    @property
    def viewset_template(self):
        return f"""class {self.name}ViewSet(CustomModelViewSet):
    serializer_class = {self.name}Serializer
    filter_class = {self.name}Filter
    queryset = {self.name}.objects.all()
        """

    @property
    def serializer_template(self):
        return f"""class {self.name}Serializer(serializers.ModelSerializer):
    class Meta:
        model = {self.name}
        exclude = ('updated', 'deleted')
        """

    @property
    def filter_template(self):
        return f"""class {self.name}Filter(FilterSet):
    class Meta:
        model = {self.name}
        fields = {{

        }}
        """

    def _write_urls(self):
        url_template = self.url_template
        url_path = path.join(self.parent_path, self.module_name, "urls.py")
        with open(url_path, 'r+') as f:
            content = str(f.read())
            pos = self._find_pos("urlpatterns", content)
            if pos == -1:
                raise Exception("urlpatterns not defined")
            
            f.seek(0)
            f.truncate()

        with open(url_path, 'a') as f:
            content = '\n' + content[:pos] + url_template + '\n' + content[pos:]
            f.write(content)

    def _write_viewset(self):
        viewset_template = self.viewset_template
        viewset_path = path.join(self.parent_path, self.module_name, "viewsets.py")

        with open(viewset_path, 'a') as f:
            content = '\n\n' + viewset_template
            f.write(content)

    def _write_serializer(self):
        serializer_template = self.serializer_template
        serializer_path = path.join(self.parent_path, self.module_name, "serializers.py")

        with open(serializer_path, 'a') as f:
            content = '\n\n' + serializer_template
            f.write(content)

    def _write_filter(self):
        filter_template = self.filter_template
        filter_path = path.join(self.parent_path, self.module_name, "filters.py")

        with open(filter_path, 'a') as f:
            content = '\n\n' + filter_template
            f.write(content)

    def gen_code(self):
        self._write_urls()
        self._write_viewset()
        self._write_serializer()
        self._write_filter()

if __name__ == "__main__":
    module_name = sys.argv[1]
    name = sys.argv[2]
    verbose_name = sys.argv[3]

    gen = CodeGenerator(module_name, name, verbose_name)
    gen.gen_code()
