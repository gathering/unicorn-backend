from django import forms

#
# Forms
#


class BootstrapMixin(forms.BaseForm):
    def __init__(self, *args, **kwargs):
        super(BootstrapMixin, self).__init__(*args, **kwargs)

        exempt_widgets = [
            forms.CheckboxInput,
            forms.ClearableFileInput,
            forms.FileInput,
            forms.RadioSelect,
        ]

        for field_name, field in self.fields.items():
            if field.widget.__class__ not in exempt_widgets:
                css = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = " ".join([css, "form-control"]).strip()

                if "placeholder" not in field.widget.attrs:
                    field.widget.attrs["placeholder"] = field.label

            if field.required and not isinstance(field.widget, forms.FileInput):
                field.widget.attrs["required"] = "required"
