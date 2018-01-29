from django.conf import settings # import the settings file

def custom_context_processor(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'LAS_URL': settings.LAS_URL}
