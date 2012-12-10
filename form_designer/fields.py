from django import forms


class DecimalField(forms.DecimalField):
    def to_python(self, value):
        if isinstance(value, basestring):
            value = value.replace(u',', '.')
        return super(DecimalField, self).to_python(value)
