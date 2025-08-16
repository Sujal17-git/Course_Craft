from django import template

register = template.Library()

@register.filter
def total_assignments(sections):
    return sum(section.assignments.count() for section in sections)