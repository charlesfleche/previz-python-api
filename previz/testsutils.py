import functools

from . import PrevizProject

class Decorators(object):
    def __init__(self, api_token, api_root, new_project_prefix = 'cf-'):
        self.api_root = api_root
        self.api_token = api_token
        self.new_project_prefix = new_project_prefix

    def project(self, project_id):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                p = PrevizProject(self.api_root, self.api_token, project_id)
                project = p.project(include=['scenes'])
                func(project=project, *args, **kwargs)
            return wrapper
        return decorator

    def tempproject(self):
        '''Returning an existing project while the API v2 is being worked on'''
        return self.project('8d9e684f-0763-4756-844b-d0219a4f3f9a')

    def scene(self, scene_id):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                project_id = kwargs['project']['id']
                p = PrevizProject(self.api_root, self.api_token, project_id)
                scene = p.scene(scene_id, include=[])
                func(scene=scene, *args, **kwargs)
                #p = PrevizProject(self.api_root, self.api_token, project_id)
                #func(project=p.project(include=['scenes']), *args, **kwargs)
            return wrapper
        return decorator

    def tempscene(self):
        '''Returning an existing scene while the API v2 is being worked on'''
        return self.scene('5a56a895-46ef-4f0f-862c-38ce14f6275b')


def tempproject(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        api_root = os.environ[PREVIZ_API_ROOT_ENVVAR]
        api_token = os.environ[PREVIZ_API_TOKEN_ENVVAR]
        project_name = 'cf-' + func.__qualname__

        p = PrevizProject(api_root, api_token)
        #p.project_id = p.new_project(project_name)['id']
        p.project_id = 'a5ff9cef-4904-4dc3-8a3c-821a219c891e' # p.project_id

        func(project_id=p.project_id, *args, **kwargs)

        #p.delete_project()
    return wrapper

def tempscene(func):
    pass
