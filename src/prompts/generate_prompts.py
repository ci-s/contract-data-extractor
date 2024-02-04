def partial_format(template, **kwargs):
    for key, value in kwargs.items():
        template = template.replace("{" + key + "}", str(value))
    return template
