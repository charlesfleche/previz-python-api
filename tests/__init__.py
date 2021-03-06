try:
    from StringIO import StringIO # python 2
except ImportError:
    from io import StringIO # python 3
import responses
import unittest

from previz import *

class TestPrevizProject(unittest.TestCase):
    def setUp(self):
        self.p = PrevizProject('https://example.com/api',
                               'TOKEN',
                               '94071d22-3fd6-47bc-9e5b-b3b9f234c3f5')

    def test_url(self):
        self.assertEqual(self.p.url('project',
                                    root='http://previz.app/api',
                                    project_id='d899cd46-a94d-4b51-b9ce-eb6569df9c8b'),
                         'http://previz.app/api/projects/d899cd46-a94d-4b51-b9ce-eb6569df9c8b')

        self.assertEqual(self.p.url('projects'),
                         'https://example.com/api/projects')
        self.assertEqual(self.p.url('project'),
                         'https://example.com/api/projects/94071d22-3fd6-47bc-9e5b-b3b9f234c3f5')
        self.assertEqual(self.p.url('scene',
                                    scene_id='a71fc256-68a6-11e7-8716-3b6dc9964f94'),
                         'https://example.com/api/scenes/a71fc256-68a6-11e7-8716-3b6dc9964f94')
        self.assertEqual(self.p.url('assets'),
                         'https://example.com/api/projects/94071d22-3fd6-47bc-9e5b-b3b9f234c3f5/assets')
        self.assertEqual(self.p.url('asset',
                                    asset_id='ee35122e-65ba-4c56-8280-39653a32bf09'),
                         'https://example.com/api/projects/94071d22-3fd6-47bc-9e5b-b3b9f234c3f5/assets/ee35122e-65ba-4c56-8280-39653a32bf09')
        self.assertEqual(self.p.url('state'),
                         'https://example.com/api/projects/94071d22-3fd6-47bc-9e5b-b3b9f234c3f5/state')

    def test_url_elems(self):
        self.assertEqual(self.p.url_elems,
                         {
                             'root': 'https://example.com/api',
                             'project_id': '94071d22-3fd6-47bc-9e5b-b3b9f234c3f5'
                         })

    def test_common_headers(self):
        self.assertEqual(self.p.common_headers,
                         {
                             'Accept': 'application/vnd.previz.v2+json',
                             'Authorization': 'Bearer TOKEN'
                         })

    def test_custom_headers(self):
        self.assertEqual(self.p.custom_headers, {})

    def test_set_custom_headers(self):
        self.p.custom_headers = {'Greeting': 'Hello World'}
        self.assertEqual(self.p.custom_headers, {'Greeting': 'Hello World'})

    @responses.activate
    def test_request_headers(self):
        # Set the custom headers.
        self.p.custom_headers = {'x-test-header': 'this is a test'}

        # Mock the response.
        responses.add(responses.GET,
                      'https://example.com/api/plugins',
                      json={'data': []},
                      status=200)

        self.p.plugins()

        # Check the request headers.
        headers = responses.calls[0].request.headers

        self.assertTrue(('Accept', 'application/vnd.previz.v2+json'), headers.items())
        self.assertTrue(('Authorization', 'Bearer TOKEN'), headers.items())
        self.assertTrue(('x-test-header', 'this is a test'), headers.items())


class TestUtils(unittest.TestCase):
    def test_flat_list(self):
        l = [
            [
                [1, 2, 3],
                [range(4, 6+1), range(7, 9+1)]
            ],
            [
                {
                    (10, 11, 12): 'dummy',
                    13: 'dummy'
                }
            ]
        ]
        self.assertListEqual(flat_list(l),
                             [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])

    def test_UuidBuilder(self):
        b = UuidBuilder()
        self.assertEqual(b('SomeString'), b('SomeString'))
        self.assertEqual(b('SomeString'), b('SomeString').upper())
        self.assertNotEqual(b(), b())

    def test_walk_data(self):
        d = {
            'data': {'id': 1}
        }
        self.assertEqual(walk_data(d), {'id': 1})

        d = {
            'data': [
                {
                    'data': {'id': 0,
                             'vals': ['a', {'b': 'c'}]},
                    'links': []
                },
                {
                    'data': {
                        'id': 1,
                        'sub': [
                            {'data': {'id': 2}},
                            {'data': {'id': 3,
                                      'vals': ['d', {'e': 'f'}]}}
                        ]
                    },
                    'links': []
                },
                {
                    'data': {
                        'id': 4,
                        'sub': {'data': {'id': 5}}
                    },
                    'links': []
                }
            ],
            'pagination': {}
        }
        self.assertListEqual(walk_data(d),
                             [
                                 {'id': 0,
                                  'vals': [
                                      'a',
                                      {'b': 'c'}
                                  ]
                                 },
                                 {'id': 1,
                                  'sub': [
                                      {'id': 2},
                                      {'id': 3,
                                       'vals': [
                                           'd',
                                           {'e': 'f'}
                                        ]
                                      }
                                  ]
                                 },
                                 {'id': 4,
                                  'sub': {'id': 5}
                                 }
                             ])

    def test_to_param(self):
        self.assertEqual(to_param('key', 0), {'key': 0})
        self.assertEqual(to_param('key', 'a'), {'key': 'a'})
        self.assertEqual(to_param('key', []), {})
        self.assertEqual(to_param('key', ['a', 'b']), {'key': 'a,b'})
        self.assertEqual(to_param('key', [0, 1]), {'key': '0,1'})

    def test_to_params(self):
        self.assertEqual(
            to_params({
                'a': 0,
                'b': 'a',
                'c': [],
                'd': ['a', 'b'],
                'e': 'a,b'
            }),
            {
                'a': 0,
                'b': 'a',
                'd': 'a,b',
                'e': 'a,b'
            }
        )

    def test_get_updated_version(self):
        d = {
            "blender": {
                "current_version": "0.0.8",
                "description": "Create Previz projects and export meshes, UV sets and images directly from Blender",
                "downloadUrl": "http://previz.app/downloads/plugins/previz-blender-current_version.zip",
                "handle": "blender",
                "icon": "http://previz.app/img/third-party-logos/addons_c4d.png",
                "id": "c25da42b-99b4-4b87-a702-50ca6f1c4ef7",
                "title": "Blender",
                "versions": {
                    "0.0.8": {
                        "downloadUrl": "http://previz.app/downloads/plugins/previz-blender-0.0.8.zip",
                        "id": "37cb1fa5-f5e3-43cd-8e1c-5bae36e42c43",
                        "released_at": "2017-07-20T09:00:00+00:00"
                    }
                }
            },
            "cinema4d": {
                "current_version": "0.0.12",
                "description": "Create Previz projects and export meshes, UV sets and images directly from Cinema4D.",
                "downloadUrl": "http://previz.app/downloads/plugins/previz-cinema4d-current_version.zip",
                "handle": "cinema4d",
                "icon": "http://previz.app/img/third-party-logos/addons_blender.png",
                "id": "af0d0f86-dd06-4656-828b-ec07b8b89fd6",
                "title": "Cinema4D",
                "versions": {
                    "0.0.12": {
                        "downloadUrl": "http://previz.app/downloads/plugins/previz-cinema4d-0.0.12.zip",
                        "id": "7df96df3-3f35-4e6c-9d40-7a42e68ca60c",
                        "released_at": "2017-07-20T09:00:00+00:00"
                    }
                }
            }
        }
        self.assertIsNone(get_updated_version(d, 'blender', '0.0.8'))
        self.assertEqual(get_updated_version(d, 'cinema4d', '0.0.11')['version'], '0.0.12')

    def test_normalize_api_root(self):
        should_be = 'https://example.com/api'
        token = 'XXX'

        p = PrevizProject('https://example.com/api', token)
        self.assertEqual(p.root, should_be)

        p = PrevizProject('https://example.com/api/', token)
        self.assertEqual(p.root, should_be)


class TestExport(unittest.TestCase):
    def setUp(self):
        self.mesh = Mesh('MyMesh',
                         'MyMeshGeometry',
                         [[0, 1, 2], [4, 5], [6]],                           # world_matrix, no special meaning
                         [[7, [8, 9, 10], [[11, 12, 13], [14, 15, 16]]]],    # faces,        no special meaning
                         [[17, 18], [19, 20]],                               # vertices,     no special meaning
                         [UVSet('uvsA', [21, 22]), UVSet('uvsB', range(23, 25))]) # uvsets,       no special meaning

        self.scene = Scene('MyGenerator',
                           '/path/to/my/source/file.json',
                           14423100, # SVG crimson #DC143C
                           [self.mesh])

        self.built_metadata = {
            'version': 4.4,
            'type': 'Object',
            'generator': 'MyGenerator',
            'sourceFile': '/path/to/my/source/file.json'
        }

        self.built_geometry = {
            'data': {
                'metadata': {
                    'version': 3,
                    'generator': 'MyGenerator',
                },
                'name': 'MyMeshGeometry',
                'faces': [7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
                'uvs': [[21, 22], [23, 24]],
                'vertices': [17, 18, 19, 20]
            },
            'uuid': '43A33449-0B05-4A9F-B05A-8B880646F6B4',
            'type': 'Geometry'
        }

        self.built_user_data = {
            'previz': {
                'uvsetNames': ['uvsA', 'uvsB']
            }
        }

        self.built_object = {
            'name': 'MyMesh',
            'uuid': '748A9554-7CC1-4F4E-BF23-D70D3E5DFF44',
            'matrix': [0, 1, 2, 4, 5, 6],
            'visible': True,
            'type': 'Mesh',
            'geometry': self.built_geometry['uuid'],
            'userData': self.built_user_data
        }

        self.built_scene_root = {
            'type': 'Scene',
            'matrix': [
                1.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1.0
            ],
            'uuid': '01C4BFA0-2524-4EC8-943C-9F2E5C37925B',
            'children': [self.built_object],
            'background': 14423100
        }

        self.built_scene = {
            'animations': [],
            'geometries': [self.built_geometry],
            'images': [],
            'materials': [],
            'metadata': self.built_metadata,
            'object': self.built_scene_root,
            'textures': []
        }

    def reset_uuid(self, d, new_uuid):
        uuid.UUID(d['uuid']) # Test if uuid is valid
        d['uuid'] = new_uuid

    def test_build_metadata(self):
        self.assertEqual(build_metadata(self.scene), self.built_metadata)

    def test_build_scene_root(self):
        root = build_scene_root(self.scene, [self.built_object])
        self.reset_uuid(root, self.built_scene_root['uuid'])
        self.assertEqual(root, self.built_scene_root)

    def test_build_geometry(self):
        g = build_geometry(self.scene, self.mesh)
        self.reset_uuid(g, self.built_geometry['uuid'])
        self.assertEqual(g, self.built_geometry)

    def test_build_user_data(self):
        self.assertEqual(build_user_data(self.mesh), self.built_user_data)

    def test_build_object(self):
        o = build_object(self.mesh, self.built_geometry['uuid'])
        self.reset_uuid(o, self.built_object['uuid'])
        self.assertEqual(o, self.built_object)

    def fix_uuids(self, scene_root, geometries):
        self.reset_uuid(scene_root, self.built_scene_root['uuid'])
        self.reset_uuid(scene_root['children'][0], self.built_object['uuid'])
        scene_root['children'][0]['geometry'] = self.built_geometry['uuid']

        self.reset_uuid(geometries[0], self.built_geometry['uuid'])

    def test_build_objects(self):
        scene_root, geometries = build_objects(self.scene)
        self.fix_uuids(scene_root, geometries)
        self.assertEqual(scene_root, self.built_scene_root)
        self.assertEqual(geometries, [self.built_geometry])

    def test_build_three_js_scene(self):
        scene = build_three_js_scene(self.scene)
        self.fix_uuids(scene['object'], scene['geometries'])
        self.assertEqual(scene, self.built_scene)

    def test_export(self):
        fp = StringIO()
        export(self.scene, fp)
        scene_from_json = json.loads(fp.getvalue())
        self.fix_uuids(scene_from_json['object'],
                       scene_from_json['geometries'])
        self.assertEqual(scene_from_json, self.built_scene)
