from django import template
register = template.Library()

@register.filter(name='add_attr')
def add_attr(field, css):
    attr, value = css.split(':')
    return field.as_widget(attrs={attr: value})