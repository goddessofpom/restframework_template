import sys
import re
from os import path
import os
from django.db import models
import zipfile
import json


class CodeGenerator(object):
    def __init__(self, module_name="", name="", model=None):
        self.module_name = module_name
        self.name = name.capitalize()
        self.model = model
        self.parent_path = path.dirname(path.dirname(__file__))
        self.exclude_models = [
            "LogEntry", "Permission", "Group", "ContentType", "Session"
        ]

    def _find_pos(self, target, content):
        tab=re.search(target, content)
        pos=tab.start()
        return pos

    def set_module_name(self, module_name):
        self.module_name = module_name
    
    def set_name(self, name):
        self.name = name

    def set_model(self, model):
        self.model = model
    
    @property
    def _lower_name(self):
        lst = []
        for index, char in enumerate(self.name):
            if char.isupper() and index != 0:
                lst.append("_")
            lst.append(char)

        return "".join(lst).lower()

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

    def init_files(self, path):
        urls = os.path.join(path, "urls.py")
        viewsets = os.path.join(path, "viewsets.py")
        serializers = os.path.join(path, "serializers.py")
        filters = os.path.join(path, "filters.py")
        if os.path.exists(urls):
            os.remove(urls)
        if os.path.exists(viewsets):
            os.remove(viewsets)
        if os.path.exists(serializers):
            os.remove(serializers)
        if os.path.exists(filters):
            os.remove(filters)

        open(urls, 'w').close()
        open(viewsets, 'w').close()
        open(serializers, 'w').close()
        open(filters, 'w').close()

    def _write_urls(self, insert=True):
        url_template = self.url_template
        url_path = path.join(self.parent_path, self.module_name, "urls.py")
        if insert:
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
        else:
            with open(url_path, 'a') as f:
                content = '\n\n' + url_template
                f.write(content)

    def _get_field_type_string(self, field):
        if isinstance(field, models.SmallIntegerField) or\
            isinstance(field, models.PositiveIntegerField) or\
            isinstance(field, models.IntegerField) or\
            isinstance(field, models.ForeignKey) or\
            isinstance(field, models.AutoField) or\
            isinstance(field, models.PositiveSmallIntegerField):
            return f"{{Number}}"
        elif isinstance(field, models.CharField) or\
            isinstance(field, models.TextField) or\
            isinstance(field, models.DateField) or\
            isinstance(field, models.DateTimeField):
            return f"{{String}}"
        elif isinstance(field, models.BooleanField):
            return f"{{Boolean}}"
        else:
            return f"{{Object}}"

    def _get_choice_desc(self, field):
        if len(field.choices) > 0:
            desc = ""
            for choice in field.choices:
                num = choice[0]
                num_text = choice[1]
                desc = desc + f"{num}{num_text} "
            return desc
        return ""

    def _get_doc_template(self):
        m = self.model
        lower = self._lower_name
        list_template = f"""\n\n\"\"\"
    @api {{get}} /{self.module_name}/{lower} {m._meta.verbose_name}列表
    @apiVersion 1.0.0
    @apiGroup {self.module_name}
    @apiName {m._meta.verbose_name}列表({m.__name__}List)\n
        """

        create_template = f"""\n\n\"\"\"
    @api {{post}} /{self.module_name}/{lower} 创建{m._meta.verbose_name}
    @apiVersion 1.0.0
    @apiGroup {self.module_name}
    @apiName 创建{m._meta.verbose_name}(create{m.__name__})\n
        """

        for field in m._meta.fields:
            field_type_string = self._get_field_type_string(field)
            api_name = field.name
            field_desc = field.verbose_name
            optional_name = f"[{field.name}]" if field.null else field.name
            choices_text = self._get_choice_desc(field)
            result_line = f"@apiSuccess {field_type_string} {api_name} {field_desc} {choices_text}\n"
            list_template = list_template + result_line
            param_line = f"@apiParam {field_type_string} {optional_name} {field_desc} {choices_text}\n"
            create_template = create_template + param_line
        
        list_template = list_template + "\n\"\"\""
        create_template = create_template + "\n\"\"\""

        hold_template = list_template + "\n\n" + create_template
        return hold_template

    def _write_viewset(self):
        viewset_template = self.viewset_template
        viewset_path = path.join(self.parent_path, self.module_name, "viewsets.py")

        with open(viewset_path, 'a') as f:
            if self.model:
                doc = self._get_doc_template()
                content = '\n\n' + viewset_template + '\n\n' + doc
            else:
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

    def write_file_header(self, configs):
        for config in configs:
            filter_header = "from django_filters.rest_framework import FilterSet"
            serializer_header = "from rest_framework.serializers import ModelSerializer"
            viewset_header = "from restframework_core.viewsets import CustomModelViewSet"
            url_header = "from django.conf.urls import url, re_path, include\n\nfrom rest_framework.routers import DefaultRouter"

            filter_path = path.join(self.parent_path, config.name, "filters.py")
            serializer_path = path.join(self.parent_path, config.name, "serializers.py")
            viewset_path = path.join(self.parent_path, config.name, "viewsets.py")
            url_path = path.join(self.parent_path, config.name, "urls.py")

            models = config.get_models()

            mark = 0
            import_serializer_string = ""
            import_filter_string = ""
            import_model_string = ""
            for m in models:
                if m.__name__ in self.exclude_models:
                    continue
                try:
                    if mark == 0:
                        filter_header = filter_header + f"\n\nfrom .models import {m.__name__}"
                        serializer_header = serializer_header + f"\n\nfrom .models import {m.__name__}"
                        import_serializer_string = import_serializer_string + f"\n\nfrom .serializers import {m.__name__}Serializer"
                        import_filter_string = import_filter_string + f"\n\nfrom .filters import {m.__name__}Filter"
                        import_model_string = import_model_string + f"\n\nfrom .models import {m.__name__}"
                        url_header = url_header + f"\n\nfrom .viewsets import {m.__name__}ViewSet"
                        mark = 1
                    else:
                        filter_header = filter_header + f", {m.__name__}"
                        serializer_header = serializer_header + f", {m.__name__}"
                        import_serializer_string = import_serializer_string + f", {m.__name__}Serializer"
                        import_filter_string = import_filter_string + f", {m.__name__}Filter"
                        import_model_string = import_model_string + f", {m.__name__}"
                        url_header = url_header + f", {m.__name__}ViewSet"
                except:
                    raise Exception("error happen!")
            
            viewset_header = viewset_header + import_model_string + import_serializer_string + import_filter_string
            with open(viewset_path, 'a') as f:
                f.write(viewset_header)
            
            with open(serializer_path, 'a') as f:
                f.write(serializer_header)
            
            with open(filter_path, 'a') as f:
                f.write(filter_header)

            url_header = url_header + "\n\n\n\nrouter = DefaultRouter()\n\nrouter.trailing_slash = '[/]?'\n\nurlpatterns = [\n\n    url('', include(router.urls)),\n\n]\n\n"
            with open(url_path, 'a') as f:
                f.write(url_header)


    def gen_code(self):
        self._write_urls()
        self._write_viewset()
        self._write_serializer()
        self._write_filter()

    def batch_gen_code(self, configs):
        for config in configs:
            models = config.get_models()
            for m in models:
                if m.__name__ in self.exclude_models:
                    continue
                else:
                    self.set_module_name(config.name)
                    self.set_name(m.__name__)
                    self.set_model(m)
                    self.gen_code()



class JsonGenerator(object):
    def __init__(self):
        self.base_path = os.getcwd()
        self.file_list = []
        self.exclude_models = [
            "LogEntry", "Permission", "Group", "ContentType", "Session"
        ]

    def _get_type_data(self, field):
        if isinstance(field, models.SmallIntegerField) or\
            isinstance(field, models.PositiveIntegerField) or\
            isinstance(field, models.IntegerField) or\
            isinstance(field, models.ForeignKey) or\
            isinstance(field, models.AutoField) or\
            isinstance(field, models.PositiveSmallIntegerField):
            return "number"
        elif isinstance(field, models.CharField) or\
            isinstance(field, models.TextField):
            return "string"
        elif isinstance(field, models.BooleanField):
            return "boolean"
        elif isinstance(field, models.DateField) or\
            isinstance(field, models.DateTimeField):
            return "date"
        else:
            return "string"

    def _get_choices_data(self, field):
        if len(field.choices) > 0:
            enum = []
            for choice in field.choices:
                data = {"label": choice[1], "value": choice[0]}
                enum.append(data)
            return enum
        return None

    def gen_model_json(self, model):
        file_name = f"{model.__name__}.json"
        full_path = os.path.join(self.base_path, file_name)

        properties = {}
        for field in model._meta.fields:
            if field.name == "id" or field.name == "deleted" or field.name == "updated":
                continue
            field_data = {
                "title": str(field.verbose_name),
                "required": "false" if field.null else "true",
            }

            choice_data = self._get_choices_data(field)
            if choice_data:
                field_data["enum"] = choice_data

            field_type = self._get_type_data(field)
            field_data["type"] = field_type

            field_name = field.name

            properties[field_name] = field_data
        
        data = {"type": "object", "properties": properties}

        with open(full_path, "w") as f:
            json.dump(data, f, ensure_ascii=False)

        self.file_list.append(full_path)

    def batch_gen_json(self, configs):
        for config in configs:
            models = config.get_models()
            for m in models:
                if m.__name__ in self.exclude_models:
                    continue
                else:
                    self.gen_model_json(m)

        self._get_zip()

    def _get_zip(self, zip_name="json_data.zip"):
        zp=zipfile.ZipFile(zip_name,'w')
        for f in self.file_list:
            zp.write(f)
        zp.close()

        for f in self.file_list:
            os.remove(f)



if __name__ == "__main__":
    module_name = sys.argv[1]
    name = sys.argv[2]

    gen = CodeGenerator(module_name, name)
    gen.gen_code()
